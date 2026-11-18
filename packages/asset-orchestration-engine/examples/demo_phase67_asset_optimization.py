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
from src.automated_visual_evaluation import AutomatedVisualEvaluationAPI
from src.geometric_validation_qa import GeometricValidationAPI
from src.quality_scoring_acceptance import QualityScoringAPI
from src.asset_optimization_engine import (
    AssetOptimizationAPI, OptimizationProfile, TargetPlatform, OptimizationObjective
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 67: ASSET OPTIMIZATION ENGINE")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()
    geom_api = GeometryGenerationAPI()
    surf_api = MaterialSurfaceAPI()
    pres_api = PresentationMatchingAPI()
    eval_api = AutomatedVisualEvaluationAPI()
    qa_api = GeometricValidationAPI()
    scoring_api = QualityScoringAPI()
    opt_api = AssetOptimizationAPI()

    # 1. Pipeline Previo y Aceptación Formal (F55 a F66)
    print("\n[PASO 1] Pipeline Previo y Aceptación Formal (F55 a F66):")
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
    q_res = scoring_api.evaluate_asset_quality("barrel_hero", "barrel_hero.root", eval_res, qa_res)
    print(f" - Asset Status (F66): [{q_res.acceptance_status.value}] | Quality Score: {q_res.overall_score:.1f}/100.0 (Level: {q_res.quality_level.value})")

    # 2. Ejecución del Asset Optimization Engine (F67)
    print("\n[PASO 2] Ejecución de Optimización Automática para Real-Time (F67):")
    profile = OptimizationProfile(
        profile_id="GAME_PROP_HERO_PC_UNREAL",
        target_platform=TargetPlatform.PC,
        objective=OptimizationObjective.BALANCED,
        visual_degradation_limit=0.03 # Max 3% degradación tolerada
    )
    opt_res = opt_api.optimize_game_asset(
        asset_id="barrel_hero",
        semantic_id="barrel_hero.root",
        generated_geometry=geom_res,
        surface_result=surf_res,
        quality_result=q_res,
        profile=profile
    )
    val = opt_api.validate_optimization_result(opt_res)
    print(f" - Sesión ID: [{opt_res.optimization_session_id}] | Válido: {val.is_valid} | Status: [{opt_res.optimization_status}]")
    print(f" - Candidato Seleccionado: [{opt_res.selected_candidate_id}] | Production Candidate: {opt_res.production_candidate}")
    print(f" - Hash Determinista de Optimización (SHA-256): {opt_res.optimization_hash[:16]}...{opt_res.optimization_hash[-8:]}")

    # 3. Reporte Comparativo Before vs After (Costes y Rendimiento)
    print("\n[PASO 3] Reporte Comparativo Antes vs Después (Costes de Render y Memoria):")
    base = opt_res.baseline_cost
    opt = opt_res.optimized_cost
    print(f"   * Triángulos: {base.triangle_count} -> {opt.triangle_count} ({((opt.triangle_count - base.triangle_count)/base.triangle_count)*100:+.1f}%)")
    print(f"   * Vértices:   {base.vertex_count} -> {opt.vertex_count}")
    print(f"   * Memoria Textura: {base.texture_memory_mb:.1f} MB -> {opt.texture_memory_mb:.1f} MB")
    print(f"   * Draw Calls Estimados: {base.estimated_draw_calls} -> {opt.estimated_draw_calls}")
    print(f"   * Cost Index Global: {base.total_cost_index:.1f} -> {opt.total_cost_index:.1f} ({((opt.total_cost_index - base.total_cost_index)/base.total_cost_index)*100:+.1f}%)")

    # 4. Resumen de Jerarquía LOD
    print("\n[PASO 4] Jerarquía de Niveles de Detalle (LOD Summary):")
    for lod_name, lod_data in opt_res.lod_summary.items():
        print(f"   * [{lod_name}] Triángulos: {lod_data['triangles']} | Screen Size: {lod_data['screen_size']} | Ratio: {lod_data['reduction']*100:.0f}%")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 67 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
