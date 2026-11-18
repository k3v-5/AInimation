from typing import List
from ...evaluation import EvaluationBenchmark, AcceptanceDecision, DefectSeverity
from ..core.golden_types import GoldenAssetException

class EvaluationBridge:
    """Bridges and validates F75 EvaluationBenchmarks for Golden Asset registration."""
    
    @staticmethod
    def validate_benchmark_for_golden(benchmark: EvaluationBenchmark, min_score: float = 0.85) -> List[str]:
        errors: List[str] = []
        if benchmark.acceptance != AcceptanceDecision.APPROVED:
            errors.append(f"Benchmark acceptance status is '{benchmark.acceptance.value}', must be 'APPROVED'.")

        if benchmark.weighted_score < min_score:
            errors.append(f"Benchmark score {round(benchmark.weighted_score, 4)} is below required threshold {min_score}.")

        crit = [d for d in benchmark.defects if d.severity == DefectSeverity.CRITICAL or d.blocking]
        if crit:
            errors.append(f"Benchmark contains {len(crit)} critical/blocking defects.")

        if not benchmark.verify_integrity():
            errors.append("Benchmark failed cryptographic integrity verification.")

        return errors
