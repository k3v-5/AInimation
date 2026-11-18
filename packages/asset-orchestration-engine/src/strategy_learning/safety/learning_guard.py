from typing import Tuple
from ..core.learning_models import StrategyOutcome

class LearningGuard:
    """Blocks corrupted, invalid, or regression-inducing outcomes from corrupting positive knowledge."""

    @staticmethod
    def is_outcome_valid_for_learning(outcome: StrategyOutcome) -> Tuple[bool, str]:
        if not outcome.success and outcome.quality_score == 0.0:
            return False, "Corrupted or incomplete execution"

        if outcome.regression_detected and outcome.golden_asset_delta < -0.10:
            return False, "Severe regression detected against Golden Asset"

        return True, "Outcome validated for learning"
