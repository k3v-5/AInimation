from typing import List, Optional
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOutcome, LearningEvent
from .outcome_learner import OutcomeLearner

class LearningEngine:
    """Coordinates learning pipeline from execution outcomes."""

    @staticmethod
    def process_outcome(strategy: StrategyRecord, outcome: StrategyOutcome) -> LearningEvent:
        return OutcomeLearner.learn_from_outcome(strategy, outcome)
