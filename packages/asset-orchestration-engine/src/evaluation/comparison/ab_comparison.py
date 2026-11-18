from dataclasses import dataclass, field
from typing import Dict, List, Any
from ..models.evaluation_models import EvaluationBenchmark
from ..core.evaluation_types import EvaluationDimension, DefectSeverity

@dataclass
class ABComparisonResult:
    winner: str
    score_a: float
    score_b: float
    global_delta: float
    dimension_deltas: Dict[str, float] = field(default_factory=dict)
    improvements: List[str] = field(default_factory=list)
    regressions: List[str] = field(default_factory=list)
    critical_failures: List[str] = field(default_factory=list)
    confidence: float = 1.0

class ABComparisonEngine:
    """Performs structured A/B comparisons between two candidate evaluation benchmarks."""
    
    @classmethod
    def compare_benchmarks(cls, bench_a: EvaluationBenchmark, bench_b: EvaluationBenchmark) -> ABComparisonResult:
        delta = round(bench_b.weighted_score - bench_a.weighted_score, 4)
        dim_deltas: Dict[str, float] = {}
        improvements: List[str] = []
        regressions: List[str] = []
        critical_failures: List[str] = []

        all_dims = set(bench_a.dimension_scores.keys()).union(set(bench_b.dimension_scores.keys()))
        for dim in all_dims:
            score_a = bench_a.dimension_scores.get(dim).score if dim in bench_a.dimension_scores else 0.0
            score_b = bench_b.dimension_scores.get(dim).score if dim in bench_b.dimension_scores else 0.0
            d_delta = round(score_b - score_a, 4)
            dim_deltas[dim.value] = d_delta

            if d_delta > 0.001:
                improvements.append(f"{dim.value} (+{d_delta})")
            elif d_delta < -0.001:
                regressions.append(f"{dim.value} ({d_delta})")

        # Critical defects in B
        for defect in bench_b.defects:
            if defect.severity == DefectSeverity.CRITICAL or defect.blocking:
                critical_failures.append(f"Candidate B: {defect.description}")

        winner = bench_b.candidate_id if delta > 0 and not critical_failures else bench_a.candidate_id
        if delta == 0:
            winner = "TIE"

        conf = round(min(bench_a.confidence, bench_b.confidence), 4)

        return ABComparisonResult(
            winner=winner,
            score_a=round(bench_a.weighted_score, 4),
            score_b=round(bench_b.weighted_score, 4),
            global_delta=delta,
            dimension_deltas=dim_deltas,
            improvements=improvements,
            regressions=regressions,
            critical_failures=critical_failures,
            confidence=conf
        )
