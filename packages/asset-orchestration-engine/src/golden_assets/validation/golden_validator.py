from typing import Dict, Any, List, Optional
from ..core.golden_exceptions import GoldenPromotionError
from ...evaluation import EvaluationBenchmark, AcceptanceDecision, DefectSeverity

class GoldenValidator:
    """Validates whether a candidate asset satisfies all rigorous criteria to become a Golden Asset."""
    
    @classmethod
    def validate_for_promotion(
        cls,
        benchmark: EvaluationBenchmark,
        min_global_score: float = 0.85,
        allowed_critical_defects: int = 0
    ) -> List[str]:
        errors: List[str] = []

        if benchmark.acceptance != AcceptanceDecision.APPROVED:
            errors.append(f"Benchmark acceptance is '{benchmark.acceptance.value}', must be 'APPROVED'.")

        if benchmark.weighted_score < min_global_score:
            errors.append(f"Benchmark global score {round(benchmark.weighted_score, 4)} is below threshold {min_global_score}.")

        crit_defects = [d for d in benchmark.defects if d.severity == DefectSeverity.CRITICAL or d.blocking]
        if len(crit_defects) > allowed_critical_defects:
            errors.append(f"Found {len(crit_defects)} critical/blocking defects (max allowed: {allowed_critical_defects}).")

        # Specific domain validation
        if not benchmark.verify_integrity():
            errors.append("Benchmark content hash verification failed.")

        return errors
