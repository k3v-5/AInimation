from typing import List, Dict, Any
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOutcome

class PatternLearner:
    """Discovers high-level generation patterns correlating methods with high quality."""

    @staticmethod
    def discover_best_methods(strategies: List[StrategyRecord]) -> Dict[str, str]:
        if not strategies:
            return {}

        best_strat = max(strategies, key=lambda s: s.average_quality_score)
        return {
            "preferred_generation_method": best_strat.generation_method,
            "preferred_geometry_method": best_strat.geometry_method,
            "preferred_material_method": best_strat.material_method,
            "preferred_uv_method": best_strat.uv_method,
            "preferred_lod_method": best_strat.lod_method
        }
