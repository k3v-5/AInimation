from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from ..core.golden_types import ComparisonOutcome
from ..models.golden_baseline import GoldenBaseline
from ...evaluation import EvaluationBenchmark

@dataclass
class GoldenComparisonResult:
    outcome: ComparisonOutcome
    candidate_score: float
    golden_score: float
    global_delta: float
    dimension_deltas: Dict[str, float] = field(default_factory=dict)
    regressions: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    notes: str = ""

class GoldenComparator:
    """Compares candidate asset evaluation benchmarks against official Golden Baselines."""
    
    @classmethod
    def compare(
        cls,
        candidate_bench: EvaluationBenchmark,
        golden_baseline: GoldenBaseline,
        max_allowed_regression: float = 0.05
    ) -> GoldenComparisonResult:
        delta = round(candidate_bench.weighted_score - golden_baseline.global_score, 4)
        dim_deltas: Dict[str, float] = {}
        regressions: List[str] = []
        improvements: List[str] = []

        cand_dims = {k.value: v.score for k, v in candidate_bench.dimension_scores.items()}
        all_dims = set(cand_dims.keys()).union(set(golden_baseline.dimension_scores.keys()))

        for d in all_dims:
            c_score = cand_dims.get(d, 0.0)
            g_score = golden_baseline.dimension_scores.get(d, 0.0)
            d_delta = round(c_score - g_score, 4)
            dim_deltas[d] = d_delta

            if d_delta < -max_allowed_regression:
                regressions.append(f"{d} ({d_delta})")
            elif d_delta > 0.01:
                improvements.append(f"{d} (+{d_delta})")

        if len(regressions) > 0:
            outcome = ComparisonOutcome.REGRESSION
        elif delta > 0.001 or len(improvements) > 0:
            outcome = ComparisonOutcome.IMPROVEMENT
        elif delta >= -max_allowed_regression:
            outcome = ComparisonOutcome.PASS
        else:
            outcome = ComparisonOutcome.FAIL

        return GoldenComparisonResult(
            outcome=outcome,
            candidate_score=round(candidate_bench.weighted_score, 4),
            golden_score=round(golden_baseline.global_score, 4),
            global_delta=delta,
            dimension_deltas=dim_deltas,
            regressions=regressions,
            improvements=improvements,
            notes=f"Comparison evaluated against Golden Baseline v{golden_baseline.version}"
        )
