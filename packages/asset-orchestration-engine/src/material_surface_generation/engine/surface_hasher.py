import hashlib
import json
from typing import Dict, Any, List

class SurfaceHasher:
    @classmethod
    def compute_surface_hash(
        cls,
        materials: Dict[str, Any],
        assignments: List[Any],
        uv_layouts: List[Any],
        attributes: List[Any],
        surface_version: str
    ) -> str:
        data = {
            "version": surface_version,
            "materials": {
                k: {
                    "class": v.material_class.value if hasattr(v.material_class, "value") else str(v.material_class),
                    "base_color": v.base_color,
                    "metallic": v.metallic,
                    "roughness": v.roughness
                } for k, v in sorted(materials.items())
            },
            "assignments": [
                {
                    "region": a.surface_region_id,
                    "object": a.object_id,
                    "material": a.material_id
                } for a in assignments
            ],
            "uvs": [
                {"channel": u.uv_channel, "resolution": u.resolution, "padding": u.padding} for u in uv_layouts
            ],
            "attributes": [
                {"name": att.attribute_name, "channel": att.channel} for att in attributes
            ]
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
