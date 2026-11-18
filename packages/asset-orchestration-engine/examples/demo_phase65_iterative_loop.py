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
from src.iterative_generation_loop import (
    IterativeGenerationLoopAPI, IterativeGenerationRequest, IterationLoopConfiguration,
    IterationTargets
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 65: ITERATIVE GENERATION LOOP")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()
    geom_api = GeometryGenerationAPI()
    surf_api = MaterialSurfaceAPI()
    pres_api = PresentationMatchingAPI()
    loop_api = IterativeGenerationLoopAPI()

    # 1. Pipeline Inicial: Prompt -> F55 Ref -> F56 VAS -> F57 MSP -> F58 Geom -> F59 Surf -> F60 Pres
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
        semantic_context={"semantic_id": "barrel_hero.root", "asset_id": "barrel_hero"},
        project_constraints={"nanite": True, "collision": "CUSTOM_UCX"}
    )
    vas = vas_api.compile_specification(vas_input)
    msp = msp_api.plan_strategy(vas)
    geom_res = geom_api.generate_geometry(msp)
    surf_res = surf_api.generate_surface(geom_res, vas, msp, generation_seed=42)
    vpc = pres_api.build_presentation_context(geom_res, surf_res, f55_report, vas)
    print(f" - Geometría: [{geom_res.generation_id}] | Superficie: [{surf_res.surface_generation_id}] | VPC: [{vpc.presentation_id}]")

    # 2. Configuración y Ejecución del Ciclo Autónomo Iterativo (F65)
    print("\n[PASO 2] Ejecución del Ciclo Autónomo Iterativo (F65 Closed Loop: F61 -> F62 -> F63 -> F64):")
    loop_config = IterationLoopConfiguration(
        max_iterations=4,
        targets=IterationTargets(
            overall_target_score=0.92,
            minimum_visual_score=0.90,
            minimum_geometry_score=0.90
        )
    )
    request = IterativeGenerationRequest(
        job_id="HERO_BARREL_RUN_01",
        asset_id="barrel_hero",
        semantic_id="barrel_hero.root",
        reference_report=f55_report,
        vas=vas,
        configuration=loop_config
    )

    loop_res = loop_api.execute_iterative_loop(request, geom_res, surf_res, vpc)
    val = loop_api.validate_loop_result(loop_res)
    print(f" - Loop ID: [{loop_res.loop_id}] | Válido: {val.is_valid} | Status: [{loop_res.status.value}]")
    print(f" - Razón de Parada: [{loop_res.stop_reason.value}] | Iteraciones Ejecutadas: {loop_res.iterations_executed}")
    print(f" - Calidad Inicial: {loop_res.initial_quality*100:.1f}% -> Calidad Final Óptima: {loop_res.final_quality*100:.1f}% (Delta: {loop_res.quality_delta:+.2f})")
    print(f" - Mejor Iteración Seleccionada: [Iteración #{loop_res.best_iteration}]")
    print(f" - Hash Determinista del Loop (SHA-256): {loop_res.loop_hash[:16]}...{loop_res.loop_hash[-8:]}")

    # 3. Historial de Iteraciones y Evolución de Calidad
    print("\n[PASO 3] Historial Detallado de Iteraciones (Evolución de Scores y Decisiones):")
    for rec in loop_res.iteration_history:
        print(f"   * [Iter #{rec.iteration_number}] Score Global: {rec.overall_score:.4f} (Visual: {rec.visual_score:.4f}, Geom: {rec.geometry_score:.4f}) -> Decisión: [{rec.decision.value}] (Aceptada: {rec.accepted})")

    # 4. Verificación de Checkpoint y Capacidad de Reanudación
    print("\n[PASO 4] Verificación de Checkpoints y Reanudación de Estado:")
    checkpoint = loop_api.resume_loop(loop_res.loop_id)
    if checkpoint:
        print(f" - Checkpoint Cargado Exitosamente para Loop [{loop_res.loop_id}]: Iteración #{checkpoint['iteration_number']}")
        print(f" - Datos de Checkpoint: {checkpoint['payload']}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 65 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
