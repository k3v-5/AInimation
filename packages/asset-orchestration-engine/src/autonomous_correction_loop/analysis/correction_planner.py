import uuid
from typing import Dict, Any, List
from ...visual_reference_matching.core.reference_schema import ErrorMap
from ..core.loop_schema import CorrectionPlan, CorrectionStep

class CorrectionPlanner:
    @staticmethod
    def plan_corrections(error_map: ErrorMap, current_parameters: Dict[str, Any]) -> CorrectionPlan:
        steps: List[CorrectionStep] = []
        affected_comps = set()

        for disc in error_map.discrepancies:
            curr_val = float(current_parameters.get(disc.parameter_hint, disc.actual_value))
            rec_val = error_map.recommended_patches.get(disc.parameter_hint, disc.expected_value)
            steps.append(CorrectionStep(
                target_component=disc.component,
                parameter_name=disc.parameter_hint,
                current_value=curr_val,
                recommended_value=rec_val,
                operation="SET",
                reason=disc.description
            ))
            affected_comps.add(disc.component)

        scope = "SUBTREE" if len(affected_comps) > 1 else ("COMPONENT" if affected_comps else "PARAMETER")

        return CorrectionPlan(
            plan_id=f"cplan_{uuid.uuid4().hex[:6]}",
            steps=steps,
            affected_components=sorted(list(affected_comps)),
            rebuild_scope=scope,
            estimated_improvement=0.15 * len(steps)
        )
