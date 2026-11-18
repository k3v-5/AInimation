from typing import Dict, Any, List
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOptimizationProfile

class CandidateScorer:
    """Calculates objective utility score for candidate strategies based on explicit optimization profiles."""

    @staticmethod
    def calculate_score(strategy: StrategyRecord, profile: StrategyOptimizationProfile) -> float:
        # Normalize cost and time: lower is better
        cost_norm = max(0.0, 1.0 - (strategy.estimated_cost / 300.0))
        time_norm = max(0.0, 1.0 - (strategy.estimated_time / 120.0))
        rel_norm = strategy.historical_success_rate * (1.0 - strategy.historical_regression_rate)

        score = (
            (strategy.average_quality_score * profile.weight_quality) +
            (strategy.average_quality_score * profile.weight_visual) +
            (1.0 * profile.weight_engine_readiness) +
            (rel_norm * profile.weight_reliability) +
            (cost_norm * profile.weight_cost) +
            (time_norm * profile.weight_time) +
            (strategy.confidence * profile.weight_confidence)
        )
        return min(1.0, max(0.0, round(score, 4)))
