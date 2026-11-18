from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class RegisteredComponent:
    component_id: str
    asset_id: str
    object_id: str
    semantic_role: str # blade, guard, grip, pommel
    is_locked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class ComponentRegistry:
    def __init__(self):
        self.components: Dict[str, RegisteredComponent] = {} # component_id -> RegisteredComponent
        self.asset_components: Dict[str, List[str]] = {} # asset_id -> [component_id]

    def register(self, component: RegisteredComponent):
        self.components[component.component_id] = component
        if component.asset_id not in self.asset_components:
            self.asset_components[component.asset_id] = []
        if component.component_id not in self.asset_components[component.asset_id]:
            self.asset_components[component.asset_id].append(component.component_id)

    def get(self, component_id: str) -> Optional[RegisteredComponent]:
        return self.components.get(component_id)

    def is_locked(self, component_id: str) -> bool:
        comp = self.get(component_id)
        return comp.is_locked if comp else False

    def lock_component(self, component_id: str, locked: bool = True):
        comp = self.get(component_id)
        if comp:
            comp.is_locked = locked
