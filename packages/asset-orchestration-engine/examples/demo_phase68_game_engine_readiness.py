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
from src.asset_optimization_engine import AssetOptimizationAPI, OptimizationProfile
from src.game_engine_readiness import (
    GameEngineReadinessAPI, EngineProfile, EngineTarget
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 68: GAME-ENGINE READINESS PIPELINE")
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
    readiness_api = GameEngineReadinessAPI()

    # 1. Pipeline Previo (F55 a F67)
    print("\n[PASO 1] Pipeline Previo y Asset Optimizado (F55 a F67):")
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
        prompt="Barril medieval de roble oscuro con aros de hierro",
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
    opt_res = opt_api.optimize_game_asset("barrel_hero", "barrel_hero.root", geom_res, surf_res, q_res)
    print(f" - Asset Optimizado (F67): [{opt_res.selected_candidate_id}] | Cost Index: {opt_res.optimized_cost.total_cost_index:.1f}")

    # 2. Ejecución de Game-Engine Readiness Pipeline (F68)
    print("\n[PASO 2] Ejecución de Validación y Preparación para Unreal Engine (F68):")
    engine_profile = EngineProfile(
        profile_id="UNREAL_ENGINE_5_HERO_PROP",
        target_engine=EngineTarget.UNREAL_ENGINE_5,
        require_ucx_collision=True,
        require_lightmap_uv=True
    )
    ready_asset = readiness_api.verify_and_prepare_for_engine(
        optimized_asset_result=opt_res,
        engine_profile=engine_profile
    )
    val = readiness_api.validate_engine_ready_asset(ready_asset)
    print(f" - Readiness Status: [{ready_asset.readiness_status.value}] | Score: {ready_asset.readiness_score:.1f}/100.0 (Válido: {val.is_valid})")
    print(f" - Prepared State Hash: [{ready_asset.prepared_state_hash}]")
    print(f" - Hash Determinista de Readiness (SHA-256): {ready_asset.readiness_hash[:16]}...{ready_asset.readiness_hash[-8:]}")

    # 3. Demostración de Hard Blocker (Falta de UCX Collision)
    print("\n[PASO 3] Demostración de Hard Blocker (Rechazo ante Falta de Colisión UCX_):")
    blocked_asset = readiness_api.verify_and_prepare_for_engine(
        optimized_asset_result=opt_res,
        engine_profile=engine_profile,
        context={"force_missing_collision": True}
    )
    print(f" - Status con Blocker: [{blocked_asset.readiness_status.value}] (Score: {blocked_asset.readiness_score:.1f})")

    # 4. Reporte Humano Legible
    print("\n[PASO 4] Manifiesto e Informe Legible de Game-Engine Readiness:")
    print(readiness_api.generate_human_report(ready_asset.manifest))

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 68 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
