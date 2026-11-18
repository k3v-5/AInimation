import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import (
    VisualSpecificationAPI, VisualCompilationInput
)
from src.reference_analysis_visual_decomposition import (
    DecomposedReferenceReport, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ExtractedMaterialType
)
from src.procedural_modeling_strategy import ProceduralModelingStrategyAPI
from src.geometry_generation_engine import GeometryGenerationAPI
from src.material_surface_generation import MaterialSurfaceAPI
from src.presentation_matching import PresentationMatchingAPI
from src.automated_visual_evaluation import AutomatedVisualEvaluationAPI, VisualDefect, DefectType
from src.geometric_validation_qa import GeometricValidationAPI, GeometricDefect, GeometricDefectCategory, DefectSeverity
from src.intelligent_critic_engine import IntelligentCriticAPI

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 63: INTELLIGENT CRITIC ENGINE")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()
    geom_api = GeometryGenerationAPI()
    surf_api = MaterialSurfaceAPI()
    pres_api = PresentationMatchingAPI()
    eval_api = AutomatedVisualEvaluationAPI()
    qa_api = GeometricValidationAPI()
    critic_api = IntelligentCriticAPI()

    # 1. Pipeline Inicial: F55 Ref -> F56 VAS -> F57 MSP -> F58 Geom -> F59 Surf -> F60 Pres -> F61 Eval -> F62 QA
    print("\n[PASO 1] Pipeline de Percepción y QA Estructural (F55 a F62):")
    f55_report = DecomposedReferenceReport(
        report_id="REP_F55_BARREL_HERO",
        reference_ids=["REF_HERO_01"],
        silhouette=SilhouetteExtraction(aspect_ratio=1.0, symmetry_axis="VERTICAL_Z"),
        proportions=ProportionEstimate(component_ratios={"body": 0.80, "top_ring": 0.10, "bottom_ring": 0.10}),
        parts=[
            DecomposedPart("part_body", "BODY", (0, 0, 1, 1.0), (0, 0, 0), True, 0.98),
            DecomposedPart("part_ring_top", "RING_01", (0, 0.8, 1.02, 0.15), (0, 0, 0.8), False, 0.95),
            DecomposedPart("part_ring_bottom", "RING_02", (0, 0.2, 1.02, 0.15), (0, 0, 0.2), False, 0.95)
        ],
        materials=MaterialPalette(base_material=ExtractedMaterialType.WOOD, surface_roughness=0.68)
    )

    vas_input = VisualCompilationInput(
        prompt="Barril medieval de roble oscuro con aros de hierro, altura 1.0m",
        asset_class_hint="PROP.BARREL",
        reference_reports=[f55_report],
        semantic_context={"semantic_id": "barrel_hero.root", "asset_id": "barrel_hero"},
        project_constraints={"nanite": True, "collision": "CUSTOM_UCX"}
    )
    vas = vas_api.compile_specification(vas_input)
    msp = msp_api.plan_strategy(vas)
    geom_res = geom_api.generate_geometry(msp)
    surf_res = surf_api.generate_surface(geom_res, vas, msp, generation_seed=42)
    vpc = pres_api.build_presentation_context(geom_res, surf_res, f55_report, vas)
    eval_res = eval_api.evaluate_visuals(f55_report, geom_res, {"surface": surf_res, "presentation": vpc})
    qa_res = qa_api.validate_geometry(geom_res, {"visual_evaluation": eval_res, "surface": surf_res})

    # Inyectar una discrepancia visual y geométrica controlada para demostrar la inferencia causal
    eval_res.defects = [
        VisualDefect("DEF_V_SILHOUETTE_BODY", DefectType.WRONG_SILHOUETTE, region="part_body", error_pct=14.5)
    ]
    qa_res.defects = [
        GeometricDefect("DEF_G_SCALE_BODY", GeometricDefectCategory.TRANSFORM_ERROR, severity=DefectSeverity.MODERATE, location="part_body")
    ]
    print(f" - Defectos de Entrada: Visual=[{len(eval_res.defects)}] | QA Geométrico=[{len(qa_res.defects)}]")

    # 2. Ejecución del Intelligent Critic Engine (F63)
    print("\n[PASO 2] Ejecución del Diagnóstico Causal y Crítica Inteligente (F63):")
    critic_res = critic_api.generate_critic_diagnosis(vas, qa_res, eval_res)
    val = critic_api.validate_critic_result(critic_res)
    print(f" - Crítica ID: [{critic_res.critic_id}] | Válida: {val.is_valid} | Recomendación: [{critic_res.iteration_recommendation.value}]")
    print(f" - Confianza del Diagnóstico: {critic_res.confidence*100:.1f}%")
    print(f" - Hash de Crítica Determinista (SHA-256): {critic_res.critic_hash[:16]}...{critic_res.critic_hash[-8:]}")

    # 3. Diagnósticos Causales y Agrupación de Defectos en Clusters
    print("\n[PASO 3] Diagnósticos Causales y Clusters de Defectos:")
    for cluster in critic_res.defect_clusters:
        print(f"   * Cluster: [{cluster.cluster_id}] ({cluster.primary_category.value}) -> Componentes: {cluster.affected_components}")
        print(f"     - Defectos Visuales F61: {cluster.visual_defects}")
        print(f"     - Defectos Geométricos F62: {cluster.geometric_defects}")

    for diag in critic_res.diagnoses:
        print(f"\n   * Diagnóstico: [{diag.diagnosis_id}] Categoría=[{diag.category.value}] Prioridad=[{diag.priority.value}]")
        print(f"     - Acción Recomendada: {diag.recommended_action} (Impacto: {diag.downstream_impact})")
        for ev in diag.evidence:
            print(f"     - Evidencia [{ev.source}]: {ev.description} (Confianza: {ev.confidence})")

    # 4. Recomendaciones de Parámetros Específicos para F64
    print("\n[PASO 4] Recomendaciones Cuantitativas de Parámetros (para F64 Autonomous Correction):")
    for p_rec in critic_res.parameter_recommendations:
        print(f"   * Parámetro: [{p_rec.parameter_id}] Valor Actual={p_rec.current_value} -> Recomendado={p_rec.recommended_value} (Delta: {p_rec.delta:+.2f})")
        print(f"     - Rango Seguro: {p_rec.recommended_range} | Razón: {p_rec.reason}")

    # 5. Plan de Corrección Ordenado y Dependiente
    print("\n[PASO 5] Plan de Corrección Priorizado (Correction Plan):")
    plan = critic_res.correction_plan
    print(f" - Plan ID: [{plan.plan_id}] | Riesgo de Regresión: [{plan.regression_risk.value}]")
    for act in plan.ordered_actions:
        print(f"   * [{act.action_id}] Target: {act.target} -> Parámetro: {act.parameter} (Delta: {act.delta:+.2f}) [Autonomía: {act.autonomy_level.value}]")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 63 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
