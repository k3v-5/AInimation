from typing import List, Dict, Any, Tuple
from ..core.critic_types import CausalCategory
from ..core.critic_schema import RootCause, ParameterRecommendation, CriticDiagnosis

class RootCauseAnalyzer:
    @classmethod
    def analyze_causes_and_parameters(
        cls,
        diagnoses: List[CriticDiagnosis],
        context: Dict[str, Any]
    ) -> Tuple[List[RootCause], List[ParameterRecommendation]]:
        all_causes: List[RootCause] = []
        param_recs: List[ParameterRecommendation] = []

        for diag in diagnoses:
            for c in diag.probable_causes:
                all_causes.append(c)
                for p in c.related_parameters:
                    # Recommendation delta
                    p_rec = ParameterRecommendation(
                        parameter_id=p,
                        current_value=1.15,
                        recommended_value=1.00,
                        recommended_range=(0.98, 1.02),
                        min_value=0.5,
                        max_value=2.0,
                        delta=-0.15,
                        confidence=c.probability,
                        reason=f"Resolve {diag.category.value} deviation ({diag.diagnosis_id})",
                        evidence=[e.description for e in c.evidence]
                    )
                    param_recs.append(p_rec)

        return all_causes, param_recs
