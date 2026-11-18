from typing import List, Dict, Any
from ..core.learning_models import StrategyOutcome

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
