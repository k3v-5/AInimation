import hashlib
import json
from typing import Dict, Any

class ReadinessHasher:
    @classmethod
    def compute_readiness_hash(
        cls,
        asset_id: str,
        source_hash: str,
        engine_profile_id: str,
        status: str,
        score: float
    ) -> str:
        data = {
            "asset_id": asset_id,
            "source_hash": source_hash,
            "profile": engine_profile_id,
            "status": status,
            "score": round(score, 2)
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
