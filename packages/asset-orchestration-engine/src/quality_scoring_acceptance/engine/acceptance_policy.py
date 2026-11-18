from typing import Dict, List, Tuple
from ..core.scoring_types import AcceptanceStatus, QualityLevel, MetricCategory
from ..core.scoring_schema import QualityProfile

class AcceptancePolicy:
    @classmethod
    def evaluate_acceptance(
        cls,
        overall_score: float,
        category_scores: Dict[str, float],
        has_passed_hard_gates: bool,
        blocking_reasons: List[str],
        warnings: List[str],
        profile: QualityProfile
    ) -> Tuple[AcceptanceStatus, QualityLevel]:
        # 1. Hard Gate Violation
        if not has_passed_hard_gates or len(blocking_reasons) > 0:
            return AcceptanceStatus.REJECTED, QualityLevel.INVALID

        # 2. Category Minimums Check
        for cat, min_val in profile.category_minimums.items():
            cat_score = category_scores.get(cat.value, 100.0)
            if (cat_score / 100.0) < min_val:
                blocking_reasons.append(f"CATEGORY_BELOW_MINIMUM: [{cat.value}] {cat_score:.1f} < {min_val*100.0:.1f}")
                return AcceptanceStatus.REJECTED, QualityLevel.POOR

        # 3. Quality Level Mapping
        if overall_score >= 90.0:
            q_level = QualityLevel.EXCEPTIONAL
        elif overall_score >= 80.0:
            q_level = QualityLevel.PRODUCTION
        elif overall_score >= 70.0:
            q_level = QualityLevel.ACCEPTABLE
        elif overall_score >= 60.0:
            q_level = QualityLevel.MARGINAL
        else:
            q_level = QualityLevel.POOR

        # 4. Acceptance Thresholds Check
        if overall_score >= profile.acceptance_threshold:
            if len(warnings) > 0:
                return AcceptanceStatus.CONDITIONAL, q_level
            return AcceptanceStatus.ACCEPTED, q_level
        elif overall_score >= profile.conditional_threshold:
            return AcceptanceStatus.CONDITIONAL, q_level
        else:
            return AcceptanceStatus.REJECTED, q_level
