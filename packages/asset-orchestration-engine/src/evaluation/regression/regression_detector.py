from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from ..models.evaluation_models import EvaluationBenchmark
from ..core.evaluation_types import DefectSeverity

@dataclass
class RegressionReport:
    has_regression: bool = False
    global_delta: float = 0.0
    regressed_dimensions: List[str] = field(default_factory=list)
    improved_dimensions: List[str] = field(default_factory=list)
    new_defects: List[str] = field(default_factory=list)
    critical_regression_detected: bool = False

class RegressionDetector:
    """Detects quality regressions and new defects against established baselines."""
    
    @classmethod
    def detect_regressions(cls, candidate: EvaluationBenchmark, baseline: EvaluationBenchmark) -> RegressionReport:
        delta = round(candidate.weighted_score - baseline.weighted_score, 4)
        report = RegressionReport(global_delta=delta)

        for dim, base_dim_score in baseline.dimension_scores.items():
            cand_dim_score = candidate.dimension_scores.get(dim)
            if not cand_dim_score:
                report.regressed_dimensions.append(f"{dim.value} (Missing in candidate)")
                report.has_regression = True
                continue

            dim_delta = round(cand_dim_score.score - base_dim_score.score, 4)
            if dim_delta < -0.01:
                report.regressed_dimensions.append(f"{dim.value} ({dim_delta})")
                report.has_regression = True
                if dim in candidate.evaluation_profile.critical_dimensions:
                    report.critical_regression_detected = True
            elif dim_delta > 0.01:
                report.improved_dimensions.append(f"{dim.value} (+{dim_delta})")

        # Detect new critical or major defects
        baseline_defect_ids = {d.defect_id for d in baseline.defects}
        for d in candidate.defects:
            if d.defect_id not in baseline_defect_ids:
                report.new_defects.append(f"[{d.severity.value}] {d.description}")
                if d.severity == DefectSeverity.CRITICAL or d.blocking:
                    report.critical_regression_detected = True
                    report.has_regression = True

        if delta < -0.01:
            report.has_regression = True

        return report

    @classmethod
    def check_regression(cls, rep_before: Any, rep_after: Any) -> Tuple[bool, str]:
        """Backward compatibility helper for visual evaluation QA."""
        score_before = getattr(rep_before, "overall_score", getattr(rep_before, "weighted_score", 0.0))
        score_after = getattr(rep_after, "overall_score", getattr(rep_after, "weighted_score", 0.0))
        
        # Check dimensional degradation
        dims_before = getattr(rep_before, "dimension_scores", {})
        dims_after = getattr(rep_after, "dimension_scores", {})
        
        for d, s_bef in dims_before.items():
            s_aft = dims_after.get(d, s_bef)
            val_bef = getattr(s_bef, "score", s_bef) if not isinstance(s_bef, (int, float)) else s_bef
            val_aft = getattr(s_aft, "score", s_aft) if not isinstance(s_aft, (int, float)) else s_aft
            if val_aft < val_bef - 0.05:
                return True, f"Dimension {d} degraded from {val_bef} to {val_aft}"

        if score_after < score_before - 0.01:
            return True, f"Overall score dropped from {score_before} to {score_after}"
        return False, "No regression detected"
