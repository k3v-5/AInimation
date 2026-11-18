from typing import Dict, Optional, List
from ..core.library_schema import ComponentDefinition

class ComponentRegistry:
    def __init__(self):
        self.components: Dict[str, ComponentDefinition] = {}
        self._init_defaults()

    def register_component(self, comp: ComponentDefinition):
        self.components[comp.component_id] = comp

    def get_component(self, comp_id: str) -> Optional[ComponentDefinition]:
        return self.components.get(comp_id)

    def _init_defaults(self):
        # Blades
        self.register_component(ComponentDefinition(
            component_id="blade_standard", category="blade", version="1.0.0",
            parameters={"blade_length": 0.90, "blade_width": 0.05, "blade_thickness": 0.02},
            materials={"metallic": 0.90, "roughness": 0.25}
        ))
        self.register_component(ComponentDefinition(
            component_id="blade_broad", category="blade", version="1.0.0",
            parameters={"blade_length": 0.85, "blade_width": 0.08, "blade_thickness": 0.025},
            materials={"metallic": 0.90, "roughness": 0.25}
        ))
        # Guards
        self.register_component(ComponentDefinition(
            component_id="guard_cross", category="guard", version="1.0.0",
            parameters={"guard_width": 0.18, "guard_thickness": 0.04},
            materials={"metallic": 0.90, "roughness": 0.30}
        ))
        # Handles
        self.register_component(ComponentDefinition(
            component_id="handle_leather", category="handle", version="1.0.0",
            parameters={"handle_length": 0.22, "handle_radius": 0.03},
            materials={"material_type": "LEATHER", "roughness": 0.80}
        ))
        self.register_component(ComponentDefinition(
            component_id="handle_wood", category="handle", version="1.0.0",
            parameters={"handle_length": 0.22, "handle_radius": 0.03},
            materials={"material_type": "WOOD", "roughness": 0.70}
        ))
        # Pommels
        self.register_component(ComponentDefinition(
            component_id="pommel_round", category="pommel", version="1.0.0",
            parameters={"pommel_size": 0.04},
            materials={"metallic": 0.90, "roughness": 0.30}
        ))
