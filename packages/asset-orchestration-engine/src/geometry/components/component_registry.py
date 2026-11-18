from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from ..generators.base_generator import GeneratedGeometry

@dataclass
class GeometricComponent:
    component_id: str
    asset_id: str
    component_type: str
    generator_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    geometry: Optional[GeneratedGeometry] = None
    version: int = 1
    status: str = "CLEAN" # CLEAN, DIRTY, BUILDING, BUILT, INVALID, FAILED

class ComponentRegistry:
    def __init__(self):
        self.components: Dict[str, GeometricComponent] = {}

    def register(self, comp: GeometricComponent):
        self.components[comp.component_id] = comp

    def get(self, component_id: str) -> Optional[GeometricComponent]:
        if component_id in self.components:
            return self.components[component_id]
        # Buscar por sufijo
        for cid, comp in self.components.items():
            if cid.endswith(f".{component_id}") or comp.component_type == component_id:
                return comp
        return None

    def list_components(self, asset_id: Optional[str] = None) -> List[GeometricComponent]:
        if asset_id:
            return [c for c in self.components.values() if c.asset_id == asset_id]
        return list(self.components.values())
