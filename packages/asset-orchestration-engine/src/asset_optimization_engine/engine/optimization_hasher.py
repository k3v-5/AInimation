import hashlib
import json
from typing import Dict, Any

class OptimizationHasher:
    @classmethod
    def compute_optimization_hash(
        cls,
        asset_id: str,
        baseline_cost_index: float,
        optimized_cost_index: float,
        selected_strategy: str,
        status: str
    ) -> str:
        data = {
            "asset_id": asset_id,
            "base_cost": round(baseline_cost_index, 2),
            "opt_cost": round(optimized_cost_index, 2),
            "strategy": selected_strategy,
            "status": status
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
