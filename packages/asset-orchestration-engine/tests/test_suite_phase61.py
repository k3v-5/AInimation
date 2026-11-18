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
from src.automated_visual_evaluation import (
    AutomatedVisualEvaluationAPI, EvaluationCategory, DefectType,
    DefectSeverity, AcceptanceStatus, RegressionStatus, VisualDefect,
    CategoryEvaluation, EvaluationConfiguration
)

class TestAutomatedVisualEvaluationPhase61(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.eval_api = AutomatedVisualEvaluationAPI()

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
            semantic_context={"semantic_id": "barrel_01.root", "asset_id": "barrel_01"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        surf = self.surf_api.generate_surface(geom)
        vpc = self.pres_api.build_presentation_context(geom, surf, ref_report, vas)
        return ref_report, vas, geom, surf, vpc

    def test_01_case_a_correct_asset_high_score(self):
        """Case A: Asset correcto produce score global alto y status PASS."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertGreaterEqual(res.global_score, 0.90)
        self.assertEqual(len([d for d in res.defects if d.severity == DefectSeverity.CRITICAL]), 0)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.PASS)

    def test_02_case_b_wrong_silhouette_detection(self):
        """Case B: Silueta deformada es detectada con tipo WRONG_SILHOUETTE."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        # Modificar referencia para crear discrepancia artificial de silueta
        ref.silhouette.aspect_ratio = 3.50 # Gran discrepancia
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        sil_defects = [d for d in res.defects if d.defect_type == DefectType.WRONG_SILHOUETTE]
        self.assertGreater(len(sil_defects), 0)
        self.assertIn("GEOMETRY", sil_defects[0].probable_causes)

    def test_03_case_c_proportion_defect_detection(self):
        """Case C: Discrepancia de proporciones genera defecto con hint de corrección."""
        cats = {
            EvaluationCategory.PROPORTION.value: CategoryEvaluation(
                category=EvaluationCategory.PROPORTION,
                score=0.65,
                metrics={"width_error": 0.25}
            )
        }
        defects = self.eval_api.detect_defects({"category_scores": cats})
        self.assertGreater(len(defects), 0)
        self.assertEqual(defects[0].defect_type, DefectType.WRONG_PROPORTION)
        self.assertIsNotNone(defects[0].correction_hint)

    def test_04_case_d_wrong_material_cause_attribution(self):
        """Case E: Defecto de material atribuido a MATERIAL y no a geometría."""
        cats = {
            EvaluationCategory.MATERIAL.value: CategoryEvaluation(
                category=EvaluationCategory.MATERIAL,
                score=0.60,
                metrics={"roughness_error": 0.30}
            )
        }
        defects = self.eval_api.detect_defects({"category_scores": cats})
        self.assertGreater(len(defects), 0)
        self.assertEqual(defects[0].defect_type, DefectType.WRONG_MATERIAL)
        self.assertGreater(defects[0].probable_causes.get("MATERIAL", 0.0), 0.80)

    def test_05_case_e_temporal_comparison_improvement(self):
        """Case I: Comparación de iteraciones N y N+1 detecta IMPROVEMENT."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        eval1 = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        eval2 = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        eval1.global_score = 0.80
        eval2.global_score = 0.94
        eval1.defects = [VisualDefect("DEF_1", DefectType.WRONG_SILHOUETTE)]
        eval2.defects = []
        delta = self.eval_api.compare_iterations(eval1, eval2)
        self.assertEqual(delta.regression_status, RegressionStatus.IMPROVEMENT)
        self.assertIn("WRONG_SILHOUETTE", delta.fixed_defects)

    def test_06_case_f_temporal_comparison_regression(self):
        """Case J: Nueva anomalía introducida detecta REGRESSION."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        eval1 = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        eval2 = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        eval1.defects = []
        eval2.defects = [VisualDefect("DEF_NEW", DefectType.WRONG_MATERIAL)]
        eval2.global_score = 0.75
        delta = self.eval_api.compare_iterations(eval1, eval2)
        self.assertEqual(delta.regression_status, RegressionStatus.REGRESSION)
        self.assertIn("WRONG_MATERIAL", delta.new_defects)

    def test_07_case_g_deterministic_evaluation_hash(self):
        """Case H: Dos evaluaciones con idéntica entrada producen el mismo hash (SHA-256)."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res1 = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        res2 = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertEqual(res1.evaluation_hash, res2.evaluation_hash)

    def test_08_metric_registry_evaluates_enabled_categories(self):
        """Test 08: MetricRegistry evalúa todas las categorías habilitadas."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertIn(EvaluationCategory.SILHOUETTE.value, res.category_scores)
        self.assertIn(EvaluationCategory.PROPORTION.value, res.category_scores)
        self.assertIn(EvaluationCategory.MATERIAL.value, res.category_scores)
        self.assertIn(EvaluationCategory.LIGHTING.value, res.category_scores)

    def test_09_multi_hypothesis_cause_estimation(self):
        """Test 09: Defecto contiene probabilidades multi-hipótesis de causa."""
        cats = {
            EvaluationCategory.SILHOUETTE.value: CategoryEvaluation(
                category=EvaluationCategory.SILHOUETTE,
                score=0.60,
                metrics={"aspect_ratio_error": 0.20}
            )
        }
        defects = self.eval_api.detect_defects({"category_scores": cats})
        self.assertGreaterEqual(len(defects[0].probable_causes), 2)
        self.assertIn("GEOMETRY", defects[0].probable_causes)
        self.assertIn("CAMERA", defects[0].probable_causes)

    def test_10_correction_hint_structure(self):
        """Test 10: CorrectionHint contiene target, parámetro, dirección y ganancia esperada."""
        cats = {
            EvaluationCategory.PROPORTION.value: CategoryEvaluation(
                category=EvaluationCategory.PROPORTION,
                score=0.65,
                metrics={"width_error": 0.25}
            )
        }
        defects = self.eval_api.detect_defects({"category_scores": cats})
        hint = defects[0].correction_hint
        self.assertEqual(hint.target, "component.body")
        self.assertEqual(hint.parameter, "width")
        self.assertGreater(hint.expected_score_gain, 0.0)

    def test_11_global_score_weighted_average(self):
        """Test 11: Score global calculado como promedio ponderado de categorías."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertGreaterEqual(res.global_score, 0.0)
        self.assertLessEqual(res.global_score, 1.0)

    def test_12_validation_clean_result(self):
        """Test 12: Validación de resultado limpio retorna is_valid = True."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        val = self.eval_api.validate_evaluation(res)
        self.assertTrue(val.is_valid)

    def test_13_difference_maps_present(self):
        """Test 13: Mapas de diferencia registrados en el resultado."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertIn("silhouette_diff", res.difference_maps)
        self.assertIn("heatmap", res.difference_maps)

    def test_14_evaluate_single_category_api(self):
        """Test 14: API evaluate_category evalúa una categoría individual."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        cat_res = self.eval_api.evaluate_category(
            EvaluationCategory.SILHOUETTE, ref, geom, {"surface": surf, "presentation": vpc}
        )
        self.assertEqual(cat_res.category, EvaluationCategory.SILHOUETTE)
        self.assertGreater(cat_res.score, 0.0)

    def test_15_acceptance_status_pass_with_warnings(self):
        """Test 15: Defecto menor produce PASS_WITH_WARNINGS."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        ref.silhouette.aspect_ratio = 1.65 # Discrepancia leve
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertEqual(res.acceptance_status, AcceptanceStatus.PASS_WITH_WARNINGS)

    def test_16_defect_severity_levels(self):
        """Test 16: Asignación de severidad según magnitud del desvío."""
        cats = {
            EvaluationCategory.SILHOUETTE.value: CategoryEvaluation(
                category=EvaluationCategory.SILHOUETTE,
                score=0.40,
                metrics={"aspect_ratio_error": 0.50}
            )
        }
        defects = self.eval_api.detect_defects({"category_scores": cats})
        self.assertEqual(defects[0].severity, DefectSeverity.MAJOR)

    def test_17_execution_trace_records_steps(self):
        """Test 17: Traza de ejecución registra etapas de la evaluación."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertGreater(len(res.execution_trace), 0)
        steps = [t["step"] for t in res.execution_trace]
        self.assertIn("EXECUTE_METRICS", steps)
        self.assertIn("DETECT_DEFECTS", steps)

    def test_18_defect_localization_bbox(self):
        """Test 18: Defecto localizado con coordenadas bbox válidas."""
        cats = {
            EvaluationCategory.SILHOUETTE.value: CategoryEvaluation(
                category=EvaluationCategory.SILHOUETTE,
                score=0.60,
                metrics={"aspect_ratio_error": 0.20}
            )
        }
        defects = self.eval_api.detect_defects({"category_scores": cats})
        bbox = defects[0].bbox
        self.assertEqual(len(bbox), 4)
        self.assertLessEqual(bbox[0], bbox[2])

    def test_19_invalidation_state_handling(self):
        """Test 19: Evaluación mantiene trazabilidad de hashes geométricos y de superficie."""
        ref, _, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        self.assertEqual(res.geometry_generation_id, geom.generation_id)
        self.assertEqual(res.surface_generation_id, surf.surface_generation_id)
        self.assertEqual(res.presentation_id, vpc.presentation_id)

    def test_20_end_to_end_visual_evaluation_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> Listo para F62."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        res = self.eval_api.evaluate_visuals(ref, geom, {"surface": surf, "presentation": vpc})
        val = self.eval_api.validate_evaluation(res)
        self.assertTrue(val.is_valid)
        self.assertGreaterEqual(res.global_score, 0.90)
        self.assertGreater(len(res.evaluation_hash), 0)
        self.assertEqual(res.acceptance_status, AcceptanceStatus.PASS)

if __name__ == "__main__":
    unittest.main()
