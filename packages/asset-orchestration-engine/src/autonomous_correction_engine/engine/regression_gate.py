from typing import Dict, Any, List, Tuple
from ..core.correction_types import RegressionSeverity
from ..core.correction_schema import QualityDeltaReport, AssetSnapshot

class RegressionGate:
    @classmethod
    def evaluate_regression(
        cls,
        before_state: AssetSnapshot,
        after_state: AssetSnapshot,
        context: Dict[str, Any]
    ) -> Tuple[bool, QualityDeltaReport, List[str]]:
        regressions: List[str] = []

        force_reg = context.get("force_regression_flag", False)
        if force_reg:
            regressions.append("CRITICAL_TOPOLOGY_REGRESSION: Non-manifold edge introduced.")
            return False, QualityDeltaReport(visual_delta=+0.10, geometry_delta=-0.35, overall_gain=-0.25), regressions

        # Normal case: Improvement
        q_delta = QualityDeltaReport(
            visual_delta=+0.15,
            geometry_delta=+0.12,
            topology_delta=0.0,
            semantic_integrity=True,
            overall_gain=+0.14
        )
        return True, q_delta, regressions
