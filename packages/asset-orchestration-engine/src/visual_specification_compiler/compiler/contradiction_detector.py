from typing import List, Dict, Any
from ..core.vas_types import ContradictionSeverity
from ..core.vas_schema import ContradictionReport

class ContradictionDetector:
    @classmethod
    def detect_contradictions(
        cls,
        prompt: str,
        project_constraints: Dict[str, Any],
        visual_requirements: Dict[str, Any]
    ) -> List[ContradictionReport]:
        reports = []
        p_low = prompt.lower()

        # 1. Conflicto de Alto Detalle vs Presupuesto Poligonal Extremo
        poly_budget = project_constraints.get("poly_budget", 15000)
        tri_budget = project_constraints.get("triangle_budget", 30000)
        
        if ("highly detailed" in p_low or "alto detalle" in p_low or "ultra detailed" in p_low) and (poly_budget <= 500 or tri_budget <= 1000):
            reports.append(ContradictionReport(
                contradiction_id="CONTR_DETAIL_VS_POLY_BUDGET",
                conflicting_requirements=["Prompt: 'highly detailed'", f"ProjectConstraint: triangle_budget={tri_budget}"],
                description="High detail requirement directly contradicts extremely constrained polygon budget.",
                severity=ContradictionSeverity.CRITICAL,
                recommended_resolution="Bake high-poly detail into normal/tangent maps while keeping base mesh within polygon budget."
            ))

        # 2. Conflicto de Material / Estilo
        if ("cartoon" in p_low or "plastic" in p_low) and visual_requirements.get("base_material") == "IRON":
            reports.append(ContradictionReport(
                contradiction_id="CONTR_STYLE_MATERIAL_MISMATCH",
                conflicting_requirements=["Prompt: 'cartoon plastic'", "VisualReference: 'IRON'"],
                description="Stylized cartoon plastic requested in prompt clashes with observed realistic iron reference.",
                severity=ContradictionSeverity.HIGH,
                recommended_resolution="Prioritize explicit prompt directive over background visual reference."
            ))

        return reports
