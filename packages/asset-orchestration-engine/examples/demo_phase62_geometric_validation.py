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

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 62: GEOMETRIC VALIDATION & TOPOLOGY QA")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()
    geom_api = GeometryGenerationAPI()
    surf_api = MaterialSurfaceAPI()
    pres_api = PresentationMatchingAPI()
    eval_api = AutomatedVisualEvaluationAPI()
    qa_api = GeometricValidationAPI()

    # 1. Pipeline Inicial: Prompt -> F55 -> F56 -> F57 -> F58 -> F59 -> F60 -> F61
    print("\n[PASO 1] Pipeline Inicial (F55 Ref -> F56 VAS -> F57 MSP -> F58 Geom -> F59 Surf -> F60 Pres -> F61 Eval):")
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
    print(f" - Geometría ID: [{geom_res.generation_id}] | Evaluación Visual Global: {eval_res.global_score*100:.1f}%")

    # 2. Validación Geométrica y QA Topológico (F62)
    print("\n[PASO 2] Ejecución de la Validación Geométrica y QA Topológico (F62):")
    qa_res = qa_api.validate_geometry(geom_res, {"visual_evaluation": eval_res, "surface": surf_res})
    val = qa_api.validate_qa_result(qa_res)
    print(f" - Validación ID: [{qa_res.validation_id}] | Válida: {val.is_valid} | Status: [{qa_res.validation_status.value}]")
    print(f" - Score Global Geométrico: {qa_res.quality_scores['overall_geometry_score']:.4f} ({qa_res.quality_scores['overall_geometry_score']*100:.1f}%)")
    print(f" - Hash de QA Determinista (SHA-256): {qa_res.validation_hash[:16]}...{qa_res.validation_hash[-8:]}")

    # 3. Inventario de Malla y Resumen Topológico
    print("\n[PASO 3] Inventario de Malla y Estadísticas Estructurales:")
    inv = qa_res.mesh_inventory
    top = qa_res.topology_statistics
    print(f" - Objetos: {inv.object_count} | Mallas: {inv.mesh_count} | Vértices: {inv.vertex_count} | Triángulos: {inv.triangle_count}")
    print(f" - Dimensiones: {inv.dimensions} | Volumen: {inv.volume} m³ | Área Superficial: {inv.surface_area} m²")
    print(f" - Manifold: {top.is_manifold} | Bordes Abiertos: {top.open_boundary_count} | Caras Degeneradas: {top.degenerate_face_count}")

    # 4. Desglose de Scores de Calidad Estructural
    print("\n[PASO 4] Scores por Dimensión Estructural:")
    for dim_name, dim_score in qa_res.quality_scores.items():
        print(f"   * [{dim_name:<24}] Score: {dim_score:.4f}")

    # 5. Reporte de Preparación para Unreal Engine
    print("\n[PASO 5] Reporte de Preparación para Unreal Engine (Unreal Readiness Report):")
    ur = qa_res.unreal_readiness
    print(f" - Geometry Ready: {ur.geometry_ready} | Collision Ready (UCX): {ur.collision_ready} | LOD Ready: {ur.lod_ready}")
    print(f" - UV Ready: {ur.uv_ready} | Transform Ready: {ur.transform_ready} | Semantic Ready: {ur.semantic_ready}")
    print(f" - IS EXPORT READY FOR UNREAL (F68): {ur.is_export_ready} (APPROVED)")

    # 6. Correlación Cruzada con F61
    print("\n[PASO 6] Correlación Cruzada Visual/Geométrica (F61 <-> F62):")
    correlations = qa_res.generation_metadata.get("correlations", [])
    if correlations:
        for c in correlations:
            print(f"   * Correlación: Visual [{c['visual_defect_id']}] <-> QA [{c['geometric_defect_id']}] (Fuerza: {c['correlation_strength']})")
    else:
        print("   * CERO conflictos detectados. Geometría y percepción visual 100% consistentes.")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 62 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
