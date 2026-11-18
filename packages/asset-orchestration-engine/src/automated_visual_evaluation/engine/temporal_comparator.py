from typing import List, Dict, Any
from ..core.evaluation_types import RegressionStatus
from ..core.evaluation_schema import VisualEvaluationResult, EvaluationDelta

class TemporalComparator:
    @classmethod
    def compare_evaluations(
        cls,
        previous_eval: VisualEvaluationResult,
        current_eval: VisualEvaluationResult
    ) -> EvaluationDelta:
        score_delta = round(current_eval.global_score - previous_eval.global_score, 4)

        prev_defect_types = {d.defect_type for d in previous_eval.defects}
        curr_defect_types = {d.defect_type for d in current_eval.defects}

        fixed = [d.value for d in prev_defect_types if d not in curr_defect_types]
        new_defs = [d.value for d in curr_defect_types if d not in prev_defect_types]

        if fixed and new_defs:
            status = RegressionStatus.MIXED
        elif new_defs:
            status = RegressionStatus.REGRESSION
        elif fixed or score_delta > 0.02:
            status = RegressionStatus.IMPROVEMENT
        elif score_delta < -0.02:
            status = RegressionStatus.REGRESSION
        else:
            status = RegressionStatus.UNCHANGED

        return EvaluationDelta(
            previous_eval_id=previous_eval.evaluation_id,
            current_eval_id=current_eval.evaluation_id,
            score_delta=score_delta,
            fixed_defects=fixed,
            new_defects=new_defs,
            regression_status=status
        )
