from typing import Dict, Any, List, Optional, Tuple
from ..core.visual_goal_builder import VisualGoalSpec
from ..analyzers.proportion_analyzer import ProportionAnalyzer
from ..analyzers.component_detector import ComponentDetector
from ..qa.quality_scorer import QualityScorer, VerificationReport
from ..correction.correction_planner import VisualCorrectionPlanner

class VisualIntelligenceAPI:
    """
    Visual Intelligence & Asset Verification API (AOE v10)
    
    Principio Fundamental:
    BLENDER SUCCESS != ASSET SUCCESS
    ASSET SUCCESS = ASSET STATE MATCHES GOAL SPEC
    """
    def __init__(self):
        pass

    def build_goal_spec(
        self,
        category: str = "ONE_HANDED_MEDIEVAL_SWORD",
        target_proportions: Optional[Dict[str, Dict[str, float]]] = None,
        required_components: Optional[List[str]] = None,
        forbidden_components: Optional[List[str]] = None,
        hard_constraints: Optional[List[str]] = None
    ) -> VisualGoalSpec:
        return VisualGoalSpec(
            category=category,
            target_proportions=target_proportions or {"blade_ratio": {"target": 0.72, "min": 0.65, "max": 0.78}},
            required_components=required_components or ["blade", "guard", "grip", "pommel"],
            forbidden_components=forbidden_components or [],
            hard_constraints=hard_constraints or ["is_one_handed", "has_blade", "has_guard"]
        )

    def verify_asset(
        self,
        asset_id: str,
        component_dimensions: Dict[str, Tuple[float, float, float]],
        present_components: List[str],
        materials: Optional[Dict[str, Dict[str, Any]]] = None,
        goal_spec: Optional[VisualGoalSpec] = None
    ) -> VerificationReport:
        goal = goal_spec or self.build_goal_spec()
        hard_fails = []
        warnings = []
        evidence = {}
        metrics = {}

        # 1. Analizar Componentes
        comp_score, comp_ev, comp_fails = ComponentDetector.detect_components(present_components, goal)
        metrics["components"] = comp_score
        evidence["components"] = comp_ev
        hard_fails.extend(comp_fails)

        # 2. Analizar Proporciones
        prop_score, prop_ev, prop_fails = ProportionAnalyzer.analyze_proportions(component_dimensions, goal)
        metrics["proportion"] = prop_score
        evidence["proportion"] = prop_ev
        if prop_fails:
            warnings.extend(prop_fails)

        # 3. Analizar Materiales
        mat_score = 1.0
        if materials and goal.target_materials:
            for c_name, req_m in goal.target_materials.items():
                act_m = materials.get(c_name, {})
                if req_m.get("metallic") is not None and abs(req_m["metallic"] - act_m.get("metallic", 0.0)) > 0.3:
                    mat_score = 0.5
                    warnings.append(f"MATERIAL_METALLIC_MISMATCH: component '{c_name}' metallic is {act_m.get('metallic')} vs target {req_m['metallic']}.")
        metrics["material"] = mat_score

        # 4. Métricas base
        metrics["silhouette"] = 1.0 if prop_score >= 0.8 else 0.7
        metrics["color"] = 1.0
        metrics["style"] = 1.0
        metrics["geometry"] = 1.0

        return QualityScorer.calculate_score(asset_id, metrics, hard_fails, warnings, evidence)

    def plan_correction(self, report: VerificationReport) -> Dict[str, Any]:
        return VisualCorrectionPlanner.plan_minimal_correction(report)
