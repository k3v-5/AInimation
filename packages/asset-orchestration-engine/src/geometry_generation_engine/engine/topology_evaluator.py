import hashlib
import json
from typing import Dict, Any, List
from ..core.geom_schema import TopologySummary, GeometryObjectSpec

class TopologyEvaluator:
    @classmethod
    def evaluate_topology(cls, objects: Dict[str, GeometryObjectSpec]) -> TopologySummary:
        tot_v = sum(o.topology.vertex_count for o in objects.values())
        tot_e = sum(o.topology.edge_count for o in objects.values())
        tot_f = sum(o.topology.face_count for o in objects.values())
        tot_t = sum(o.topology.triangle_count for o in objects.values())
        tot_ng = sum(o.topology.ngon_count for o in objects.values())
        tot_nm = sum(o.topology.non_manifold_count for o in objects.values())
        tot_deg = sum(o.topology.degenerate_face_count for o in objects.values())
        all_manifold = all(o.topology.is_manifold for o in objects.values())

        return TopologySummary(
            vertex_count=tot_v,
            edge_count=tot_e,
            face_count=tot_f,
            triangle_count=tot_t,
            ngon_count=tot_ng,
            non_manifold_count=tot_nm,
            degenerate_face_count=tot_deg,
            is_manifold=all_manifold
        )

    @classmethod
    def compute_bounds(cls, objects: Dict[str, GeometryObjectSpec]) -> Dict[str, Any]:
        if not objects:
            return {"min": (0,0,0), "max": (0,0,0), "dimensions": {"x": 0.0, "y": 0.0, "z": 0.0}}

        min_x = min(o.bounds["min"][0] for o in objects.values())
        min_y = min(o.bounds["min"][1] for o in objects.values())
        min_z = min(o.bounds["min"][2] for o in objects.values())

        max_x = max(o.bounds["max"][0] for o in objects.values())
        max_y = max(o.bounds["max"][1] for o in objects.values())
        max_z = max(o.bounds["max"][2] for o in objects.values())

        return {
            "min": (min_x, min_y, min_z),
            "max": (max_x, max_y, max_z),
            "dimensions": {
                "x": round(max_x - min_x, 3),
                "y": round(max_y - min_y, 3),
                "z": round(max_z - min_z, 3)
            }
        }

    @classmethod
    def compute_geometry_hash(cls, objects: Dict[str, GeometryObjectSpec], generation_version: str) -> str:
        # Serializar propiedades invariantes geométricas
        logical = {
            "version": generation_version,
            "objects": {
                k: {
                    "dimensions": v.dimensions,
                    "topology": v.topology.__dict__,
                    "modifiers": v.modifiers,
                    "material_slots": v.material_slots
                } for k, v in sorted(objects.items())
            }
        }
        serialized = json.dumps(logical, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
