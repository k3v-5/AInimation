import time
from typing import Dict, Any, List, Set, Optional
from ..core.gateway_types import (
    CommandType, RiskLevel, GatewayState, ExecutionStatus
)
from ..core.gateway_schema import (
    GatewayCommand, CommandPlan, GatewayPolicy, ExecutionResult,
    TransactionRecord, SceneStateSnapshot
)
from ..registry.command_registry import CommandRegistry, CapabilityManager
from ..state.scene_state_tracker import SceneStateTracker, LockController
from ..transactions.transaction_manager import TransactionManager, ResultVerifier
from ..scheduler.dependency_scheduler import DependencyScheduler, ExecutionLoopGuard
from ..adapter.mock_mcp_adapter import MockMCPAdapter

class ExecutionGateway:
    def __init__(self, policy: Optional[GatewayPolicy] = None, mcp_adapter: Optional[MockMCPAdapter] = None):
        self.policy = policy or GatewayPolicy()
        self.adapter = mcp_adapter or MockMCPAdapter()
        self.cap_manager = CapabilityManager()
        self.state_tracker = SceneStateTracker()
        self.lock_controller = LockController()
        self.tx_manager = TransactionManager()
        self.loop_guard = ExecutionLoopGuard(self.policy.max_same_command_retries)
        self.idempotency_cache: Dict[str, ExecutionResult] = {}
        self.state = GatewayState.IDLE
        self.emergency_stopped = False

    def plan_commands(self, commands: List[GatewayCommand]) -> CommandPlan:
        for cmd in commands:
            CommandRegistry.validate_command_policy(cmd)
        return DependencyScheduler.create_plan(commands, self.policy)

    def execute_command(self, cmd: GatewayCommand) -> ExecutionResult:
        if self.emergency_stopped:
            return ExecutionResult(
                execution_id="EXEC_STOPPED",
                command_id=cmd.command_id,
                status=ExecutionStatus.BLOCKED,
                mcp_calls_made=0,
                error="EMERGENCY_STOP: Gateway is in emergency stop state."
            )

        # 1. Validación de Sandboxing y Denylist
        CommandRegistry.validate_command_policy(cmd)

        # 2. Control de Idempotencia
        if cmd.idempotency_key and cmd.idempotency_key in self.idempotency_cache:
            return self.idempotency_cache[cmd.idempotency_key]

        # 3. Control de Concurrencia Optimista
        self.state_tracker.validate_optimistic_concurrency(cmd.expected_scene_version)

        # 4. Loop Guard
        sig = f"{cmd.type.value}_{cmd.target}"
        self.loop_guard.record_attempt(sig)

        # 5. Transacción y Snapshot
        snap_before = self.state_tracker.get_snapshot()
        tx = self.tx_manager.begin_transaction(cmd.operation_id, snap_before)

        # 6. Ejecución a través del Adapter MCP
        self.state = GatewayState.EXECUTING
        res = self.adapter.execute_command(cmd)

        # 7. Manejo de Resultado Desconocido (Timeout)
        if res.status == ExecutionStatus.UNKNOWN_OUTCOME:
            # Inspeccionar estado real en Blender
            actual_objs = self.adapter.inspect_scene_objects()
            if cmd.target in actual_objs:
                # El objeto sí se creó antes del timeout
                res.status = ExecutionStatus.SUCCESS
                res.output = {"created_target": cmd.target, "recovered_from_timeout": True}
                res.error = None

        if res.status != ExecutionStatus.SUCCESS:
            # Rollback
            self.state = GatewayState.ROLLING_BACK
            created_objs = self.tx_manager.rollback(tx.transaction_id)
            for oid in created_objs:
                self.adapter.delete_object(oid)
                self.state_tracker.unregister_object(oid)
            self.state = GatewayState.IDLE
            return res

        # 8. Verificación de Resultado en Blender
        self.state = GatewayState.VERIFYING
        actual_objs = self.adapter.inspect_scene_objects()
        verif = ResultVerifier.verify_objects_exist([cmd.target], actual_objs)
        if not verif.verified:
            # Fallo de verificación -> Rollback
            self.state = GatewayState.ROLLING_BACK
            created_objs = self.tx_manager.rollback(tx.transaction_id)
            for oid in created_objs:
                self.adapter.delete_object(oid)
            self.state = GatewayState.IDLE
            return ExecutionResult(
                execution_id=f"EXEC_{cmd.command_id}",
                command_id=cmd.command_id,
                status=ExecutionStatus.FAILED_VERIFICATION,
                mcp_calls_made=1,
                error=verif.details
            )

        # 9. Commit y Actualización de Estado
        self.tx_manager.track_created_object(tx.transaction_id, cmd.target)
        self.tx_manager.commit(tx.transaction_id)
        self.state_tracker.register_object(cmd.target, cmd.target)
        self.state = GatewayState.IDLE

        if cmd.idempotency_key:
            self.idempotency_cache[cmd.idempotency_key] = res

        return res

    def emergency_stop(self):
        self.emergency_stopped = True
        self.state = GatewayState.EMERGENCY_STOPPED

    def resume_gateway(self):
        self.emergency_stopped = False
        self.state = GatewayState.IDLE
