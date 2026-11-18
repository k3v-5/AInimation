from typing import Dict, Any, List

class ParameterOptimizer:
    """Optimizes generation parameter knobs (polygon budget, decimation, bevel, subds)."""

    @staticmethod
    def recommend_best_parameter(configurations: List[Dict[str, Any]], param_name: str) -> Any:
        # configurations: list of {"params": {param_name: val}, "score": float}
        if not configurations:
            return None
        best = max(configurations, key=lambda c: c.get("score", 0.0))
        return best.get("params", {}).get(param_name)
