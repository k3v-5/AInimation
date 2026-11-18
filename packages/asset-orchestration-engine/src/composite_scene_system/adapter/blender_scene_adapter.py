from typing import Dict, Any, List
from ..core.scene_schema import SceneBuildPlan, AssetInstance

class BlenderSceneAdapter:
    def __init__(self):
        self.blender_collections: Dict[str, List[str]] = {}
        self.blender_objects: Dict[str, Dict[str, Any]] = {}

    def sync_scene_plan(self, plan: SceneBuildPlan):
        """
        Traduce el plan abstracto de escena a jerarquías de colecciones e instancias de Blender.
        """
        for reg_id, region in plan.regions.items():
            if reg_id not in self.blender_collections:
                self.blender_collections[reg_id] = []

        for inst_id, inst in plan.instances.items():
            reg_id = inst.region_id
            if reg_id in self.blender_collections:
                if inst_id not in self.blender_collections[reg_id]:
                    self.blender_collections[reg_id].append(inst_id)

            self.blender_objects[inst_id] = {
                "asset_type": inst.asset_type,
                "transform": dict(inst.transform),
                "is_instance": inst.is_instance_of_id is not None,
                "lock_state": inst.lock_state.value
            }

    def get_blender_object_state(self, instance_id: str) -> Dict[str, Any]:
        return self.blender_objects.get(instance_id, {})
