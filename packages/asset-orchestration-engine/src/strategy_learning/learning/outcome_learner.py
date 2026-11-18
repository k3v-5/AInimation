import time
from typing import Optional
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOutcome, LearningEvent
from ..ranking.confidence_engine import ConfidenceEngine

class OutcomeLearner:
    """Updates strategy performance statistics incrementally from execution outcomes."""

    @staticmethod
    def learn_from_outcome(strategy: StrategyRecord, outcome: StrategyOutcome) -> LearningEvent:
        n = strategy.sample_count
        new_n = n + 1

        # Moving average quality
        old_q = strategy.average_quality_score
        new_q = ((old_q * n) + outcome.quality_score) / new_n

        # Moving average success
        old_succ = strategy.historical_success_rate
        new_succ = ((old_succ * n) + (1.0 if outcome.success else 0.0)) / new_n
        new_fail = 1.0 - new_succ

        # Moving average regression
        old_reg = strategy.historical_regression_rate
        new_reg = ((old_reg * n) + (1.0 if outcome.regression_detected else 0.0)) / new_n

        # Moving average cost and time
        strategy.estimated_cost = ((strategy.estimated_cost * n) + outcome.resource_cost) / new_n
        strategy.estimated_time = ((strategy.estimated_time * n) + outcome.generation_time) / new_n

        # Update confidence
        new_conf = ConfidenceEngine.compute_confidence(new_n, new_fail, new_reg)

        delta_q = new_q - old_q
        delta_c = new_conf - strategy.confidence

        strategy.sample_count = new_n
        strategy.average_quality_score = round(new_q, 4)
        strategy.historical_success_rate = round(new_succ, 4)
        strategy.historical_failure_rate = round(new_fail, 4)
        strategy.historical_regression_rate = round(new_reg, 4)
        strategy.confidence = new_conf
        strategy.updated_at = time.time()

        return LearningEvent(
            event_id=f"EVT_{strategy.strategy_id}_{int(time.time()*1000)}",
            strategy_id=strategy.strategy_id,
            semantic_id=outcome.semantic_id,
            event_type="OUTCOME_LEARNED",
            delta_quality=delta_q,
            delta_confidence=delta_c,
            reason=f"Execution outcome processed (Success={outcome.success}, Quality={round(outcome.quality_score, 4)})"
        )
