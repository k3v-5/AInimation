from typing import List, Dict, Any
from ..core.critic_types import (
    CriticPriority, RiskLevel, ActionAutonomyLevel
)
from ..core.critic_schema import (
    CorrectionAction, CorrectionPlan, CriticDiagnosis, ParameterRecommendation
)

class CorrectionPlanner:
    @classmethod
    def build_plan(
        cls,
        diagnoses: List[CriticDiagnosis],
        param_recs: List[ParameterRecommendation],
        context: Dict[str, Any]
    ) -> CorrectionPlan:
        actions: List[CorrectionAction] = []

        # 1. Priorizar diagnósticos: CRITICAL > HIGH > MEDIUM > LOW
        priority_order_map = {
            CriticPriority.CRITICAL: 0,
            CriticPriority.HIGH: 1,
            CriticPriority.MEDIUM: 2,
            CriticPriority.LOW: 3,
            CriticPriority.INFO: 4
        }
        sorted_diags = sorted(diagnoses, key=lambda d: priority_order_map.get(d.priority, 5))

        for idx, d in enumerate(sorted_diags):
            target_comp = d.affected_components[0] if d.affected_components else "mesh.root"
            param_name = "scale" if d.category.value == "TRANSFORM" else "geometry_param"

            act = CorrectionAction(
                action_id=f"ACT_{idx+1:03d}_{d.category.value}",
                target=f"component.{target_comp}",
                parameter=param_name,
                current_value=1.15,
                proposed_value=1.00,
                delta=-0.15,
                reason=f"Correct {d.category.value} via {d.recommended_action}",
                evidence=[e.description for e in d.evidence],
                expected_improvement=0.18,
                risk=RiskLevel.LOW,
                autonomy_level=ActionAutonomyLevel.AUTONOMOUSLY_ACTIONABLE,
                dependencies=[]
            )
            actions.append(act)

        plan = CorrectionPlan(
            plan_id="PLAN_CAUSAL_CORRECTION_V63",
            ordered_actions=actions,
            expected_effect="RESTORE_STRUCTURAL_AND_PERCEPTUAL_ALIGNMENT",
            confidence=0.95,
            estimated_cost=float(len(actions)),
            regression_risk=RiskLevel.LOW,
            dependencies={}
        )
        return plan
