import copy
from typing import Dict, Any, Tuple, Optional
from .blender_provider import IBlenderProvider

class MockBlenderProvider(IBlenderProvider):
    def __init__(self):
        # asset_id -> {"components": {comp_id: {"dimensions": (x,y,z), "material": {...}}}}
        self.assets: Dict[str, Dict[str, Any]] = {}
        self.simulate_timeout = False
        self.simulate_transient_error_count = 0

    def init_asset(self, asset_id: str, components: Dict[str, Dict[str, Any]]):
        self.assets[asset_id] = {
            "components": copy.deepcopy(components)
        }

    def get_component_dimensions(self, asset_id: str, component_id: str) -> Optional[Tuple[float, float, float]]:
        if self.simulate_timeout:
            raise TimeoutError("Simulated MCP timeout.")
        ast = self.assets.get(asset_id)
        if ast and component_id in ast["components"]:
            return ast["components"][component_id].get("dimensions")
        return None

    def set_component_dimensions(self, asset_id: str, component_id: str, dimensions: Tuple[float, float, float]) -> bool:
        if self.simulate_timeout:
            raise TimeoutError("Simulated MCP timeout.")
        if self.simulate_transient_error_count > 0:
            self.simulate_transient_error_count -= 1
            raise ConnectionResetError("Simulated transient connection reset.")

        ast = self.assets.get(asset_id)
        if not ast or component_id not in ast["components"]:
            return False

        ast["components"][component_id]["dimensions"] = tuple(dimensions)
        return True

    def scale_component(self, asset_id: str, component_id: str, factor: float) -> bool:
        cur_dims = self.get_component_dimensions(asset_id, component_id)
        if not cur_dims:
            return False
        new_dims = (cur_dims[0] * factor, cur_dims[1] * factor, cur_dims[2] * factor)
        return self.set_component_dimensions(asset_id, component_id, new_dims)

    def get_material_property(self, asset_id: str, component_id: str, prop_name: str) -> Any:
        ast = self.assets.get(asset_id)
        if ast and component_id in ast["components"]:
            mat = ast["components"][component_id].get("material", {})
            return mat.get(prop_name)
        return None

    def set_material_property(self, asset_id: str, component_id: str, prop_name: str, value: Any) -> bool:
        ast = self.assets.get(asset_id)
        if not ast or component_id not in ast["components"]:
            return False

        if "material" not in ast["components"][component_id]:
            ast["components"][component_id]["material"] = {}
        ast["components"][component_id]["material"][prop_name] = value
        return True

    def get_asset_state(self, asset_id: str) -> Dict[str, Any]:
        return copy.deepcopy(self.assets.get(asset_id, {}))

    def restore_asset_state(self, asset_id: str, state_data: Dict[str, Any]) -> bool:
        self.assets[asset_id] = copy.deepcopy(state_data)
        return True
