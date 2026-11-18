from typing import List, Dict, Any
from ..core.learning_models import StrategyOutcome

class CostAnalyzer:
    """Analyzes computational cost, token usage, tool invocations, and duration."""

    @staticmethod
    def analyze_cost(outcomes: List[StrategyOutcome]) -> Dict[str, Any]:
        if not outcomes:
            return {"average_cost": 100.0, "average_time": 30.0, "average_tokens": 1500}

        total = len(outcomes)
        return {
            "average_cost": round(sum(o.resource_cost for o in outcomes) / total, 2),
            "average_time": round(sum(o.generation_time for o in outcomes) / total, 2),
            "average_tokens": int(sum(o.token_cost for o in outcomes) / total),
            "average_blender_calls": round(sum(o.blender_calls for o in outcomes) / total, 2)
        }

class RegressionAnalyzer:
    """Tracks regression risk against F76 Golden Assets."""

    @staticmethod
    def analyze_regression(outcomes: List[StrategyOutcome]) -> Dict[str, Any]:
        if not outcomes:
            return {"regression_rate": 0.0, "is_high_risk": False}

        regressions = sum(1 for o in outcomes if o.regression_detected)
        rate = regressions / len(outcomes)

        return {
            "regression_count": regressions,
            "regression_rate": round(rate, 4),
            "is_high_risk": rate > 0.10
        }
