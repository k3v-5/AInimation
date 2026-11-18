import time
from typing import Dict, Any, List
from ...golden.core.golden_models import GoldenAsset
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureType, FailureSeverity, FailureStatus

class RegressionFailureDetector:
    """Detects quality regressions against F76 Golden Assets."""

    @staticmethod
    def detect_regression(
        semantic_id: str,
        golden: GoldenAsset,
        current_score: float,
        critical_dimension_degraded: bool = False
    ) -> List[FailureRecord]:
        records = []
        delta = current_score - golden.baseline_score
        
        if delta < -0.05 or critical_dimension_degraded:
            rec = FailureRecord(
                failure_id=f"FAIL_REG_{golden.golden_id}_{int(time.time()*1000)}",
                semantic_id=semantic_id,
                pipeline_phase="GOLDEN_VERIFICATION",
                pipeline_stage="REGRESSION_CHECK",
                operation="COMPARE_GOLDEN",
                failure_type=FailureType.REGRESSION_ERROR,
                failure_category="GOLDEN_BASELINE",
                severity=FailureSeverity.CRITICAL if critical_dimension_degraded else FailureSeverity.ERROR,
                status=FailureStatus.DETECTED,
                message=f"Regression detected against Golden Asset {golden.golden_id}: Delta={round(delta, 4)}",
                expected_state={"baseline_score": golden.baseline_score},
                actual_state={"current_score": current_score, "delta": delta}
            )
            records.append(rec)

        return records
