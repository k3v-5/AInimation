from typing import Dict, Any, List
from ..core.golden_types import RegressionLevel

class RegressionPolicy:
    """Configurable policy determining regression levels and critical veto conditions."""
    def __init__(
        self,
        variation_threshold: float = 0.02,
        regression_threshold: float = 0.05,
        critical_dimensions: List[str] = None
    ):
        self.variation_threshold = variation_threshold
        self.regression_threshold = regression_threshold
        self.critical_dimensions = critical_dimensions or [
            "GEOMETRY", "COLLISION", "ENGINE_READINESS", "SILHOUETTE"
        ]

    def evaluate_regression(
        self,
        candidate_score: float,
        golden_score: float,
        dimension_deltas: Dict[str, float],
        has_critical_defect: bool = False
    ) -> RegressionLevel:
        if has_critical_defect:
            return RegressionLevel.CRITICAL_REGRESSION

        # Check critical dimensions
        for crit in self.critical_dimensions:
            d_delta = dimension_deltas.get(crit, 0.0)
            if d_delta < -self.regression_threshold:
                return RegressionLevel.CRITICAL_REGRESSION

        global_delta = candidate_score - golden_score

        if global_delta > 0.005:
            return RegressionLevel.IMPROVEMENT
        elif global_delta >= -self.variation_threshold:
            return RegressionLevel.ACCEPTABLE_VARIATION
        elif global_delta >= -self.regression_threshold:
            return RegressionLevel.REGRESSION
        else:
            return RegressionLevel.CRITICAL_REGRESSION
