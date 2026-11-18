import hashlib
import json
from typing import Dict, Any, List

class QualityHasher:
    @classmethod
    def compute_quality_hash(
        cls,
        asset_id: str,
        overall_score: float,
        status: str,
        level: str,
        profile_id: str
    ) -> str:
        data = {
            "asset_id": asset_id,
            "overall_score": round(overall_score, 2),
            "status": status,
            "level": level,
            "profile_id": profile_id
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
