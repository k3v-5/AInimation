from typing import Dict, Any, List
from ..core.gateway_types import CommandType, RiskLevel, GatewayErrorType
from ..core.gateway_schema import GatewayCommand

class CommandRegistry:
    FORBIDDEN_COMMANDS = {CommandType.DELETE_ALL_OBJECTS}

    @classmethod
    def validate_command_policy(cls, cmd: GatewayCommand):
        if cmd.type in cls.FORBIDDEN_COMMANDS:
            raise PermissionError(f"COMMAND_DENIED: Execution of forbidden command '{cmd.type.value}' is blocked by Gateway Sandboxing Policy.")

        # Validar tipo de comando conocido
        if not isinstance(cmd.type, CommandType):
            raise ValueError(f"COMMAND_INVALID: Unknown command type '{cmd.type}'.")

        # Comprobar target
        if not cmd.target or not cmd.target.strip():
            raise ValueError("COMMAND_INVALID: Command target cannot be empty.")

class CapabilityManager:
    DEFAULT_CAPABILITIES = {
        "supports_mesh_generation": True,
        "supports_material_creation": True,
        "supports_rendering": True,
        "supports_transforms": True,
        "supports_inspection": True,
        "supports_export_fbx": True
    }

    def __init__(self, capabilities: Dict[str, bool] = None):
        self.caps = capabilities if capabilities is not None else dict(self.DEFAULT_CAPABILITIES)

    def check_capability(self, required_cap: str):
        if not self.caps.get(required_cap, False):
            raise ValueError(f"CAPABILITY_UNSUPPORTED: Operation requires MCP capability '{required_cap}' which is unavailable.")
