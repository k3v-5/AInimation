import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_reference_matching import (
    VisualReferenceMatcherAPI, VisualDiagnosisType, CriticDecisionType,
    EvaluationMode
)
from src.parametric_asset_engine import ParametricAssetAPI

class TestVisualReferenceMatchingPhase41(unittest.TestCase):
    def setUp(self):
        self.api = VisualReferenceMatcherAPI()
        self.param_api = ParametricAssetAPI()
        self.ref = self.api.create_reference_spec(
            image_id="REF_HOUSE_001",
            expected_aspect_ratio=1.52,
            expected_roof_ratio=0.31,
            expected_components={"chimney": True},
            expected_colors={"walls": [50.0, 0.0, 0.0]}
        )

    def test_01_acceptance_1_silhouette_iou_and_aspect_ratio(self):
        """Acceptance Test 1: Cálculo de IoU y error de relación de aspecto (+0.28)."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 9.0}, generated_aspect_ratio=1.80, generated_roof_ratio=0.31)
        self.assertAlmostEqual(rep.explainability["how_much"].count("Aspect ratio error: +0.28"), 1)

    def test_02_acceptance_2_diagnostic_too_wide(self):
        """Acceptance Test 2: Error de ancho detecta diagnóstico TOO_WIDE."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 9.0}, generated_aspect_ratio=1.80, generated_roof_ratio=0.31)
        self.assertTrue(any(d.diag_type == VisualDiagnosisType.TOO_WIDE for d in rep.diagnoses))

    def test_03_acceptance_3_diagnostic_roof_too_high(self):
        """Acceptance Test 3: Ratio de tejado excesivo detecta diagnóstico ROOF_TOO_HIGH."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"roof_height": 2.0}, generated_aspect_ratio=1.52, generated_roof_ratio=0.43)
        self.assertTrue(any(d.diag_type == VisualDiagnosisType.ROOF_TOO_HIGH for d in rep.diagnoses))

    def test_04_acceptance_4_exact_parameter_correction_width(self):
        """Acceptance Test 4: Corrección de ancho calcula matemáticamente 9.0m * (1.52 / 1.80) = 7.60m."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 9.0}, generated_aspect_ratio=1.80, generated_roof_ratio=0.31)
        w_corr = next(c for c in rep.suggested_corrections if c.parameter_name == "width")
        self.assertEqual(w_corr.suggested_value, 7.60)
        self.assertEqual(w_corr.delta, -1.40)

    def test_05_acceptance_5_exact_parameter_correction_roof_height(self):
        """Acceptance Test 5: Corrección de techo calcula 2.0m * (0.31 / 0.43) = 1.44m."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"roof_height": 2.0}, generated_aspect_ratio=1.52, generated_roof_ratio=0.43)
        r_corr = next(c for c in rep.suggested_corrections if c.parameter_name == "roof_height")
        self.assertEqual(r_corr.suggested_value, 1.44)
        self.assertEqual(r_corr.delta, -0.56)

    def test_06_acceptance_6_bounded_correction_replan_guard(self):
        """Acceptance Test 6: Cambio relativo > 20% (-28%) activa replan_required = True."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"roof_height": 2.0}, generated_aspect_ratio=1.52, generated_roof_ratio=0.43)
        r_corr = next(c for c in rep.suggested_corrections if c.parameter_name == "roof_height")
        self.assertTrue(r_corr.replan_required)
        self.assertEqual(rep.decision, CriticDecisionType.REPLAN)

    def test_07_acceptance_7_user_intent_priority_window_count(self):
        """Acceptance Test 7: Conteo pedido por usuario (4) prevalece sobre la referencia."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"window_count": 4}, generated_aspect_ratio=1.52, generated_roof_ratio=0.31, user_window_count=4)
        self.assertEqual(rep.sub_scores["components"], 1.0)

    def test_08_acceptance_8_missing_component_detection(self):
        """Acceptance Test 8: Ausencia de chimenea detecta COMPONENT_MISSING."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 7.6}, generated_aspect_ratio=1.52, generated_roof_ratio=0.31, has_chimney=False)
        self.assertTrue(any(d.diag_type == VisualDiagnosisType.COMPONENT_MISSING for d in rep.diagnoses))

    def test_09_acceptance_9_material_cielab_delta_e(self):
        """Acceptance Test 9: Cálculo de Delta E en espacio Lab en modo DEEP."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 7.6}, generated_aspect_ratio=1.52, generated_roof_ratio=0.31, mode=EvaluationMode.DEEP)
        self.assertGreater(rep.sub_scores["material"], 0.90)

    def test_10_acceptance_10_fast_mode_skips_deep_materials(self):
        """Acceptance Test 10: Modo FAST evalúa silueta y componentes sin análisis pesado."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 7.6}, generated_aspect_ratio=1.52, generated_roof_ratio=0.31, mode=EvaluationMode.FAST)
        self.assertEqual(rep.sub_scores["material"], 1.0)

    def test_11_acceptance_11_deep_mode_includes_lab_analysis(self):
        """Acceptance Test 11: Modo DEEP ejecuta análisis completo."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 7.6}, generated_aspect_ratio=1.52, generated_roof_ratio=0.31, mode=EvaluationMode.DEEP)
        self.assertIn("material", rep.sub_scores)

    def test_12_acceptance_12_decision_state_correct(self):
        """Acceptance Test 12: Desviación moderada emite decisión CORRECT."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 8.5}, generated_aspect_ratio=1.65, generated_roof_ratio=0.31)
        self.assertEqual(rep.decision, CriticDecisionType.CORRECT)

    def test_13_acceptance_13_decision_state_accept_matching_model(self):
        """Acceptance Test 13: Modelo que coincide con silueta y proporciones emite ACCEPT."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 7.6, "window_count": 4}, generated_aspect_ratio=1.52, generated_roof_ratio=0.31, user_window_count=4, has_chimney=True)
        self.assertEqual(rep.decision, CriticDecisionType.ACCEPT)

    def test_14_acceptance_14_explainability_completeness(self):
        """Acceptance Test 14: Informe contiene qué, dónde, cuánto y por qué."""
        rep = self.api.evaluate_asset("HOUSE_001", self.ref, {"width": 9.0}, generated_aspect_ratio=1.80, generated_roof_ratio=0.31)
        exp = rep.explainability
        self.assertIn("what", exp)
        self.assertIn("where", exp)
        self.assertIn("how_much", exp)
        self.assertIn("why", exp)

    def test_15_acceptance_15_oscillation_detection(self):
        """Acceptance Test 15: Detección de oscilación en historial de evaluación."""
        history = [0.75, 0.85, 0.74, 0.84]
        self.assertTrue(self.api.detect_oscillation(history))

    def test_16_acceptance_16_e2e_parametric_feedback_loop(self):
        """Acceptance Test 16: Feedback loop completo: Critic propone corrección y motor paramétrico actualiza solo lo afectado."""
        house = self.param_api.create_asset("H_FEEDBACK", {"width": 9.0, "roof_height": 2.0})
        rep = self.api.evaluate_asset("H_FEEDBACK", self.ref, house.parameters, generated_aspect_ratio=1.80, generated_roof_ratio=0.43)
        
        # Extraer corrección de ancho sugerida (-1.40m -> 7.60m)
        w_corr = next(c for c in rep.suggested_corrections if c.parameter_name == "width")
        updated_house = self.param_api.update_asset("H_FEEDBACK", {"width": w_corr.suggested_value})
        self.assertEqual(updated_house.parameters["width"], 7.60)

if __name__ == "__main__":
    unittest.main()
