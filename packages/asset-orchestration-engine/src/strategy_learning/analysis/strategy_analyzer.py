from typing import Dict, Any, List
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOutcome

class StrategyAnalyzer:
    """Computes comprehensive analytical summary of a strategy across all executions."""

    @staticmethod
    def analyze_strategy(strategy: StrategyRecord, outcomes: List[StrategyOutcome]) -> Dict[str, Any]:
        if not outcomes:
            return {
                "strategy_id": strategy.strategy_id,
                "sample_count": 0,
                "success_rate": strategy.historical_success_rate,
                "average_quality": strategy.average_quality_score,
                "failure_rate": strategy.historical_failure_rate,
                "regression_rate": strategy.historical_regression_rate
            }

        total = len(outcomes)
        successes = sum(1 for o in outcomes if o.success)
        failures = sum(1 for o in outcomes if not o.success)
        regressions = sum(1 for o in outcomes if o.regression_detected)

        avg_quality = sum(o.quality_score for o in outcomes) / total
        avg_cost = sum(o.resource_cost for o in outcomes) / total
        avg_time = sum(o.generation_time for o in outcomes) / total
        avg_corrections = sum(o.correction_count for o in outcomes) / total
        avg_recoveries = sum(o.recovery_count for o in outcomes) / total

        return {
            "strategy_id": strategy.strategy_id,
            "sample_count": total,
            "success_rate": round(successes / total, 4),
            "failure_rate": round(failures / total, 4),
            "regression_rate": round(regressions / total, 4),
            "average_quality": round(avg_quality, 4),
            "average_cost": round(avg_cost, 4),
            "average_time": round(avg_time, 4),
            "average_corrections": round(avg_corrections, 4),
            "average_recoveries": round(avg_recoveries, 4)
        }
