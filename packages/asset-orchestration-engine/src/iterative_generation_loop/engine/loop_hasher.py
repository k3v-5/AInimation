import hashlib
import json
from typing import Dict, Any, List

class LoopHasher:
    @classmethod
    def compute_loop_hash(
        cls,
        loop_id: str,
        asset_id: str,
        iterations_count: int,
        best_iteration: int,
        stop_reason: str
    ) -> str:
        data = {
            "loop_id": loop_id,
            "asset_id": asset_id,
            "iterations_count": iterations_count,
            "best_iter": best_iteration,
            "stop": stop_reason
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
