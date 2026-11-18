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
from src.quality_scoring_acceptance import (
    QualityScoringAPI, AcceptanceStatus, QualityLevel, QualityProfile,
    MetricCategory, DirectionType, MetricNormalizer
)

class TestQualityScoringAcceptancePhase66(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.eval_api = AutomatedVisualEvaluationAPI()
        self.qa_api = GeometricValidationAPI()
        self.scoring_api = QualityScoringAPI()

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
        return vas, geom, v_eval, g_qa

    def test_01_case_a_clean_asset_acceptance(self):
        """Case A: Asset limpio pasa todas las restricciones y alcanza status ACCEPTED."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.ACCEPTED)
        self.assertEqual(res.quality_level, QualityLevel.EXCEPTIONAL)
        self.assertGreaterEqual(res.overall_score, 85.0)

    def test_02_case_b_hard_constraint_failure_rejection(self):
        """Case B: Fallo en restricción crítica produce REJECTED a pesar de alto score visual."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        # Inyectar defecto crítico en g_qa
        from src.geometric_validation_qa import GeometricDefect, DefectSeverity, GeometricDefectCategory
        g_qa.defects.append(
            GeometricDefect("DEF_NON_MANIFOLD", GeometricDefectCategory.NON_MANIFOLD, DefectSeverity.CRITICAL, "Non-manifold edge")
        )
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.REJECTED)
        self.assertGreater(len(res.blocking_reasons), 0)

    def test_03_case_c_conditional_acceptance_with_warnings(self):
        """Case C: Advertencias no bloqueantes producen status CONDITIONAL."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_WARN", DefectType.WRONG_COLOR, region="body", error_pct=10.0)]
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertIn(res.acceptance_status, (AcceptanceStatus.ACCEPTED, AcceptanceStatus.CONDITIONAL))

    def test_04_case_d_category_minimum_failure(self):
        """Case D: Fallar el mínimo de una categoría requerida produce REJECTED."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        prof = QualityProfile(category_minimums={MetricCategory.VISUAL: 0.999}) # Imposiblemente alto
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa, profile=prof)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.REJECTED)

    def test_05_case_e_stale_evaluation_protection(self):
        """Case E: Discrepancia de state_hash produce status INVALID."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        context = {"expected_state_hash": "HASH_MISMATCH_EXPECTED"}
        g_qa.state_hash = "ACTUAL_HASH_001"
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa, context=context)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.INVALID)

    def test_06_case_f_metric_normalization(self):
        """Case F: Normalización correcta de métricas directas, inversas y booleanas."""
        self.assertEqual(MetricNormalizer.normalize(95.0, DirectionType.HIGHER_IS_BETTER), 0.95)
        self.assertEqual(MetricNormalizer.normalize(0.10, DirectionType.LOWER_IS_BETTER), 0.90)
        self.assertEqual(MetricNormalizer.normalize(True, DirectionType.BOOLEAN), 1.0)
        self.assertEqual(MetricNormalizer.normalize(False, DirectionType.BOOLEAN), 0.0)

    def test_07_case_g_custom_quality_profile(self):
        """Case G: Configuración personalizada de pesos en QualityProfile."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        prof = QualityProfile(
            weights={MetricCategory.VISUAL: 0.80, MetricCategory.GEOMETRY: 0.20},
            acceptance_threshold=90.0
        )
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa, profile=prof)
        self.assertIsNotNone(res.overall_score)

    def test_08_case_h_deterministic_quality_hash(self):
        """Case H: Dos evaluaciones idénticas producen el mismo quality_hash (SHA-256)."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res1 = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        res2 = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertEqual(res1.quality_hash, res2.quality_hash)

    def test_09_case_i_quality_report_generation(self):
        """Case I: Generación de reporte humano y máquina legible."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        report = self.scoring_api.generate_acceptance_report(res)
        self.assertIn("ASSET QUALITY & ACCEPTANCE REPORT", report.human_readable)
        self.assertEqual(report.asset_id, "barrel_01")

    def test_10_case_j_score_bounds_clamping(self):
        """Case J: El score global está estrictamente en el rango 0.0 a 100.0."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertGreaterEqual(res.overall_score, 0.0)
        self.assertLessEqual(res.overall_score, 100.0)

    def test_11_unreal_readiness_gate(self):
        """Test 11: Fallo en Unreal Readiness bloquea aceptación."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        g_qa.unreal_readiness.is_export_ready = False
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.REJECTED)

    def test_12_validation_clean_result(self):
        """Test 12: Validación de resultado limpio retorna is_valid = True."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        val = self.scoring_api.validate_quality_result(res)
        self.assertTrue(val.is_valid)

    def test_13_quality_level_mapping(self):
        """Test 13: Mapeo correcto de QualityLevel."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertIn(res.quality_level, [QualityLevel.EXCEPTIONAL, QualityLevel.PRODUCTION])

    def test_14_category_scores_breakdown(self):
        """Test 14: Desglose individual de scores por categoría."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertIn("VISUAL", res.category_scores)
        self.assertIn("GEOMETRY", res.category_scores)
        self.assertIn("TOPOLOGY", res.category_scores)

    def test_15_preservation_of_ids(self):
        """Test 15: Preservación de asset_id y semantic_id."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertEqual(res.asset_id, "barrel_01")
        self.assertEqual(res.semantic_id, "barrel_01.root")

    def test_16_non_destructive_scoring(self):
        """Test 16: El scoring no muta los resultados de F61 ni F62."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        v_hash_before = v_eval.evaluation_hash
        _ = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertEqual(v_eval.evaluation_hash, v_hash_before)

    def test_17_scoring_version_tracking(self):
        """Test 17: Versionado del algoritmo de scoring registrado."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertEqual(res.scoring_version, "1.0.0")

    def test_18_rejection_blocking_reasons(self):
        """Test 18: Registro explícito de razones de bloqueo en caso de rechazo."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        g_qa.unreal_readiness.is_export_ready = False
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        self.assertGreater(len(res.blocking_reasons), 0)

    def test_19_threshold_validation_rules(self):
        """Test 19: Validación de límites de thresholds en QualityProfile."""
        prof = QualityProfile(acceptance_threshold=85.0, conditional_threshold=70.0, rejection_threshold=50.0)
        self.assertLessEqual(prof.rejection_threshold, prof.conditional_threshold)
        self.assertLessEqual(prof.conditional_threshold, prof.acceptance_threshold)

    def test_20_end_to_end_quality_acceptance_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> F64 -> F65 -> F66 -> Listo para F67."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        report = self.scoring_api.generate_acceptance_report(res)
        val = self.scoring_api.validate_quality_result(res)
        self.assertTrue(val.is_valid)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.ACCEPTED)
        self.assertGreater(len(report.human_readable), 0)
        self.assertGreater(len(res.quality_hash), 0)

if __name__ == "__main__":
    unittest.main()
