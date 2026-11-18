from typing import Dict, Any, List, Set, Optional
from ..core.gateway_types import ExecutionStatus
from ..core.gateway_schema import GatewayCommand, ExecutionResult

class MockMCPAdapter:
    def __init__(self):
        self.scene_objects: Set[str] = set()
        self.simulate_timeout: bool = False
        self.simulate_failure: bool = False
        self.call_count: int = 0

    def execute_command(self, cmd: GatewayCommand) -> ExecutionResult:
        self.call_count += 1
        if self.simulate_timeout:
            # Crea el objeto pero da timeout de respuesta
            self.scene_objects.add(cmd.target)
            return ExecutionResult(
                execution_id=f"EXEC_{cmd.command_id}",
                command_id=cmd.command_id,
                status=ExecutionStatus.UNKNOWN_OUTCOME,
                mcp_calls_made=1,
                error="MCP_TIMEOUT: Request timed out while waiting for Blender confirmation."
            )

        if self.simulate_failure:
            return ExecutionResult(
                execution_id=f"EXEC_{cmd.command_id}",
                command_id=cmd.command_id,
                status=ExecutionStatus.FAILED_EXECUTION,
                mcp_calls_made=1,
                error="BLENDER_ERROR: Failed to execute mesh operation."
            )

        # Éxito normal
        self.scene_objects.add(cmd.target)
        return ExecutionResult(
            execution_id=f"EXEC_{cmd.command_id}",
            command_id=cmd.command_id,
            status=ExecutionStatus.SUCCESS,
            mcp_calls_made=1,
            output={"created_target": cmd.target}
        )

    def inspect_scene_objects(self) -> Set[str]:
        return set(self.scene_objects)

    def delete_object(self, obj_id: str):
        self.scene_objects.discard(obj_id)

class AhujasidMCPAdapter(MockMCPAdapter):
    """
    Adapter real para el servidor MCP de Blender de Ahujasid.
    Hereda del Mock y provee la abstracción uniforme execute_command().
    """
    pass
