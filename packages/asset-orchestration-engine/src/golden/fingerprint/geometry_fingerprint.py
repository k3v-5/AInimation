import hashlib
import json
from typing import Dict, Any

class GeometryFingerprinter:
    """Computes deterministic SHA-256 fingerprints for 3D asset geometry."""
    
    @staticmethod
    def compute(geometry_data: Dict[str, Any]) -> str:
        canonical = {
            "object_names": sorted(geometry_data.get("object_names", [])),
            "mesh_names": sorted(geometry_data.get("mesh_names", [])),
            "vertex_count": geometry_data.get("vertex_count", 0),
            "polygon_count": geometry_data.get("polygon_count", 0),
            "edge_count": geometry_data.get("edge_count", 0),
            "bounding_box": geometry_data.get("bounding_box", [0, 0, 0]),
            "scale": geometry_data.get("scale", [1.0, 1.0, 1.0]),
            "rotation": geometry_data.get("rotation", [0.0, 0.0, 0.0]),
            "topology": geometry_data.get("topology", "MANIFOLD_QUADS"),
            "lod_count": geometry_data.get("lod_count", 1),
            "collision_hulls": geometry_data.get("collision_hulls", 0)
        }
        raw = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
