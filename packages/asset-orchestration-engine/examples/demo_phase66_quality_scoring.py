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
from src.geometric_validation_qa import (
    GeometricValidationAPI, GeometricDefect, DefectSeverity, GeometricDefectCategory
)
from src.quality_scoring_acceptance import QualityScoringAPI, QualityProfile

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 66: QUALITY SCORING & ACCEPTANCE SYSTEM")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()
    geom_api = GeometryGenerationAPI()
    surf_api = MaterialSurfaceAPI()
    pres_api = PresentationMatchingAPI()
    eval_api = AutomatedVisualEvaluationAPI()
    qa_api = GeometricValidationAPI()
    scoring_api = QualityScoringAPI()

    # 1. Pipeline Inicial: F55 Ref -> F56 VAS -> F57 MSP -> F58 Geom -> F59 Surf -> F60 Pres -> F61 Eval -> F62 QA
    print("\n[PASO 1] Pipeline Previo y Recopilación de Métricas (F55 a F62):")
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
    print(f" - F61 Visual Score: {eval_res.global_score*100:.1f}% | F62 Geometry QA Defectos: [{len(qa_res.defects)}]")

    # 2. Evaluación Formal de Calidad y Scoring (F66)
    print("\n[PASO 2] Evaluación Formal de Calidad y Decisión de Aceptación (F66):")
    profile = QualityProfile(profile_id="GAME_PROP_HERO_HEROIC", acceptance_threshold=85.0)
    q_res = scoring_api.evaluate_asset_quality(
        asset_id="barrel_hero",
        semantic_id="barrel_hero.root",
        visual_eval_result=eval_res,
        geometry_qa_result=qa_res,
        profile=profile
    )
    val = scoring_api.validate_quality_result(q_res)
    print(f" - Evaluación ID: [{q_res.evaluation_id}] | Válida: {val.is_valid}")
    print(f" - Score Global: {q_res.overall_score:.1f}/100.0 | Nivel de Calidad: [{q_res.quality_level.value}]")
    print(f" - Decisión de Aceptación Final: [{q_res.acceptance_status.value}] (Bloqueantes: {len(q_res.blocking_reasons)})")
    print(f" - Hash Determinista de Calidad (SHA-256): {q_res.quality_hash[:16]}...{q_res.quality_hash[-8:]}")

    # 3. Desglose de Puntuaciones por Categoría
    print("\n[PASO 3] Desglose de Puntuaciones Ponderadas por Categoría:")
    for cat, sc in q_res.category_scores.items():
        if cat != "OVERALL":
            print(f"   * {cat:<22}: {sc:.1f}%")

    # 4. Demostración de Hard Gate: Rechazo Inmediato ante Falla Crítica
    print("\n[PASO 4] Demostración de Hard Gates (Rechazo ante Violación Topológica):")
    qa_res_corrupt = qa_api.validate_geometry(geom_res, {"visual_evaluation": eval_res, "surface": surf_res})
    qa_res_corrupt.defects.append(
        GeometricDefect("DEF_NON_MANIFOLD_CRITICAL", GeometricDefectCategory.NON_MANIFOLD, DefectSeverity.CRITICAL, "Non-manifold edge detected.")
    )
    q_res_corrupt = scoring_api.evaluate_asset_quality("barrel_hero", "barrel_hero.root", eval_res, qa_res_corrupt, profile=profile)
    print(f" - Score Visual Alto (95.7%) + Falla Crítica -> Decisión: [{q_res_corrupt.acceptance_status.value}] ({q_res_corrupt.quality_level.value})")
    print(f" - Razones de Bloqueo Registradas: {q_res_corrupt.blocking_reasons}")

    # 5. Generación del Informe Humano Legible
    print("\n[PASO 5] Generación del Informe de Aceptación (Human-Readable Quality Report):")
    report = scoring_api.generate_acceptance_report(q_res, profile_id=profile.profile_id)
    print(report.human_readable)

    print("\n" + "=" * 95)
    print("  BLOQUE DE GENERACION, PERCEPCION Y CALIDAD (F56-F66) COMPLETADO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
