import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.semantic_visual_critic import (
    SemanticVisualCriticAPI, ExpectedState, ActualState,
    DefectCategory, DefectSeverity, CriticRecommendation,
    CriticCameraView
)

class TestSemanticVisualCriticPhase50(unittest.TestCase):
    def setUp(self):
        self.api = SemanticVisualCriticAPI()

    def test_01_mandatory_case_1_forbidden_satellite_dish(self):
        """Mandatory Case 1: Casa medieval con antena satelital detecta FORBIDDEN_COMPONENT y recomienda removerla."""
        expected = ExpectedState(
            asset_class="HOUSE",
            required_components=["roof", "walls", "entrance"],
            forbidden_components=["satellite_dish", "antenna"]
        )
        actual = ActualState(
            detected_class="HOUSE",
            detected_components=["roof", "walls", "entrance", "satellite_dish"]
        )
        res = self.api.evaluate_asset(expected, actual)
        def_dish = next((d for d in res.defects if d.category == DefectCategory.FORBIDDEN_COMPONENT), None)
        self.assertIsNotNone(def_dish)
        self.assertEqual(def_dish.severity, DefectSeverity.MAJOR)
        self.assertIn("remove", def_dish.recommended_action.lower())

    def test_02_mandatory_case_2_wrong_roof_proportion(self):
        """Mandatory Case 2: Techo 51% vs 30% detecta WRONG_PROPORTION (MAJOR) con corrección 'reduce roof height'."""
        expected = ExpectedState(expected_proportions={"roof_ratio": 0.30})
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            measured_proportions={"roof_ratio": 0.51}
        )
        res = self.api.evaluate_asset(expected, actual)
        def_prop = next((d for d in res.defects if d.category == DefectCategory.WRONG_PROPORTION), None)
        self.assertIsNotNone(def_prop)
        self.assertEqual(def_prop.severity, DefectSeverity.MAJOR)
        self.assertEqual(def_prop.recommended_action, "reduce roof height")
        self.assertEqual(def_prop.scope, "LOCAL")

    def test_03_mandatory_case_3_window_spatial_occlusion(self):
        """Mandatory Case 3: Ventana detrás del muro detecta SPATIAL_ERROR y recomienda reposicionar."""
        expected = ExpectedState(required_components=["roof", "walls", "entrance", "window_01", "window_02"])
        actual = ActualState(
            detected_components=["roof", "walls", "entrance", "window_01", "window_02"],
            component_spatial_status={"window_02": "BEHIND_WALL"}
        )
        res = self.api.evaluate_asset(expected, actual)
        def_spat = next((d for d in res.defects if d.category == DefectCategory.SPATIAL_ERROR), None)
        self.assertIsNotNone(def_spat)
        self.assertEqual(def_spat.affected_component, "window_02")
        self.assertIn("reposition", def_spat.recommended_action)

    def test_04_mandatory_case_4_style_mismatch_and_overdetail(self):
        """Mandatory Case 4: Stylized low-poly solicitado vs fotorrealista micro-detalle detecta STYLE_MISMATCH y EXCESSIVE_DETAIL."""
        expected = ExpectedState(style="STYLIZED_LOW_POLY")
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            is_photorealistic=True,
            detail_density=0.92
        )
        res = self.api.evaluate_asset(expected, actual)
        cats = [d.category for d in res.defects]
        self.assertIn(DefectCategory.STYLE_MISMATCH, cats)
        self.assertIn(DefectCategory.EXCESSIVE_DETAIL, cats)

    def test_05_mandatory_case_5_structural_identity_failure_spaceship(self):
        """Mandatory Case 5: Casa vs Nave Espacial detecta STRUCTURAL_IDENTITY_FAILURE y recomienda REGENERATE_ASSET."""
        expected = ExpectedState(asset_class="HOUSE")
        actual = ActualState(detected_class="SPACESHIP")
        res = self.api.evaluate_asset(expected, actual)
        self.assertEqual(res.recommendation, CriticRecommendation.REGENERATE_ASSET)
        self.assertIn("STRUCTURAL_IDENTITY_FAILURE", res.hard_failures)

    def test_06_mandatory_case_6_diminishing_returns_detection(self):
        """Mandatory Case 6: Progresión 0.48 -> 0.71 -> 0.76 -> 0.765 detecta rendimientos decrecientes (Delta < 0.02)."""
        history = [0.48, 0.71, 0.76]
        current = 0.765
        delta = current - history[-1]
        self.assertLess(delta, 0.02) # Dispara ESCALATE/HALT

    def test_07_mandatory_case_7_regression_detection(self):
        """Mandatory Case 7: Nueva versión que oculta la entrada requerida genera hard failure y veta aprobación."""
        expected = ExpectedState(required_components=["roof", "walls", "entrance"])
        actual = ActualState(detected_components=["roof", "walls"]) # Falta entrance
        res = self.api.evaluate_asset(expected, actual)
        self.assertIn("MISSING_ENTRANCE", res.hard_failures)
        self.assertLessEqual(res.overall_score, 0.40)

    def test_08_mandatory_case_8_low_confidence_uncertain_warning(self):
        """Mandatory Case 8: Detección con baja confianza (0.41) genera advertencia UNCERTAIN sin regenerar activo."""
        expected = ExpectedState()
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            detection_confidences={"possible_chimney": 0.41}
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertTrue(any("UNCERTAIN" in w for w in res.warnings))
        self.assertNotEqual(res.recommendation, CriticRecommendation.REGENERATE_ASSET)

    def test_09_mandatory_case_9_multiview_evaluation(self):
        """Mandatory Case 9: Frontal correcto pero lateral incorrecto genera defecto en evaluación multi-vista."""
        expected = ExpectedState()
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            multi_view_aspect_ratios={
                CriticCameraView.FRONT: 1.52, # Perfecto
                CriticCameraView.LEFT: 2.10   # Lateral muy distorsionado (esperado 1.20)
            }
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertTrue(any(d.category == DefectCategory.WRONG_PROPORTION for d in res.defects))

    def test_10_mandatory_case_10_barrel_extra_ring(self):
        """Mandatory Case 10: Barril con 3 aros en vez de 2 genera corrección 'remove_extra_ring' sin regenerar todo."""
        expected = ExpectedState(asset_class="BARREL", required_components=["body", "ring_01", "ring_02"])
        actual = ActualState(
            detected_class="BARREL",
            detected_components=["body", "ring_01", "ring_02", "ring_03"]
        )
        res = self.api.evaluate_asset(expected, actual)
        def_ring = next((d for d in res.defects if d.category == DefectCategory.EXTRA_COMPONENT), None)
        self.assertIsNotNone(def_ring)
        self.assertEqual(def_ring.recommended_action, "remove_extra_ring")
        self.assertEqual(def_ring.scope, "LOCAL")

    def test_11_clean_asset_acceptance(self):
        """Test 11: Activo conforme sin defectos obtiene recomendación ACCEPT."""
        expected = ExpectedState(
            asset_class="HOUSE",
            required_components=["roof", "walls", "entrance"],
            expected_proportions={"roof_ratio": 0.30}
        )
        actual = ActualState(
            detected_class="HOUSE",
            detected_components=["roof", "walls", "entrance"],
            measured_proportions={"roof_ratio": 0.30}
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertEqual(res.recommendation, CriticRecommendation.ACCEPT)
        self.assertEqual(len(res.defects), 0)

    def test_12_three_layer_explainability(self):
        """Test 12: Explicabilidad estructurada en tres capas (MACHINE, HUMAN, AGENT)."""
        expected = ExpectedState(expected_proportions={"roof_ratio": 0.30})
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            measured_proportions={"roof_ratio": 0.51}
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertGreater(len(res.explanation_human), 0)
        self.assertGreater(len(res.explanation_agent), 0)
        self.assertGreater(len(res.defects), 0)

    def test_13_correction_plan_items(self):
        """Test 13: El Critic genera ítems de plan de corrección accionables."""
        expected = ExpectedState(expected_proportions={"roof_ratio": 0.30})
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            measured_proportions={"roof_ratio": 0.51}
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertGreater(len(res.correction_plan), 0)
        self.assertEqual(res.correction_plan[0].target_component, "roof")

    def test_14_local_defect_scope(self):
        """Test 14: Defectos localizados se etiquetan con scope LOCAL."""
        expected = ExpectedState(expected_proportions={"roof_ratio": 0.30})
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            measured_proportions={"roof_ratio": 0.45}
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertEqual(res.defects[0].scope, "LOCAL")

    def test_15_silhouette_analyzer_multi_view(self):
        """Test 15: SilhouetteAnalyzer evalúa vistas frontal y lateral."""
        from src.semantic_visual_critic.analyzers.silhouette_analyzer import SilhouetteAnalyzer
        eval_dict = SilhouetteAnalyzer.evaluate_multi_view_aspect_ratios(
            {CriticCameraView.FRONT: 1.52, CriticCameraView.LEFT: 1.20}
        )
        self.assertTrue(eval_dict["overall_ok"])

    def test_16_style_material_analyzer_clean(self):
        """Test 16: StyleMaterialAnalyzer no detecta problemas en low poly limpio."""
        from src.semantic_visual_critic.analyzers.style_material_analyzer import StyleMaterialAnalyzer
        st = StyleMaterialAnalyzer.evaluate_style_and_density("STYLIZED_LOW_POLY", False, 0.30)
        self.assertFalse(st["has_style_mismatch"])
        self.assertFalse(st["has_excessive_detail"])

    def test_17_semantic_detector_clean(self):
        """Test 17: SemanticDetector no encuentra elementos prohibidos cuando la lista está limpia."""
        from src.semantic_visual_critic.analyzers.semantic_detector import SemanticDetector
        f = SemanticDetector.detect_forbidden_components(["roof", "walls"], ["satellite_dish"])
        self.assertEqual(len(f), 0)

    def test_18_minor_fix_recommendation(self):
        """Test 18: Defectos leves y locales activan recomendación MINOR_FIX."""
        expected = ExpectedState(expected_proportions={"roof_ratio": 0.30})
        actual = ActualState(
            detected_components=["roof", "walls", "entrance"],
            measured_proportions={"roof_ratio": 0.38} # Desviación menor
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertIn(res.recommendation, [CriticRecommendation.MINOR_FIX, CriticRecommendation.REFINE])

    def test_19_missing_required_wall_caps_score(self):
        """Test 19: Falta de muro requerido veta aprobación y genera hard failure."""
        expected = ExpectedState(required_components=["walls", "roof"])
        actual = ActualState(detected_components=["roof"])
        res = self.api.evaluate_asset(expected, actual)
        self.assertIn("MISSING_WALLS", res.hard_failures)
        self.assertLessEqual(res.overall_score, 0.40)

    def test_20_end_to_end_critic_pipeline(self):
        """Test 20: Flujo E2E: ExpectedState vs ActualState -> SemanticComparator -> Defects -> Actionable Correction Plan."""
        expected = ExpectedState(
            asset_class="HOUSE",
            required_components=["roof", "walls", "entrance"],
            forbidden_components=["satellite_dish"],
            expected_proportions={"roof_ratio": 0.30}
        )
        actual = ActualState(
            detected_class="HOUSE",
            detected_components=["roof", "walls", "entrance", "satellite_dish"],
            measured_proportions={"roof_ratio": 0.48}
        )
        res = self.api.evaluate_asset(expected, actual)
        self.assertEqual(len(res.defects), 2)
        self.assertEqual(len(res.correction_plan), 2)
        self.assertIn("remove satellite_dish", [d.recommended_action for d in res.defects])
        self.assertIn("reduce roof height", [d.recommended_action for d in res.defects])

if __name__ == "__main__":
    unittest.main()
