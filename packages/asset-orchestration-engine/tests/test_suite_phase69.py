import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import VisualSpecificationAPI, VisualCompilationInput
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

class TestAssetPackagingPhase69(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.eval_api = AutomatedVisualEvaluationAPI()
        self.qa_api = GeometricValidationAPI()
        self.scoring_api = QualityScoringAPI()
        self.opt_api = AssetOptimizationAPI()
        self.readiness_api = GameEngineReadinessAPI()
        self.pkg_api = AssetPackagingAPI()

    def _get_pipeline_data(self):
        ref_report = DecomposedReferenceReport(
            report_id="REP_F55_BARREL_01",
            reference_ids=["REF_01"],
            silhouette=SilhouetteExtraction(aspect_ratio=1.0),
            proportions=ProportionEstimate(component_ratios={"body": 0.8, "top_ring": 0.1, "bottom_ring": 0.1}),
            parts=[
                DecomposedPart("part_body", "BODY", (0, 0, 1, 1.0), (0, 0, 0), True, 0.98),
                DecomposedPart("part_ring_top", "RING_01", (0, 0.8, 1.02, 0.15), (0, 0, 0.8), False, 0.95),
                DecomposedPart("part_ring_bottom", "RING_02", (0, 0.2, 1.02, 0.15), (0, 0, 0.2), False, 0.95)
            ],
            materials=MaterialPalette(base_material=ExtractedMaterialType.WOOD, surface_roughness=0.68)
        )
        vas_in = VisualCompilationInput(
            prompt="Barril medieval de roble con aros de hierro",
            asset_class_hint="PROP.BARREL",
            reference_reports=[ref_report],
            semantic_context={"semantic_id": "barrel_01.root", "asset_id": "barrel_01"},
            project_constraints={"nanite": True, "collision": "CUSTOM_UCX"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        surf = self.surf_api.generate_surface(geom)
        vpc = self.pres_api.build_presentation_context(geom, surf, ref_report, vas)
        v_eval = self.eval_api.evaluate_visuals(ref_report, geom, {"surface": surf, "presentation": vpc})
        g_qa = self.qa_api.validate_geometry(geom, {"visual_evaluation": v_eval, "surface": surf})
        q_res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        opt_res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        return ready_asset

    def test_01_case_a_valid_packaging_and_delivery(self):
        """Case A: Asset validado se empaqueta y entrega correctamente (status DELIVERY_VERIFIED)."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertEqual(pkg.delivery_status, "DELIVERY_VERIFIED")
        self.assertEqual(pkg.delivery_receipt.status, "DELIVERY_VERIFIED")

    def test_02_case_b_unready_asset_rejection(self):
        """Case B: Asset con status NOT_READY o FAILED es rechazado por packaging gate."""
        ready_asset = self._get_pipeline_data()
        ready_asset.readiness_status = ReadinessStatus.NOT_READY
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertEqual(pkg.delivery_status, "REJECTED_UNREADY")

    def test_03_case_c_missing_required_dependency_blocks(self):
        """Case C: Falta de dependencia obligatoria bloquea el empaquetado."""
        ready_asset = self._get_pipeline_data()
        context = {"force_missing_required_dependency": True}
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset, context=context)
        self.assertEqual(pkg.delivery_status, "FAILED_MISSING_DEPENDENCY")

    def test_04_case_d_immutable_sealing_hash(self):
        """Case D: El sellado del paquete produce un hash de contenido inmutable."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertGreater(len(pkg.package_content_hash), 0)
        self.assertGreater(len(pkg.package_state_hash), 0)

    def test_05_case_e_deterministic_packaging_hash(self):
        """Case E: Dos ejecuciones idénticas producen el mismo content_hash (SHA-256)."""
        ready_asset = self._get_pipeline_data()
        pkg1 = self.pkg_api.package_and_deliver_asset(ready_asset)
        pkg2 = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertEqual(pkg1.package_content_hash, pkg2.package_content_hash)

    def test_06_case_f_local_directory_delivery(self):
        """Case F: Entrega en directorio local registra archivos transferidos."""
        ready_asset = self._get_pipeline_data()
        tgt = DeliveryTarget(destination_path="E:/Darx_Proyect/Saved/TestDelivery")
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset, target=tgt)
        self.assertGreater(pkg.delivery_receipt.transferred_files, 0)
        self.assertGreater(pkg.delivery_receipt.bytes_transferred, 0)

    def test_07_case_g_delivery_failure_handling(self):
        """Case G: Fallo simulado de entrega marca recibo como FAILED."""
        ready_asset = self._get_pipeline_data()
        context = {"force_delivery_failure": True}
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset, context=context)
        self.assertEqual(pkg.delivery_receipt.status, "FAILED")

    def test_08_case_h_dependency_resolver_resolves_all(self):
        """Case H: DependencyResolver resuelve malla, materiales y colisión."""
        from src.asset_packaging_delivery.builder.dependency_resolver import DependencyResolver
        ready_asset = self._get_pipeline_data()
        deps = DependencyResolver.resolve_dependencies(ready_asset, {})
        types = [d.dep_type for d in deps]
        self.assertIn("STATIC_MESH", types)
        self.assertIn("MATERIAL", types)
        self.assertIn("COLLISION", types)

    def test_09_case_i_delivery_target_configuration(self):
        """Case I: Configuración de DeliveryTarget."""
        tgt = DeliveryTarget(target_id="TGT_CUSTOM", target_type=DeliveryTargetType.PROJECT_DIRECTORY)
        self.assertEqual(tgt.target_id, "TGT_CUSTOM")
        self.assertEqual(tgt.target_type, DeliveryTargetType.PROJECT_DIRECTORY)

    def test_10_case_j_package_profile_configuration(self):
        """Case J: Configuración de PackageProfile para Unreal Engine 5.4."""
        prof = PackageProfile(target_engine="UNREAL_ENGINE", target_engine_version="5.4")
        self.assertEqual(prof.target_engine_version, "5.4")

    def test_11_package_size_and_files_count(self):
        """Test 11: Cálculo correcto del tamaño total y cantidad de archivos."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertGreater(pkg.package_size, 0)
        self.assertGreater(len(pkg.manifest.files), 0)

    def test_12_validation_clean_result(self):
        """Test 12: Validación de paquete entregado retorna is_valid = True."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        val = self.pkg_api.validate_delivered_package(pkg)
        self.assertTrue(val.is_valid)

    def test_13_preservation_of_ids(self):
        """Test 13: Preservación de asset_id y semantic_id."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertEqual(pkg.asset_id, "barrel_01")
        self.assertEqual(pkg.semantic_id, "barrel_01.root")

    def test_14_provenance_tracking(self):
        """Test 14: Registro de procedencia en paquete entregado."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertIn("aoe_version", pkg.provenance)

    def test_15_audit_trail_recorded(self):
        """Test 15: Registro de auditoría con pasos ejecutados."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertGreater(len(pkg.audit_trail), 0)

    def test_16_receipt_hash_match(self):
        """Test 16: Coincidencia entre package_hash y destination_hash."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertEqual(pkg.delivery_receipt.package_hash, pkg.delivery_receipt.destination_hash)

    def test_17_non_destructive_verification(self):
        """Test 17: Packaging no muta el GameEngineReadyAsset de entrada."""
        ready_asset = self._get_pipeline_data()
        hash_before = ready_asset.readiness_hash
        _ = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertEqual(ready_asset.readiness_hash, hash_before)

    def test_18_package_type_enumeration(self):
        """Test 18: Tipos de paquete soportados."""
        self.assertEqual(PackageType.UNREAL_ASSET_PACKAGE.value, "UNREAL_ASSET_PACKAGE")
        self.assertEqual(PackageType.AOE_ARCHIVE.value, "AOE_ARCHIVE")

    def test_19_manifest_schema_version(self):
        """Test 19: Schema version en el manifiesto del paquete."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        self.assertEqual(pkg.manifest.schema_version, "1.0.0")

    def test_20_end_to_end_packaging_pipeline_for_f70(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> F64 -> F65 -> F66 -> F67 -> F68 -> F69 -> Listo para F70 Long-Running Jobs."""
        ready_asset = self._get_pipeline_data()
        pkg = self.pkg_api.package_and_deliver_asset(ready_asset)
        val = self.pkg_api.validate_delivered_package(pkg)
        self.assertTrue(val.is_valid)
        self.assertEqual(pkg.delivery_status, "DELIVERY_VERIFIED")
        self.assertGreater(len(pkg.package_id), 0)
        self.assertGreater(len(pkg.package_content_hash), 0)

if __name__ == "__main__":
    unittest.main()
