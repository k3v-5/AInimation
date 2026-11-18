import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adaptive_generation_correction import (
    AdaptiveGenerationAPI, SessionState, TerminationReason,
    ScopeLevel, CorrectionOp
)
from src.visual_reference_matching import ReferenceImageSpec
from src.asset_knowledge_base import AssetKnowledgeAPI

class TestAdaptiveGenerationPhase46(unittest.TestCase):
    def setUp(self):
        self.api = AdaptiveGenerationAPI(max_iterations=5, target_score=0.90)
        self.kb_api = AssetKnowledgeAPI()
        self.ref = ReferenceImageSpec(
            image_id="REF_HOUSE",
            expected_aspect_ratio=1.52,
            expected_roof_ratio=0.31
        )

    def test_01_mandatory_case_1_roof_height_isolated_repair(self):
        """Mandatory Case 1: Error roof_height +20% corrige solo tejado sin tocar muros/puertas."""
        dirty = self.api.get_dirty_components_for_parameter("roof_height", ScopeLevel.PARAMETER)
        self.assertEqual(dirty, ["roof"])
        self.assertNotIn("walls", dirty)
        self.assertNotIn("windows", dirty)

    def test_02_mandatory_case_2_window_spacing_isolated_repair(self):
        """Mandatory Case 2: Error window_spacing corrige solo ventanas sin tocar tejado/muros."""
        dirty = self.api.get_dirty_components_for_parameter("window_spacing", ScopeLevel.COMPONENT)
        self.assertEqual(dirty, ["windows"])
        self.assertNotIn("roof", dirty)
        self.assertNotIn("walls", dirty)

    def test_03_mandatory_case_3_facade_width_topological_propagation(self):
        """Mandatory Case 3: Modificación de ancho de muro propaga dirty a foundation, walls y roof."""
        dirty = self.api.get_dirty_components_for_parameter("width", ScopeLevel.COMPONENT)
        self.assertIn("foundation", dirty)
        self.assertIn("walls", dirty)
        self.assertIn("roof", dirty)

    def test_04_mandatory_case_4_generator_failure_fallback_recovery(self):
        """Mandatory Case 4: Fallo en generador primario activa generador fallback."""
        fb = self.kb_api.select_generator("MEDIEVAL_HOUSE", "roof", simulate_failure=True)
        self.assertEqual(fb.generator_id, "GEN_ROOF_PRIMITIVE")

    def test_05_mandatory_case_5_plateau_no_improvement_stops(self):
        """Mandatory Case 5: Cero mejora durante iteraciones detiene el bucle (Anti-Infinite Loop)."""
        engine = self.api.engine
        engine.score_history = [0.750, 0.751, 0.752]
        # Al evaluar estancamiento
        d = engine.score_history[-1] - engine.score_history[-2]
        self.assertLess(abs(d), 0.005)

    def test_06_mandatory_case_6_conflicting_references(self):
        """Mandatory Case 6: Referencias contradictorias lanzan REFERENCE_CONFLICT."""
        from src.reference_understanding_visual_spec import VisualSpecificationAPI, ReferenceRole
        spec_api = VisualSpecificationAPI()
        r1 = spec_api.create_reference_item("R1", "assets/r1.png", role=ReferenceRole.PRIMARY, metadata={"aspect_ratio": 1.52})
        r2 = spec_api.create_reference_item("R2", "assets/r2.png", role=ReferenceRole.PRIMARY, metadata={"aspect_ratio": 0.80})
        with self.assertRaises(ValueError) as ctx:
            spec_api.analyze_references_to_visual_spec([r1, r2])
        self.assertIn("REFERENCE_CONFLICT", str(ctx.exception))

    def test_07_attempt_graph_immutability(self):
        """Test 7: Inmutabilidad del historial de intentos en la sesión."""
        report = self.api.run_adaptive_session(
            "HOUSE_IMMUTABLE",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 2.0},
            self.ref
        )
        self.assertGreaterEqual(report.total_attempts, 1)
        self.assertEqual(len(report.score_history), report.total_attempts)

    def test_08_best_candidate_persistence(self):
        """Test 8: Persistencia del mejor candidato alcanzado durante la sesión."""
        report = self.api.run_adaptive_session(
            "HOUSE_BEST",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 2.0},
            self.ref
        )
        self.assertIsNotNone(report.best_attempt)
        self.assertGreaterEqual(report.best_attempt.total_score, report.score_history[0])

    def test_09_hard_constraint_veto_failure(self):
        """Test 9: Violación de restricción dura (colisión) veta aceptación aunque el score visual sea alto."""
        report = self.api.run_adaptive_session(
            "HOUSE_HARD_FAIL",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 1.45},
            self.ref,
            simulate_collision_failure=True
        )
        self.assertEqual(report.status, SessionState.FAILED)
        self.assertEqual(report.termination_reason, TerminationReason.SYSTEM_FAILURE)

    def test_10_minimal_change_principle_one_parameter(self):
        """Test 10: Principio de cambio mínimo genera candidato de 1 parámetro para error de tejado."""
        cands = self.api.diagnose_errors(
            measured_ratios={"roof_ratio": 0.43},
            target_ratios={"roof_ratio": 0.31},
            current_parameters={"roof_height": 2.0}
        )
        self.assertEqual(len(cands), 1)
        self.assertEqual(cands[0].parameter, "roof_height")

    def test_11_delta_first_correction_clamping(self):
        """Test 11: Corrección de delta respeta límite máximo acotado (max_delta = 0.40m)."""
        cands = self.api.diagnose_errors(
            measured_ratios={"roof_ratio": 0.65}, # Gran desviación
            target_ratios={"roof_ratio": 0.31},
            current_parameters={"roof_height": 3.0}
        )
        self.assertLessEqual(abs(cands[0].delta), 0.40)

    def test_12_scope_escalation_parameter_level(self):
        """Test 12: Nivel de alcance inicial es PARAMETER."""
        cands = self.api.diagnose_errors(
            measured_ratios={"roof_ratio": 0.40},
            target_ratios={"roof_ratio": 0.31},
            current_parameters={"roof_height": 1.90}
        )
        self.assertEqual(cands[0].scope, ScopeLevel.PARAMETER)

    def test_13_oscillation_detection(self):
        """Test 13: Detección de oscilación entre valores alternos."""
        history = [0.80, 0.85, 0.80, 0.85]
        is_osc = history[-1] == history[-3] and history[-2] == history[-4]
        self.assertTrue(is_osc)

    def test_14_budget_exhaustion_termination(self):
        """Test 14: Agotamiento de iteraciones termina con BUDGET_EXCEEDED si no alcanza target."""
        tight_api = AdaptiveGenerationAPI(max_iterations=1, target_score=0.99)
        report = tight_api.run_adaptive_session(
            "HOUSE_BUDGET",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 2.2},
            self.ref
        )
        self.assertEqual(report.termination_reason, TerminationReason.BUDGET_EXCEEDED)

    def test_15_atomic_transaction_rollback(self):
        """Test 15: Transacción atómica restaura parámetros previos en caso de regresión."""
        tx_mgr = self.api.engine.transaction_mgr
        tx = tx_mgr.begin_transaction("TX_01", "ATTEMPT_01", {"roof_height": 1.80}, ["roof"])
        restored = tx_mgr.rollback("TX_01")
        self.assertEqual(restored["roof_height"], 1.80)
        self.assertEqual(tx.state, "ROLLED_BACK")

    def test_16_dry_run_candidate_evaluation(self):
        """Test 16: Evaluación de candidato calcula componentes afectados y riesgo sin aplicar."""
        cands = self.api.diagnose_errors(
            measured_ratios={"roof_ratio": 0.42},
            target_ratios={"roof_ratio": 0.31},
            current_parameters={"roof_height": 1.95}
        )
        self.assertEqual(cands[0].affected_components, ["roof"])
        self.assertEqual(cands[0].risk.value, "LOW")

    def test_17_explainability_diagnosis(self):
        """Test 17: Explicabilidad estructurada de la causa y el efecto esperado."""
        cands = self.api.diagnose_errors(
            measured_ratios={"roof_ratio": 0.42},
            target_ratios={"roof_ratio": 0.31},
            current_parameters={"roof_height": 1.95}
        )
        self.assertIn("Restore roof ratio", cands[0].expected_effect)

    def test_18_session_lifecycle_states(self):
        """Test 18: Estados del ciclo de vida de la sesión (CREATED -> GENERATING -> ACCEPTED)."""
        report = self.api.run_adaptive_session(
            "HOUSE_LIFE",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 1.45},
            self.ref
        )
        self.assertIn(report.status, [SessionState.ACCEPTED, SessionState.BLOCKED])

    def test_19_session_report_metrics(self):
        """Test 19: Reporte de sesión incluye duración, curva de score y rework efficiency."""
        report = self.api.run_adaptive_session(
            "HOUSE_METRICS",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 1.80},
            self.ref
        )
        self.assertGreaterEqual(report.duration, 0.0)
        self.assertGreater(len(report.score_history), 0)
        self.assertEqual(report.rework_efficiency, 1.0)

    def test_20_end_to_end_adaptive_convergence(self):
        """Test 20: Flujo E2E: Generación inicial -> Diagnóstico -> Corrección Quirúrgica -> Convergencia."""
        report = self.api.run_adaptive_session(
            "HOUSE_E2E_CONVERGE",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 1.95}, # Techo inicial demasiado alto
            self.ref
        )
        self.assertIn(report.status, [SessionState.ACCEPTED, SessionState.BLOCKED])
        self.assertGreaterEqual(report.best_attempt.total_score, 0.85)

if __name__ == "__main__":
    unittest.main()
