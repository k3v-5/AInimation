from typing import Dict, Any, List, Set, Optional
from ..core.gateway_types import (
    CommandType, RiskLevel, GatewayState, ExecutionStatus,
    DriftType, ReconciliationMode, GatewayErrorType
)
from ..core.gateway_schema import (
    GatewayCommand, CommandPlan, SceneStateSnapshot, ObjectStateRecord,
    TransactionRecord, VerificationResult, ExecutionResult, GatewayPolicy
)
from ..engine.execution_gateway import ExecutionGateway
from ..adapter.mock_mcp_adapter import MockMCPAdapter, AhujasidMCPAdapter

class MCPGatewayAPI:
    """
    MCP Execution Gateway & Blender State Control API (AOE v42)
    
    Regla Fundamental:
    EL MCP DE BLENDER ES UN PUENTE DE TRANSPORTE CONTROLADO, NO EL LUGAR DE LA LÓGICA.
    TODA OPERACIÓN DEBE PASAR POR EL GATEWAY CON VALIDACIÓN DE ESQUEMA, CONTROL DE
    CONCURRENCIA OPTIMISTA, SANDBOXING, VERIFICACIÓN DE RESULTADOS Y ROLLBACK TRANSACCIONAL.
    """
    def __init__(self, policy: Optional[GatewayPolicy] = None, adapter: Optional[MockMCPAdapter] = None):
        self.gateway = ExecutionGateway(policy=policy, mcp_adapter=adapter)

    def create_command(
        self,
        command_id: str,
        operation_id: str,
        type: CommandType,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        expected_scene_version: Optional[int] = None,
        idempotency_key: Optional[str] = None,
        risk_level: RiskLevel = RiskLevel.LOW
    ) -> GatewayCommand:
        return GatewayCommand(
            command_id=command_id,
            operation_id=operation_id,
            type=type,
            target=target,
            parameters=parameters or {},
            expected_scene_version=expected_scene_version,
            idempotency_key=idempotency_key,
            risk_level=risk_level
        )

    def plan_operations(self, commands: List[GatewayCommand]) -> CommandPlan:
        return self.gateway.plan_commands(commands)

    def execute_command(self, command: GatewayCommand) -> ExecutionResult:
        return self.gateway.execute_command(command)

    def emergency_stop(self):
        self.gateway.emergency_stop()

    def resume_gateway(self):
        self.gateway.resume_gateway()

    def acquire_lock(self, resource_id: str):
        self.gateway.lock_controller.acquire_lock(resource_id)

    def release_lock(self, resource_id: str):
        self.gateway.lock_controller.release_lock(resource_id)

    def detect_scene_drift(self, actual_scene_objects: Set[str]) -> Optional[str]:
        return self.gateway.state_tracker.detect_drift(actual_scene_objects)

    @property
    def current_scene_version(self) -> int:
        return self.gateway.state_tracker.scene_version
