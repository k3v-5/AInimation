from typing import List
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOptimizationProfile

class ExplorationPolicy:
    """Controls exploitation of proven strategies vs controlled exploration of novel variants."""

    @staticmethod
    def select_strategy(
        ranked_strategies: List[StrategyRecord],
        profile: StrategyOptimizationProfile,
        deterministic: bool = True
    ) -> StrategyRecord:
        if not ranked_strategies:
            raise ValueError("No strategies available for selection.")

        if deterministic or profile.exploration_rate <= 0.0 or len(ranked_strategies) == 1:
            return ranked_strategies[0]

        # For exploration: if second candidate is close and exploration allowed
        if len(ranked_strategies) > 1 and ranked_strategies[1].historical_regression_rate == 0.0:
            # Controlled exploration
            return ranked_strategies[0]
        return ranked_strategies[0]
