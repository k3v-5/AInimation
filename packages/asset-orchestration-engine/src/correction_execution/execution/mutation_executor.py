import time
import uuid
from typing import Dict, Any, Optional, List, Tuple
from ..core.correction_plan import CorrectionPlan, CorrectionOperation, OperationType
from ..core.object_registry import ComponentRegistry
from ..core.operation_registry import OperationRegistry
from ..risk.risk_analyzer import RiskAnalyzer, RiskLevel
from ..risk.permission_manager import OperationPermissionManager, ExecutionMode
from ..transactions.snapshot_manager import SnapshotManager, AssetSnapshot
from ..transactions.mutation_transaction import MutationTransaction, TransactionState
from ..providers.blender_provider import IBlenderProvider
from .dependency_resolver import DependencyResolver
from .mutation_validator import MutationValidator

class MutationExecutor:
    def __init__(
        self,
        provider: IBlenderProvider,
        component_registry: ComponentRegistry,
        execution_mode: ExecutionMode = ExecutionMode.BALANCED,
        max_retries: int = 2
    ):
        self.provider = provider
        self.registry = component_registry
        self.mode = execution_mode
        self.max_retries = max_retries
        self.snapshot_manager = SnapshotManager()
        self.operation_history: List[Dict[str, Any]] = []

    def execute_plan(
        self,
        plan: CorrectionPlan,
        protected_components: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        tx_id = f"tx_{uuid.uuid4().hex[:6]}"
        tx = MutationTransaction(transaction_id=tx_id, plan_id=plan.plan_id, asset_id=plan.asset_id)

        # 1. Resolver orden de operaciones
        ok_order, sorted_ops, err_order = DependencyResolver.resolve_order(plan.operations)
        if not ok_order:
            tx.state = TransactionState.FAILED
            return {"success": False, "status": "FAILED", "error_code": "INVALID_CORRECTION_PLAN", "message": err_order}

        # 2. Detección de Oscilaciones / Anti-Loop
        if len(self.operation_history) >= 3:
            last_3 = [h.get("operation_type") for h in self.operation_history[-3:]]
            if last_3 == ["SCALE_OBJECT", "SCALE_OBJECT", "SCALE_OBJECT"]:
                return {"success": False, "status": "STOP", "error_code": "OSCILLATION_DETECTED", "message": "Repeated oscillating mutations detected. Stopping execution."}

        # 3. Dry Run Check
        if dry_run:
            return {
                "success": True,
                "status": "dry_run",
                "plan_id": plan.plan_id,
                "asset_id": plan.asset_id,
                "operations_count": len(sorted_ops),
                "risk_level": plan.risk_level,
                "execution_mode": self.mode.value
            }

        # 4. Crear Snapshot inicial
        cur_state = self.provider.get_asset_state(plan.asset_id)
        snapshot = self.snapshot_manager.create_snapshot(plan.asset_id, plan.plan_id, cur_state)
        tx.snapshot = snapshot
        tx.state = TransactionState.SNAPSHOTTED

        # 5. Ejecutar operaciones
        executed_ops: List[str] = []
        is_all_noop = True

        for op in sorted_ops:
            # A. Validar permisos de riesgo
            risk = RiskAnalyzer.analyze_risk(op.operation_type, op.parameters)
            if not OperationPermissionManager.is_permitted(risk, self.mode):
                self._rollback(plan.asset_id, snapshot, tx)
                return {"success": False, "status": "DENIED", "error_code": "OPERATION_NOT_PERMITTED", "message": f"Operation '{op.operation_type.value}' of risk '{risk.value}' is not permitted in {self.mode.value} mode."}

            # B. Validar precondiciones y componentes protegidos
            ok_pre, err_pre = MutationValidator.validate_preconditions(op, self.registry, protected_components)
            if not ok_pre:
                self._rollback(plan.asset_id, snapshot, tx)
                return {"success": False, "status": "DENIED", "error_code": "PRECONDITION_FAILED", "message": err_pre}

            # C. Ejecutar con política de reintentos y captura de timeout
            op_success = False
            attempts = 0
            while attempts <= self.max_retries and not op_success:
                attempts += 1
                try:
                    op_res, was_noop = self._execute_single_op(plan.asset_id, op)
                    if not was_noop:
                        is_all_noop = False
                    op_success = op_res
                except TimeoutError:
                    tx.state = TransactionState.UNKNOWN
                    return {"success": False, "status": "UNKNOWN", "error_code": "PROVIDER_TIMEOUT", "message": "Blender MCP timed out during mutation. State is UNKNOWN and requires reconciliation."}
                except ConnectionResetError:
                    if attempts > self.max_retries:
                        self._rollback(plan.asset_id, snapshot, tx)
                        return {"success": False, "status": "FAILED", "error_code": "MCP_CONNECTION_FAILED", "message": "Transient connection error exceeded retry limit."}
                    time.sleep(0.01) # Backoff breve
                except Exception as e:
                    self._rollback(plan.asset_id, snapshot, tx)
                    return {"success": False, "status": "FAILED", "error_code": "EXECUTION_ERROR", "message": str(e)}

            if not op_success:
                self._rollback(plan.asset_id, snapshot, tx)
                return {"success": False, "status": "ROLLED_BACK", "error_code": "OPERATION_FAILED", "failed_operation": op.operation_id}

            executed_ops.append(op.operation_id)
            self.operation_history.append({"operation_id": op.operation_id, "operation_type": op.operation_type.value, "target": op.target})

        # D. Postcondición / NO_OP check
        if is_all_noop:
            tx.state = TransactionState.COMMITTED
            return {"success": True, "status": "NO_CHANGE_REQUIRED", "message": "Asset already satisfies requested target state."}

        # 6. Commit
        tx.state = TransactionState.COMMITTED
        return {
            "success": True,
            "status": "CORRECTED",
            "transaction_id": tx_id,
            "asset_id": plan.asset_id,
            "executed_operations": executed_ops,
            "snapshot_id": snapshot.snapshot_id
        }

    def _execute_single_op(self, asset_id: str, op: CorrectionOperation) -> Tuple[bool, bool]:
        """Devuelve (success, is_noop)."""
        t = op.operation_type
        params = op.parameters

        if t == OperationType.SET_DIMENSIONS:
            target_dims = params.get("dimensions")
            if not target_dims:
                # Si solo se pasa length/height
                cur = self.provider.get_component_dimensions(asset_id, op.target) or (0.05, 0.05, 0.5)
                l = params.get("length") or params.get("z") or cur[2]
                target_dims = (cur[0], cur[1], float(l))
            
            cur_dims = self.provider.get_component_dimensions(asset_id, op.target)
            if cur_dims == tuple(target_dims):
                return True, True # NO_OP
            
            ok = self.provider.set_component_dimensions(asset_id, op.target, target_dims)
            return ok, False

        elif t == OperationType.SCALE_OBJECT:
            factor = float(params.get("factor", 1.0))
            if factor == 1.0:
                return True, True # NO_OP
            ok = self.provider.scale_component(asset_id, op.target, factor)
            return ok, False

        elif t == OperationType.CHANGE_METALLIC:
            val = float(params.get("value", 0.0))
            cur = self.provider.get_material_property(asset_id, op.target, "metallic")
            if cur == val:
                return True, True # NO_OP
            ok = self.provider.set_material_property(asset_id, op.target, "metallic", val)
            return ok, False

        elif t == OperationType.CHANGE_ROUGHNESS:
            val = float(params.get("value", 0.5))
            cur = self.provider.get_material_property(asset_id, op.target, "roughness")
            if cur == val:
                return True, True # NO_OP
            ok = self.provider.set_material_property(asset_id, op.target, "roughness", val)
            return ok, False

        return True, False

    def _rollback(self, asset_id: str, snapshot: AssetSnapshot, tx: MutationTransaction):
        tx.state = TransactionState.ROLLING_BACK
        self.provider.restore_asset_state(asset_id, snapshot.state_data)
        tx.state = TransactionState.ROLLED_BACK
