from typing import Dict, Any, Optional
from ..core.failure_types import ResolutionStatus
from ...evaluation import EvaluationBenchmark, AcceptanceDecision, DefectSeverity
from ...golden import GoldenComparisonResult, RegressionLevel

class CorrectionValidator:
    """Validates whether a corrective action successfully resolved the failure without introducing regressions."""
    
    @staticmethod
    def validate_resolution(
        before_benchmark: EvaluationBenchmark,
        after_benchmark: EvaluationBenchmark,
        golden_comparison: Optional[GoldenComparisonResult] = None
    ) -> ResolutionStatus:
        # Check acceptance
        if after_benchmark.acceptance != AcceptanceDecision.APPROVED:
            # Check if partially improved
            if after_benchmark.weighted_score > before_benchmark.weighted_score:
                return ResolutionStatus.PARTIALLY_RESOLVED
            return ResolutionStatus.UNRESOLVED

        # Check critical defects
        has_crit = any(d.severity == DefectSeverity.CRITICAL or d.blocking for d in after_benchmark.defects)
        if has_crit:
            return ResolutionStatus.UNRESOLVED

        # Check Golden regression
        if golden_comparison and golden_comparison.critical_regression:
            return ResolutionStatus.UNRESOLVED

        if after_benchmark.weighted_score >= before_benchmark.weighted_score:
            return ResolutionStatus.RESOLVED

        return ResolutionStatus.PARTIALLY_RESOLVED
