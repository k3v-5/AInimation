from enum import Enum
from typing import Tuple

class ProgressClassification(str, Enum):
    STRONG_PROGRESS = "STRONG_PROGRESS"
    PROGRESS = "PROGRESS"
    NEUTRAL = "NEUTRAL"
    REGRESSION = "REGRESSION"
    SEVERE_REGRESSION = "SEVERE_REGRESSION"

class ProgressEvaluator:
    @staticmethod
    def evaluate_progress(score_before: float, score_after: float) -> Tuple[ProgressClassification, float]:
        delta = round(score_after - score_before, 4)
        if delta >= 0.10:
            return ProgressClassification.STRONG_PROGRESS, delta
        elif delta > 0.02:
            return ProgressClassification.PROGRESS, delta
        elif delta >= -0.02:
            return ProgressClassification.NEUTRAL, delta
        elif delta >= -0.08:
            return ProgressClassification.REGRESSION, delta
        else:
            return ProgressClassification.SEVERE_REGRESSION, delta
