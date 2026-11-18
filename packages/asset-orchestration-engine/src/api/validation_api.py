from typing import Dict, Any
from ..core.state_manager import StateManager
from ..validation.validator import QualityGateValidator

class ValidationAPI:
    def __init__(self, state_manager: StateManager, validator: QualityGateValidator):
        self.state_manager = state_manager
        self.validator = validator

    def validate_asset(self, asset_id: str) -> Dict[str, Any]:
        graph = self.state_manager.get_graph(asset_id)
        if not graph:
            return {"success": False, "error_code": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' not found."}

        spec = self.state_manager.get_spec(asset_id)
        return self.validator.validate_asset(graph, spec)
