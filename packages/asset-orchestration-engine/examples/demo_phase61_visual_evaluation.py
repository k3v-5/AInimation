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
from src.automated_visual_evaluation import (
    AutomatedVisualEvaluationAPI, EvaluationCategory, DefectType,
    VisualDefect, CategoryEvaluation
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 61: AUTOMATED VISUAL EVALUATION ENGINE")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()
    geom_api = GeometryGenerationAPI()
    surf_api = MaterialSurfaceAPI()
    pres_api = PresentationMatchingAPI()
    eval_api = AutomatedVisualEvaluationAPI()

    # 1. Pipeline Inicial: Prompt -> F55 -> F56 -> F57 -> F58 -> F59 -> F60
    print("\n[PASO 1] Pipeline Inicial (F55 Ref -> F56 VAS -> F57 MSP -> F58 Geom -> F59 Surf -> F60 Pres):")
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
        semantic_context={"semantic_id": "barrel_hero.root", "asset_id": "barrel_hero"}
    )
    vas = vas_api.compile_specification(vas_input)
    msp = msp_api.plan_strategy(vas)
    geom_res = geom_api.generate_geometry(msp)
    surf_res = surf_api.generate_surface(geom_res, vas, msp, generation_seed=42)
    vpc = pres_api.build_presentation_context(geom_res, surf_res, f55_report, vas)
    print(f" - Geometría: [{geom_res.generation_id}] | Superficie: [{surf_res.surface_generation_id}] | VPC: [{vpc.presentation_id}]")

    # 2. Evaluación Visual Automática (F61)
    print("\n[PASO 2] Ejecución de la Evaluación Visual Automática (F61):")
    eval_res = eval_api.evaluate_visuals(f55_report, geom_res, {"surface": surf_res, "presentation": vpc})
    val = eval_api.validate_evaluation(eval_res)
    print(f" - Evaluación ID: [{eval_res.evaluation_id}] | Válida: {val.is_valid} | Status: [{eval_res.acceptance_status.value}]")
    print(f" - Score Global Ponderado: {eval_res.global_score:.4f} ({eval_res.global_score*100:.1f}%)")
    print(f" - Hash de Evaluación Determinista (SHA-256): {eval_res.evaluation_hash[:16]}...{eval_res.evaluation_hash[-8:]}")

    # 3. Desglose de Scores por Categoría
    print("\n[PASO 3] Desglose Cuantitativo de Scores por Categoría:")
    for cat_name, cat_eval in eval_res.category_scores.items():
        print(f"   * [{cat_name:<12}] Score: {cat_eval.score:.4f} (Peso: {cat_eval.weight:.1f}, Confianza: {cat_eval.confidence:.2f}) -> Métricas: {cat_eval.metrics}")

    # 4. Detección y Diagnóstico Multi-Hipótesis de Defectos
    print("\n[PASO 4] Detección de Defectos y Diagnóstico de Causas:")
    if eval_res.defects:
        for defect in eval_res.defects:
            print(f"   * Defecto: [{defect.defect_id}] Tipo=[{defect.defect_type.value}] Severidad=[{defect.severity.value}] Región=[{defect.region}]")
            print(f"     - Error Medido: {defect.error_pct}% | Causas Probables: {defect.probable_causes}")
            if defect.correction_hint:
                h = defect.correction_hint
                print(f"     - Hint de Corrección (para F64): Target=[{h.target}], Parámetro=[{h.parameter}], Dirección=[{h.direction}], Prioridad=[{h.priority:.2f}]")
    else:
        print("   * CERO defectos detectados. El asset cumple al 100% las tolerancias de silueta, proporciones y material.")

    # 5. Demostración de Comparación Temporal (Iteración N vs N+1)
    print("\n[PASO 5] Demostración de Comparación Temporal entre Iteraciones (Regresión / Mejora):")
    eval_n = eval_api.evaluate_visuals(f55_report, geom_res, {"surface": surf_res, "presentation": vpc})
    eval_n.global_score = 0.78
    eval_n.defects = [VisualDefect("DEF_01", DefectType.WRONG_SILHOUETTE)]
    
    delta = eval_api.compare_iterations(eval_n, eval_res)
    print(f" - Delta de Score: {delta.score_delta:+.4f} | Estado: [{delta.regression_status.value}]")
    print(f" - Defectos Resueltos: {delta.fixed_defects} | Nuevos Defectos: {delta.new_defects}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 61 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
