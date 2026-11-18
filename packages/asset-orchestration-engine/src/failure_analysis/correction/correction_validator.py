from typing import Optional
from ...evaluation.models.evaluation_models import EvaluationBenchmark, AcceptanceDecision
from ...golden.core.golden_models import GoldenAsset
from ..core.failure_types import FailureStatus

class CorrectionValidator:
    """Validates whether a corrective action successfully resolved the failure without regressions."""

    @staticmethod
    def validate_resolution(
        before_benchmark: EvaluationBenchmark,
        after_benchmark: EvaluationBenchmark,
        golden_asset: Optional[GoldenAsset] = None
    ) -> FailureStatus:
        # 1. Check if after_benchmark is approved
        if after_benchmark.acceptance != AcceptanceDecision.APPROVED:
            if after_benchmark.weighted_score > before_benchmark.weighted_score:
                return FailureStatus.PARTIALLY_RESOLVED
            return FailureStatus.UNRESOLVED

        # 2. Check for regression against Golden Asset if present
        if golden_asset:
            delta = after_benchmark.weighted_score - golden_asset.baseline_score
            if delta < -0.05:
                return FailureStatus.UNRESOLVED

        return FailureStatus.RESOLVED
