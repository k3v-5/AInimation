from typing import Dict, Any, List
from ..core.critic_types import (
    CausalCategory, CriticPriority, EvidenceType, RiskLevel
)
from ..core.critic_schema import (
    CriticDiagnosis, RootCause, EvidenceItem, CriticConfiguration
)
from .base_rule import ICriticRule

class ProportionCausalRule(ICriticRule):
    @property
    def rule_id(self) -> str:
        return "RULE_CAUSAL_PROPORTION"

    @property
    def category(self) -> CausalCategory:
        return CausalCategory.PROPORTION

    def evaluate(
        self,
        context: Dict[str, Any],
        config: CriticConfiguration
    ) -> List[CriticDiagnosis]:
        diagnoses: List[CriticDiagnosis] = []
        v_eval = context.get("visual_evaluation")
        g_val = context.get("geometry_validation")

        v_defects = getattr(v_eval, "defects", []) if v_eval else []
        sil_defs = [d for d in v_defects if getattr(d, "defect_type", "") in ["WRONG_SILHOUETTE", "WRONG_PROPORTION"]]

        for d in sil_defs:
            d_region = getattr(d, "region", "root")
            d_error = getattr(d, "error_pct", 10.0)

            ev = [
                EvidenceItem(
                    evidence_type=EvidenceType.VISUAL_EVIDENCE,
                    source="F61_VISUAL_EVAL",
                    description=f"Silhouette/Proportion error measured: {d_error}% in region [{d_region}]",
                    metric_value=d_error,
                    confidence=0.95
                )
            ]

            root_c = RootCause(
                cause_id=f"CAUSE_PROPORTION_{d_region.upper()}",
                category=CausalCategory.GEOMETRY_PARAMETER,
                description=f"Component [{d_region}] parameter scaling exceeds target silhouette bounds.",
                evidence=ev,
                probability=0.92,
                affected_components=[d_region],
                related_parameters=[f"{d_region}_width", f"{d_region}_scale"],
                correction_candidates=[f"REDUCE_{d_region.upper()}_WIDTH"]
            )

            diag = CriticDiagnosis(
                diagnosis_id=f"DIAG_PROP_{d_region.upper()}",
                category=CausalCategory.PROPORTION,
                severity="MAJOR" if d_error > 15.0 else "MODERATE",
                priority=CriticPriority.HIGH,
                affected_components=[d_region],
                affected_regions=[d_region],
                evidence=ev,
                probable_causes=[root_c],
                confidence=0.95,
                downstream_impact="SILHOUETTE_MISMATCH",
                recommended_action=f"ADJUST_PARAMETER_{d_region.upper()}_WIDTH"
            )
            diagnoses.append(diag)

        return diagnoses

class TopologyCausalRule(ICriticRule):
    @property
    def rule_id(self) -> str:
        return "RULE_CAUSAL_TOPOLOGY"

    @property
    def category(self) -> CausalCategory:
        return CausalCategory.TOPOLOGY

    def evaluate(
        self,
        context: Dict[str, Any],
        config: CriticConfiguration
    ) -> List[CriticDiagnosis]:
        diagnoses: List[CriticDiagnosis] = []
        g_val = context.get("geometry_validation")
        g_defects = getattr(g_val, "defects", []) if g_val else []

        top_defs = [d for d in g_defects if getattr(getattr(d, "category", None), "value", "") in ["NON_MANIFOLD", "DEGENERATE_GEOMETRY"]]

        for d in top_defs:
            cat_val = getattr(getattr(d, "category", None), "value", "TOPOLOGY")
            d_id = getattr(d, "defect_id", "DEF_TOP")

            ev = [
                EvidenceItem(
                    evidence_type=EvidenceType.GEOMETRIC_EVIDENCE,
                    source="F62_GEOMETRY_QA",
                    description=f"Topological integrity failure: {cat_val}",
                    metric_value=getattr(d, "measurement", ""),
                    confidence=0.99
                )
            ]

            root_c = RootCause(
                cause_id=f"CAUSE_TOPOLOGY_{cat_val}",
                category=CausalCategory.TOPOLOGY,
                description=f"Mesh topology violated manifold/degeneracy constraints in {getattr(d, 'location', 'mesh')}",
                evidence=ev,
                probability=0.98,
                affected_components=[getattr(d, "location", "mesh")],
                correction_candidates=["REPAIR_BOUNDARY_OR_MERGE_VERTICES"]
            )

            diag = CriticDiagnosis(
                diagnosis_id=f"DIAG_TOP_{d_id}",
                category=CausalCategory.TOPOLOGY,
                severity="CRITICAL",
                priority=CriticPriority.CRITICAL,
                affected_components=[getattr(d, "location", "mesh")],
                affected_regions=[getattr(d, "location", "mesh")],
                evidence=ev,
                probable_causes=[root_c],
                confidence=0.99,
                downstream_impact="BLOCKS_UNREAL_EXPORT_AND_NANITE",
                recommended_action="REPAIR_TOPOLOGY"
            )
            diagnoses.append(diag)

        return diagnoses
