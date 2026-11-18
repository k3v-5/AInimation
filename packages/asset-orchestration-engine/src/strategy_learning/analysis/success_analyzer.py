from typing import List, Dict, Any
from ..core.learning_models import StrategyOutcome

class SuccessAnalyzer:
    """Evaluates quality metrics, consistency, and benchmark variance."""

    @staticmethod
    def analyze_success(outcomes: List[StrategyOutcome]) -> Dict[str, Any]:
        if not outcomes:
            return {"success_rate": 1.0, "quality_mean": 0.90, "quality_variance": 0.0}

        scores = [o.quality_score for o in outcomes]
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)

        return {
            "sample_count": len(outcomes),
            "success_rate": round(sum(1 for o in outcomes if o.success) / len(outcomes), 4),
            "quality_mean": round(mean, 4),
            "quality_variance": round(variance, 6),
            "min_score": round(min(scores), 4),
            "max_score": round(max(scores), 4)
        }
