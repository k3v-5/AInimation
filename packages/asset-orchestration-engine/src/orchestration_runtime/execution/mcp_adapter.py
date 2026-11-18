import time
from typing import Dict, Any, Optional, Set

class MCPAdapter:
    COMMAND_ALLOWLIST: Set[str] = {
        "CREATE_OBJECT",
        "MODIFY_OBJECT",
        "MODIFY_MATERIAL",
        "DELETE_OBJECT",
        "QUERY_SCENE",
        "RENDER",
        "EXPORT"
    }

    def __init__(self):
        self.executed_keys: Dict[str, Dict[str, Any]] = {}
        self.scene_objects: Dict[str, Set[str]] = {} # asset_id -> set of created object names

    def execute_command(
        self,
        command: str,
        asset_id: str,
        parameters: Dict[str, Any],
        idempotency_key: str,
        simulated_timeout: bool = False
    ) -> Dict[str, Any]:
        if command not in self.COMMAND_ALLOWLIST:
            raise PermissionError(f"FORBIDDEN_COMMAND: Command '{command}' is not in MCP allowlist.")

        if idempotency_key in self.executed_keys:
            return self.executed_keys[idempotency_key]

        if simulated_timeout:
            raise TimeoutError("MCP_TIMEOUT: Blender MCP connection timed out.")

        # Simular ejecución en escena
        if asset_id not in self.scene_objects:
            self.scene_objects[asset_id] = set()

        if command == "CREATE_OBJECT":
            obj_name = parameters.get("object_name", "Object")
            self.scene_objects[asset_id].add(obj_name)
        elif command == "DELETE_OBJECT":
            obj_name = parameters.get("object_name", "")
            self.scene_objects[asset_id].discard(obj_name)

        result = {
            "status": "SUCCESS",
            "command": command,
            "asset_id": asset_id,
            "timestamp": time.time(),
            "scene_objects": list(self.scene_objects[asset_id])
        }
        self.executed_keys[idempotency_key] = result
        return result

    def query_scene(self, asset_id: str) -> Set[str]:
        return self.scene_objects.get(asset_id, set())
