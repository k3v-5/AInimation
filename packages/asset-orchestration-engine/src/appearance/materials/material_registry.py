from typing import Dict, Optional, List
from .material_schema import MaterialDefinition
from .material_instance import MaterialInstance

class MaterialRegistry:
    def __init__(self):
        self.materials: Dict[str, MaterialDefinition] = {}
        self.instances: Dict[str, MaterialInstance] = {}

    def register_material(self, material: MaterialDefinition):
        self.materials[material.material_id] = material

    def get_material(self, material_id: str) -> Optional[MaterialDefinition]:
        return self.materials.get(material_id)

    def register_instance(self, instance: MaterialInstance):
        self.instances[instance.instance_id] = instance

    def get_instance(self, instance_id: str) -> Optional[MaterialInstance]:
        return self.instances.get(instance_id)

    def get_instance_for_component(self, component_id: str) -> Optional[MaterialInstance]:
        for inst in self.instances.values():
            if inst.component_id == component_id:
                return inst
        return None

    def list_materials(self) -> List[MaterialDefinition]:
        return list(self.materials.values())
