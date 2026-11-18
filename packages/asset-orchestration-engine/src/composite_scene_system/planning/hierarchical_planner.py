import hashlib
import json
from typing import Dict, Any, List
from ..core.scene_types import PlanningStage, SceneState
from ..core.scene_schema import (
    SceneSpecification, SceneBuildPlan, SceneRegion, SceneArea, AssetInstance
)
from ..spatial.spatial_solver import SpatialConstraintSolver

class HierarchicalPlanner:
    @staticmethod
    def plan_scene(spec: SceneSpecification) -> SceneBuildPlan:
        instances: Dict[str, AssetInstance] = {}
        regions: Dict[str, SceneRegion] = {
            "CENTER": SceneRegion("CENTER", "Plaza Center"),
            "NORTH": SceneRegion("NORTH", "North Quarter"),
            "EAST_REGION": SceneRegion("EAST_REGION", "East Quarter"),
            "WEST_REGION": SceneRegion("WEST_REGION", "West Quarter"),
            "SOUTH_REGION": SceneRegion("SOUTH_REGION", "South Quarter"),
            "COMMERCIAL": SceneRegion("COMMERCIAL", "Market District")
        }

        # 1. Crear Macro/Landmark instances (Plaza, Church)
        if spec.components_count.get("plaza", 0) > 0:
            instances["PLAZA_001"] = AssetInstance(
                instance_id="PLAZA_001",
                asset_type="PLAZA",
                template_id="template_plaza_stone",
                dimensions={"width": 12.0, "depth": 12.0, "height": 0.5},
                region_id="CENTER"
            )

        if spec.components_count.get("church", 0) > 0:
            instances["CHURCH_001"] = AssetInstance(
                instance_id="CHURCH_001",
                asset_type="CHURCH",
                template_id="template_church_gothic",
                dimensions={"width": 8.0, "depth": 14.0, "height": 16.0},
                region_id="NORTH"
            )

        # 2. Crear Meso instances (Shops, Houses)
        shop_cnt = spec.components_count.get("shops", spec.components_count.get("shop", 0))
        for i in range(shop_cnt):
            s_id = f"SHOP_{i+1:03d}"
            instances[s_id] = AssetInstance(
                instance_id=s_id,
                asset_type="SHOP",
                template_id="template_medieval_shop",
                dimensions={"width": 5.0, "depth": 4.5, "height": 5.5},
                region_id="COMMERCIAL"
            )

        house_cnt = spec.components_count.get("houses", spec.components_count.get("house", 8))
        for i in range(house_cnt):
            h_id = f"HOUSE_{i+1:03d}"
            instances[h_id] = AssetInstance(
                instance_id=h_id,
                asset_type="HOUSE",
                template_id="template_medieval_house",
                dimensions={"width": 4.0, "depth": 3.5, "height": 5.0}
            )

        # 3. Resolver posicionamiento espacial y orientaciones
        SpatialConstraintSolver.solve_village_radial_layout(spec, instances)

        # 4. Asignar instancias a áreas y regiones
        for inst in instances.values():
            reg_id = inst.region_id
            if reg_id in regions:
                area_id = f"AREA_{reg_id}"
                if area_id not in regions[reg_id].areas:
                    regions[reg_id].areas[area_id] = SceneArea(area_id, f"Area for {reg_id}", reg_id)
                regions[reg_id].areas[area_id].instance_ids.append(inst.instance_id)

        build_order = ["terrain", "roads", "plaza", "church", "houses", "shops", "fences", "props"]

        return SceneBuildPlan(
            scene_id=spec.scene_id,
            build_order=build_order,
            regions=regions,
            instances=instances,
            status=SceneState.PLANNED,
            stage=PlanningStage.COMPLETED
        )

    @staticmethod
    def compute_scene_fingerprint(plan: SceneBuildPlan, seed: int = 42) -> str:
        payload = {
            "scene_id": plan.scene_id,
            "seed": seed,
            "instances": {
                k: {
                    "type": v.asset_type,
                    "pos": [round(v.transform["x"], 2), round(v.transform["y"], 2), round(v.transform["z"], 2)],
                    "rot_z": round(v.transform["rot_z"], 1)
                }
                for k, v in sorted(plan.instances.items())
            }
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
