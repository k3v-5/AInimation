import math
from typing import List
from ..core.learning_models import StrategyOutcome

class ConfidenceEngine:
    """Calculates statistical confidence of strategy outcomes based on sample volume and consistency."""

    @staticmethod
    def compute_confidence(sample_count: int, failure_rate: float, regression_rate: float) -> float:
        if sample_count <= 0:
            return 0.50

        # Asymptotic curve: confidence increases with sample count
        base = 1.0 - (1.0 / (1.0 + 0.15 * sample_count))
        # Penalize for instabilities
        penalty = (failure_rate * 0.3) + (regression_rate * 0.5)
        conf = max(0.20, min(0.99, base - penalty))
        return round(conf, 4)
