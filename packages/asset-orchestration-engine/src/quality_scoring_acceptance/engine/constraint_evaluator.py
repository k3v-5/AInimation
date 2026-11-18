from typing import List, Tuple
from ..core.scoring_types import ConstraintSeverity
from ..core.scoring_schema import QualityDefect

class ConstraintEvaluator:
    @classmethod
    def evaluate_constraints(cls, defects: List[QualityDefect]) -> Tuple[bool, List[str], List[str]]:
        blocking_reasons: List[str] = []
        warnings: List[str] = []

        for d in defects:
            if d.severity == ConstraintSeverity.CRITICAL or d.blocking:
                blocking_reasons.append(f"[{d.category.value}] {d.description} (Loc: {d.location})")
            elif d.severity in (ConstraintSeverity.MEDIUM, ConstraintSeverity.HIGH):
                warnings.append(f"[{d.category.value}] {d.description} (Loc: {d.location})")

        has_passed_hard_gates = len(blocking_reasons) == 0
        return has_passed_hard_gates, blocking_reasons, warnings
