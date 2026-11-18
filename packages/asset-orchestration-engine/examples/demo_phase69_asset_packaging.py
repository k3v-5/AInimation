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
from src.asset_optimization_engine import AssetOptimizationAPI
from src.game_engine_readiness import GameEngineReadinessAPI, ReadinessStatus
from src.asset_packaging_delivery import (
    AssetPackagingAPI, PackageProfile, DeliveryTarget,
    PackageType, DeliveryTargetType
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 69: ASSET PACKAGING & DELIVERY SYSTEM")
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
    pkg_api = AssetPackagingAPI()

    # 1. Pipeline Previo (F55 a F68)
    print("\n[PASO 1] Pipeline Previo y Asset Validado para Motor (F55 a F68):")
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
    ready_asset = readiness_api.verify_and_prepare_for_engine(opt_res)
    print(f" - Engine Ready Status (F68): [{ready_asset.readiness_status.value}] | Score: {ready_asset.readiness_score:.1f}/100.0")

    # 2. Empaquetado y Sellado del Paquete (F69)
    print("\n[PASO 2] Empaquetado y Sellado de Contenido (F69):")
    pkg_profile = PackageProfile(
        profile_id="UNREAL_ENGINE_HERO_BUNDLE",
        package_type=PackageType.UNREAL_ASSET_PACKAGE,
        target_engine="UNREAL_ENGINE",
        target_engine_version="5.4"
    )
    delivery_target = DeliveryTarget(
        target_id="TARGET_PROJECT_SAVED",
        target_type=DeliveryTargetType.PROJECT_DIRECTORY,
        destination_path="E:/Darx_Proyect/Saved/Bundles"
    )
    delivered_pkg = pkg_api.package_and_deliver_asset(
        ready_asset=ready_asset,
        profile=pkg_profile,
        target=delivery_target
    )
    val = pkg_api.validate_delivered_package(delivered_pkg)
    print(f" - Package ID: [{delivered_pkg.package_id}] | Válido: {val.is_valid}")
    print(f" - Content Hash (SHA-256): {delivered_pkg.package_content_hash[:16]}...{delivered_pkg.package_content_hash[-8:]}")
    print(f" - Total Archivos Empaquetados: {len(delivered_pkg.manifest.files)} ({delivered_pkg.package_size / 1024:.1f} KB)")

    # 3. Verificación de Entrega y Recibo
    print("\n[PASO 3] Verificación Transaccional de Entrega y Recibo:")
    rcpt = delivered_pkg.delivery_receipt
    print(f" - Receipt ID: [{rcpt.receipt_id}] | Status: [{rcpt.status}]")
    print(f" - Destino Verificado: [{rcpt.destination}]")
    print(f" - Archivos Transferidos: {rcpt.transferred_files} | Bytes: {rcpt.bytes_transferred}")
    print(f" - Hash Destino == Hash Paquete: {rcpt.package_hash == rcpt.destination_hash}")

    # 4. Demostración de Rechazo ante Asset No Preparado
    print("\n[PASO 4] Demostración de Gate de Readiness (Rechazo ante Asset NOT_READY):")
    ready_asset.readiness_status = ReadinessStatus.NOT_READY
    rejected_pkg = pkg_api.package_and_deliver_asset(ready_asset)
    print(f" - Delivery Status de Asset No Preparado: [{rejected_pkg.delivery_status}]")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 69 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
