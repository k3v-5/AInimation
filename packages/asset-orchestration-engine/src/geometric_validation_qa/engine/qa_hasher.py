import hashlib
import json
from typing import Dict, Any, List

class QAHasher:
    @classmethod
    def compute_validation_hash(
        cls,
        geometry_id: str,
        inventory_dict: Dict[str, Any],
        scores_dict: Dict[str, float],
        defects: List[Any],
        status: str
    ) -> str:
        data = {
            "geometry_id": geometry_id,
            "tris": inventory_dict.get("triangle_count", 0),
            "verts": inventory_dict.get("vertex_count", 0),
            "scores": {k: round(v, 4) for k, v in sorted(scores_dict.items())},
            "defects": [
                {
                    "id": getattr(d, "defect_id", ""),
                    "cat": getattr(getattr(d, "category", None), "value", str(getattr(d, "category", ""))),
                    "sev": getattr(getattr(d, "severity", None), "value", str(getattr(d, "severity", "")))
                } for d in defects
            ],
            "status": status
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
