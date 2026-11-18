from typing import Dict, List, Tuple
from ..core.scene_schema import AssetInstance
from ..core.scene_types import CollisionSeverity

class SceneCollisionValidator:
    @staticmethod
    def check_collisions(
        instances: Dict[str, AssetInstance],
        roads: List[Dict[str, float]] = None
    ) -> List[Tuple[CollisionSeverity, str]]:
        errors: List[Tuple[CollisionSeverity, str]] = []
        inst_list = list(instances.values())
        roads = roads or []

        # 1. Comprobar colisión Asset-Asset
        for i in range(len(inst_list)):
            for j in range(i + 1, len(inst_list)):
                a, b = inst_list[i], inst_list[j]
                if SceneCollisionValidator._aabb_overlap(a, b):
                    errors.append((
                        CollisionSeverity.CRITICAL,
                        f"CRITICAL_COLLISION: Asset '{a.instance_id}' overlaps with '{b.instance_id}'."
                    ))

        # 2. Comprobar colisión Asset-Road
        for a in inst_list:
            for r in roads:
                # Si el asset se superpone al centro de la carretera
                dist_to_road = ((a.transform["x"] - r["x"])**2 + (a.transform["y"] - r["y"])**2)**0.5
                min_clearance = (a.dimensions.get("width", 4.0) / 2.0) + (r.get("width", 3.0) / 2.0)
                if dist_to_road < min_clearance * 0.80:
                    errors.append((
                        CollisionSeverity.CRITICAL,
                        f"CRITICAL_COLLISION: Asset '{a.instance_id}' overlaps with Road at ({r['x']}, {r['y']})."
                    ))

        return errors

    @staticmethod
    def _aabb_overlap(a: AssetInstance, b: AssetInstance) -> bool:
        ax, ay = a.transform["x"], a.transform["y"]
        aw, ad = a.dimensions.get("width", 4.0), a.dimensions.get("depth", 4.0)
        bx, by = b.transform["x"], b.transform["y"]
        bw, bd = b.dimensions.get("width", 4.0), b.dimensions.get("depth", 4.0)

        # Separating axis test 2D AABB
        overlap_x = abs(ax - bx) < ((aw + bw) / 2.0) * 0.90
        overlap_y = abs(ay - by) < ((ad + bd) / 2.0) * 0.90
        return overlap_x and overlap_y
