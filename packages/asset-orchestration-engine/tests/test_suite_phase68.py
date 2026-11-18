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
from src.game_engine_readiness import (
    GameEngineReadinessAPI, ReadinessStatus, EngineProfile,
    EngineTarget, ValidationSeverity
)

class TestGameEngineReadinessPhase68(unittest.TestCase):
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
        return opt_res

    def test_01_case_a_full_readiness_acceptance(self):
        """Case A: Asset optimizado válido alcanza status READY con score 100/100."""
        opt_res = self._get_pipeline_data()
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        self.assertEqual(ready_asset.readiness_status, ReadinessStatus.READY)
        self.assertEqual(ready_asset.readiness_score, 100.0)

    def test_02_case_b_missing_collision_blocker(self):
        """Case B: Falta de colisión obligatoria genera BLOCKER y status NOT_READY."""
        opt_res = self._get_pipeline_data()
        context = {"force_missing_collision": True}
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res, context=context)
        self.assertEqual(ready_asset.readiness_status, ReadinessStatus.NOT_READY)
        self.assertLess(ready_asset.readiness_score, 100.0)

    def test_03_case_c_unapplied_transforms_blocker(self):
        """Case C: Transforms sin aplicar generan BLOCKER y status NOT_READY."""
        opt_res = self._get_pipeline_data()
        context = {"force_unapplied_transform": True}
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res, context=context)
        self.assertEqual(ready_asset.readiness_status, ReadinessStatus.NOT_READY)

    def test_04_case_d_material_slots_warning(self):
        """Case D: Exceso no crítico de slots genera WARNING y READY_WITH_WARNINGS."""
        opt_res = self._get_pipeline_data()
        prof = EngineProfile(max_material_slots=0) # Forzar warning de slots
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res, engine_profile=prof)
        self.assertEqual(ready_asset.readiness_status, ReadinessStatus.READY_WITH_WARNINGS)

    def test_05_case_e_stale_state_protection(self):
        """Case E: Discrepancia en source_state_hash genera status FAILED."""
        opt_res = self._get_pipeline_data()
        context = {"expected_source_hash": "HASH_MISMATCH_EXPECTED"}
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res, context=context)
        self.assertEqual(ready_asset.readiness_status, ReadinessStatus.FAILED)

    def test_06_case_f_deterministic_readiness_hash(self):
        """Case F: Dos validaciones idénticas producen el mismo hash (SHA-256)."""
        opt_res = self._get_pipeline_data()
        res1 = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        res2 = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        self.assertEqual(res1.readiness_hash, res2.readiness_hash)

    def test_07_case_g_geometry_validator(self):
        """Case G: Validador de geometría verifica presupuesto de polígonos."""
        from src.game_engine_readiness.validators.geometry_validator import GeometryValidator
        val = GeometryValidator()
        prof = EngineProfile(max_triangle_count=50) # Menor a los 68 tris
        results = val.validate(self._get_pipeline_data(), prof, {})
        self.assertFalse(results[0].passed)
        self.assertEqual(results[0].severity, ValidationSeverity.BLOCKER)

    def test_08_case_h_material_texture_validator(self):
        """Case H: Validador de materiales verifica cantidad de slots."""
        from src.game_engine_readiness.validators.material_texture_validator import MaterialTextureValidator
        val = MaterialTextureValidator()
        prof = EngineProfile(max_material_slots=4)
        results = val.validate(self._get_pipeline_data(), prof, {})
        self.assertTrue(results[0].passed)

    def test_09_case_i_transform_pivot_validator(self):
        """Case I: Validador de transforms verifica escala y pivote."""
        from src.game_engine_readiness.validators.transform_pivot_validator import TransformPivotValidator
        val = TransformPivotValidator()
        results = val.validate(self._get_pipeline_data(), EngineProfile(), {})
        self.assertTrue(results[0].passed)

    def test_10_case_j_collision_lod_validator(self):
        """Case J: Validador de colisiones verifica convención UCX_."""
        from src.game_engine_readiness.validators.collision_lod_validator import CollisionLODValidator
        val = CollisionLODValidator()
        results = val.validate(self._get_pipeline_data(), EngineProfile(), {})
        self.assertTrue(results[0].passed)

    def test_11_readiness_score_calculation(self):
        """Test 11: Cálculo de puntuación de preparación para el motor."""
        opt_res = self._get_pipeline_data()
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        self.assertGreater(ready_asset.readiness_score, 0.0)

    def test_12_validation_clean_result(self):
        """Test 12: Validación de resultado limpio retorna is_valid = True."""
        opt_res = self._get_pipeline_data()
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        val = self.readiness_api.validate_engine_ready_asset(ready_asset)
        self.assertTrue(val.is_valid)

    def test_13_engine_profile_customization(self):
        """Test 13: Configuración de perfil de motor para Unreal Engine 5."""
        prof = EngineProfile(target_engine=EngineTarget.UNREAL_ENGINE_5, require_ucx_collision=True)
        self.assertEqual(prof.target_engine, EngineTarget.UNREAL_ENGINE_5)
        self.assertTrue(prof.require_ucx_collision)

    def test_14_export_profile_settings(self):
        """Test 14: Configuración de ExportProfile (FBX con escala 100.0)."""
        from src.game_engine_readiness import ExportProfile
        exp = ExportProfile(format="FBX", unit_scale=100.0)
        self.assertEqual(exp.format, "FBX")
        self.assertEqual(exp.unit_scale, 100.0)

    def test_15_preservation_of_ids(self):
        """Test 15: Preservación de asset_id y semantic_id."""
        opt_res = self._get_pipeline_data()
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        self.assertEqual(ready_asset.asset_id, "barrel_01")
        self.assertEqual(ready_asset.semantic_id, "barrel_01.root")

    def test_16_human_report_generation(self):
        """Test 16: Generación del informe legible Game-Engine Readiness Report."""
        opt_res = self._get_pipeline_data()
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        report = self.readiness_api.generate_human_report(ready_asset.manifest)
        self.assertIn("GAME-ENGINE READINESS REPORT", report)

    def test_17_remediation_hints_on_failure(self):
        """Test 17: Emisión de recomendaciones técnicas ante fallos de validación."""
        opt_res = self._get_pipeline_data()
        context = {"force_unapplied_transform": True}
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res, context=context)
        failed_res = [r for r in ready_asset.manifest.validation_results if not r.passed]
        self.assertIsNotNone(failed_res[0].remediation)

    def test_18_non_destructive_verification(self):
        """Test 18: La verificación no muta el resultado de optimización de F67."""
        opt_res = self._get_pipeline_data()
        hash_before = opt_res.optimization_hash
        _ = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        self.assertEqual(opt_res.optimization_hash, hash_before)

    def test_19_manifest_structure_valid(self):
        """Test 19: Manifiesto contiene lista de validaciones y hashes."""
        opt_res = self._get_pipeline_data()
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        self.assertGreater(len(ready_asset.manifest.validation_results), 0)
        self.assertIsNotNone(ready_asset.manifest.manifest_id)

    def test_20_end_to_end_readiness_pipeline_for_f69(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> F64 -> F65 -> F66 -> F67 -> F68 -> Listo para F69 Packaging."""
        opt_res = self._get_pipeline_data()
        ready_asset = self.readiness_api.verify_and_prepare_for_engine(opt_res)
        val = self.readiness_api.validate_engine_ready_asset(ready_asset)
        self.assertTrue(val.is_valid)
        self.assertEqual(ready_asset.readiness_status, ReadinessStatus.READY)
        self.assertGreater(len(ready_asset.prepared_state_hash), 0)
        self.assertGreater(len(ready_asset.readiness_hash), 0)

if __name__ == "__main__":
    unittest.main()
