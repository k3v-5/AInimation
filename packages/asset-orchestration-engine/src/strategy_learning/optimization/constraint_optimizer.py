from typing import Dict, Any, List
from ..core.strategy_models import StrategyRecord
from ..core.feature_models import ProblemFeatures

class ConstraintOptimizer:
    """Enforces hard budget and engine constraints against proposed strategies."""

    @staticmethod
    def validate_constraints(strategy: StrategyRecord, features: ProblemFeatures) -> bool:
        # Check budget limits
        poly_budget = features.polygon_budget
        strat_poly = strategy.input_features.get("polygon_budget", poly_budget)
        if strat_poly > poly_budget * 1.25:
            return False

        # Check time limit
        if strategy.estimated_time > features.time_budget * 1.5:
            return False

        return True
