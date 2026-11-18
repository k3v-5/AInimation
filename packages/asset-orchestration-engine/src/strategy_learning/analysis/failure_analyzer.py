from typing import List, Dict, Any
from ..core.learning_models import StrategyOutcome

class FailureAnalyzer:
    """Evaluates failure frequencies and penalty factors based on F77 defect records."""

    @staticmethod
    def analyze_failures(outcomes: List[StrategyOutcome]) -> Dict[str, Any]:
        if not outcomes:
            return {"failure_rate": 0.0, "total_failures": 0, "penalty_factor": 0.0}

        total_fails = sum(o.failure_count for o in outcomes)
        fail_outcomes = sum(1 for o in outcomes if not o.success or o.failure_count > 0)
        rate = fail_outcomes / len(outcomes)

        return {
            "failure_rate": round(rate, 4),
            "total_failures": total_fails,
            "penalty_factor": round(min(1.0, rate * 1.5), 4)
        }
