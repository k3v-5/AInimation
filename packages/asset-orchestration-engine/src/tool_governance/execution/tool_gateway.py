import uuid
from typing import Dict, Any, Optional, List
from ..core.governance_status import PermissionType, ActionLifecycle, ToolRisk
from ..core.governance_schema import (
    ActionProposal, ExecutionBudget, NormalizedToolResult, StateSnapshot, ExecutionReport
)
from ..core.permission_manager import PermissionManager
from ..validation.action_validator import ActionValidator
from ..validation.duplicate_detector import DuplicateActionDetector, ExecutionLoopGuard
from .post_verifier import PostActionValidator, RollbackManager
from ...correction_execution.providers.blender_provider import IBlenderProvider
from ...correction_execution.providers.mock_blender_provider import MockBlenderProvider
from ...intent_compiler.core.intent_schema import BuildSpecification

class AIToolGateway:
    """
    AI Tool Gateway & Execution Policy Engine (AOE v22)
    
    Regla Fundamental:
    LA IA NUNCA TIENE ACCESO DIRECTO AL MCP.
    TODA ACCIÓN PASA POR:
    PERMISOS -> POLÍTICA -> LÍMITES DE PARÁMETROS -> ANTI-DUPLICADOS -> ANTI-BUCLES -> PRESUPUESTO -> EJECUCIÓN -> POST-VERIFICACIÓN.
    """
    def __init__(self, provider: Optional[IBlenderProvider] = None):
        self.provider = provider or MockBlenderProvider()
        self.permission_mgr = PermissionManager()
        self.budget = ExecutionBudget()
        self.dup_detector = DuplicateActionDetector()
        self.loop_guard = ExecutionLoopGuard()
        self.logs: List[str] = []

    def submit_proposal(
        self,
        agent_id: str,
        proposal: ActionProposal,
        spec: Optional[BuildSpecification] = None,
        simulate_blender_state_failure: bool = False
    ) -> NormalizedToolResult:
        call_id = f"call_{uuid.uuid4().hex[:6]}"

        # 1. Comprobar Presupuesto
        if not self.budget.can_consume_tool_call():
            msg = "BUDGET_EXCEEDED: Maximum tool calls exceeded."
            self.logs.append(msg)
            return NormalizedToolResult(call_id, ActionLifecycle.REJECTED, proposal.target_entity, {}, False, msg)

        if proposal.action_name == "rebuild_asset" and not self.budget.can_consume_rebuild():
            msg = "BUDGET_EXCEEDED: Maximum asset rebuilds exceeded."
            self.logs.append(msg)
            return NormalizedToolResult(call_id, ActionLifecycle.REJECTED, proposal.target_entity, {}, False, msg)

        # 2. Comprobar Operaciones Destructivas de Alto Riesgo
        if proposal.action_name == "delete_asset":
            msg = "PENDING_APPROVAL: Destructive operation DELETE_ASSET requires explicit human authorization."
            self.logs.append(msg)
            return NormalizedToolResult(call_id, ActionLifecycle.REJECTED, proposal.target_entity, {}, False, msg)

        # 3. Comprobar Permisos (Least Privilege)
        req_perm = PermissionType.MODIFY_ASSET
        if proposal.action_name == "rebuild_asset":
            req_perm = PermissionType.REBUILD_ASSET

        if not self.permission_mgr.is_authorized(agent_id, req_perm):
            msg = f"PERMISSION_DENIED: Agent '{agent_id}' does not have permission '{req_perm.value}'."
            self.logs.append(msg)
            return NormalizedToolResult(call_id, ActionLifecycle.REJECTED, proposal.target_entity, {}, False, msg)

        # 4. Validar Límites de Parámetros y Restricciones
        is_val, val_msg = ActionValidator.validate_proposal(proposal, spec)
        if not is_val:
            self.logs.append(val_msg)
            return NormalizedToolResult(call_id, ActionLifecycle.REJECTED, proposal.target_entity, {}, False, val_msg)

        # 5. Comprobar Duplicados y Bucles
        fp = DuplicateActionDetector.compute_fingerprint(proposal)
        is_dup, dup_msg = self.dup_detector.check_duplicate(proposal)
        if is_dup:
            self.logs.append(dup_msg)
            return NormalizedToolResult(call_id, ActionLifecycle.REJECTED, proposal.target_entity, {}, False, dup_msg)

        is_loop, loop_msg = self.loop_guard.record_and_check_loop(fp)
        if is_loop:
            self.logs.append(loop_msg)
            return NormalizedToolResult(call_id, ActionLifecycle.REJECTED, proposal.target_entity, {}, False, loop_msg)

        # 6. Snapshot Previo para Rollback Transaccional
        snapshot = RollbackManager.take_snapshot(f"snap_{call_id}", self.provider)

        # 7. Consumir Presupuesto y Ejecutar
        self.budget.consume_tool_call()
        if proposal.action_name == "rebuild_asset":
            self.budget.consume_rebuild()

        # Ejecución en Provider
        if proposal.target_entity not in self.provider.assets:
            self.provider.assets[proposal.target_entity] = {"dimensions": (4.0, 4.0, 2.0)}

        if not simulate_blender_state_failure:
            if "roof_height" in proposal.parameters:
                # Simular modificación exitosa en dimensiones
                self.provider.assets[proposal.target_entity]["dimensions"] = (4.0, 4.0, proposal.parameters["roof_height"])

        # 8. Post-Verificación
        is_ver, ver_msg = PostActionValidator.verify_parameter_state(
            self.provider, proposal.target_entity, proposal.parameters
        )
        if not is_ver:
            # Fallo de verificación -> Rollback inmediato
            RollbackManager.restore_snapshot(snapshot, self.provider)
            self.logs.append(f"{ver_msg} -> Rolled back to snapshot '{snapshot.snapshot_id}'.")
            return NormalizedToolResult(call_id, ActionLifecycle.ROLLED_BACK, proposal.target_entity, {}, False, ver_msg)

        msg_success = f"Action '{proposal.action_name}' executed and verified on '{proposal.target_entity}'."
        self.logs.append(msg_success)
        return NormalizedToolResult(
            tool_call_id=call_id,
            status=ActionLifecycle.COMMITTED,
            target_entity=proposal.target_entity,
            modified_parameters=proposal.parameters,
            verification_passed=True,
            message=msg_success
        )
