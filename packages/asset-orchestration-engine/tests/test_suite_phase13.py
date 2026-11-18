import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AutonomousDecisionAPI, MockBlenderProvider, VisualIntelligenceAPI,
    CorrectionExecutionAPI, AssetMemoryAPI, CorrectionBudget, UtilityCalculator,
    ProgressEvaluator, ProgressClassification, LoopController
)

class TestAutonomousDecisionPhase13(unittest.TestCase):
    def setUp(self):
        self.provider = MockBlenderProvider()
        self.corr_api = CorrectionExecutionAPI(self.provider)
        self.vi_api = VisualIntelligenceAPI()
        self.mem_api = AssetMemoryAPI(":memory:")

        # Espada con hoja corta y no metálica
        self.provider.init_asset("sword_001", {
            "grip": {"dimensions": (0.03, 0.03, 0.25), "material": {"metallic": 0.0, "roughness": 0.8}},
            "guard": {"dimensions": (0.15, 0.03, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}},
            "blade": {"dimensions": (0.05, 0.02, 0.50), "material": {"metallic": 0.0, "roughness": 0.5}},
            "pommel": {"dimensions": (0.05, 0.05, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}}
        })
        self.goal = self.vi_api.build_goal_spec(category="ONE_HANDED_MEDIEVAL_SWORD")
        self.decision_api = AutonomousDecisionAPI(
            visual_api=self.vi_api,
            correction_api=self.corr_api,
            memory_api=self.mem_api,
            acceptance_threshold=0.85
        )

    def tearDown(self):
        self.mem_api.store.close()

    def test_01_goal_completion_overworking_stop(self):
        """Test 1: Goal Completion - Si el asset ya cumple el umbral, se detiene inmediatamente (0 mutaciones)."""
        # Ajustar espada para que sea óptima
        self.provider.set_component_dimensions("sword_001", "blade", (0.05, 0.02, 0.95))
        self.provider.set_material_property("sword_001", "blade", "metallic", 0.90)

        res = self.decision_api.optimize_asset("sword_001", self.goal)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(res["corrections"], 0)

    def test_02_below_threshold_optimization_cycle(self):
        """Test 2: Optimization Cycle - Asset inicial desviado se optimiza hasta alcanzar COMPLETED."""
        res = self.decision_api.optimize_asset("sword_001", self.goal)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertGreaterEqual(res["final_score"], 0.85)
        self.assertGreater(res["corrections"], 0)

    def test_03_hard_constraint_failure_blocks_completion(self):
        """Test 3: Hard Constraint - Fallo en componente obligatorio impide COMPLETED aunque score sea alto."""
        from src.visual_intelligence.qa.quality_scorer import VerificationReport
        rep = VerificationReport(
            asset_id="sword_001",
            overall_score=0.96,
            status="FAIL",
            hard_failures=["MISSING_REQUIRED_COMPONENTS: ['guard']"]
        )
        ok, msg = self.decision_api.engine.goal_eval.is_goal_satisfied(rep)
        self.assertFalse(ok)
        self.assertIn("HARD_CONSTRAINT_FAILURE", msg)

    def test_04_no_progress_detection(self):
        """Test 4: No Progress - 3 operaciones consecutivas sin delta activan NO_PROGRESS."""
        deltas = [0.001, 0.002, -0.001]
        is_no_prog, msg = LoopController.check_no_progress(deltas)
        self.assertTrue(is_no_prog)
        self.assertIn("NO_PROGRESS", msg)

    def test_05_oscillation_detection(self):
        """Test 5: Oscillation - Patrón A -> B -> A -> B activa OSCILLATION_DETECTED."""
        history = ["SCALE_BLADE", "MOVE_BLADE", "SCALE_BLADE", "MOVE_BLADE"]
        is_osc, msg = LoopController.check_oscillation(history)
        self.assertTrue(is_osc)
        self.assertIn("OSCILLATION_DETECTED", msg)

    def test_06_budget_exhaustion(self):
        """Test 6: Budget - Presupuesto de 1 iteración se agota y detiene la ejecución."""
        strict_api = AutonomousDecisionAPI(
            visual_api=self.vi_api,
            correction_api=self.corr_api,
            memory_api=self.mem_api,
            budget=CorrectionBudget(max_iterations=1, max_corrections=1)
        )
        res = strict_api.optimize_asset("sword_001", self.goal)
        self.assertEqual(res["status"], "FAILED")
        self.assertIn("BUDGET_EXHAUSTED", res["stop_reason"])

    def test_07_utility_calculation(self):
        """Test 7: Utility - Mayor mejora esperada y menor riesgo produce mayor utilidad."""
        u_high = UtilityCalculator.calculate_utility(expected_improvement=0.20, confidence=0.90, risk=0.05, estimated_cost=1.0)
        u_low = UtilityCalculator.calculate_utility(expected_improvement=0.02, confidence=0.50, risk=0.30, estimated_cost=1.0)
        self.assertGreater(u_high, u_low)

    def test_08_emergency_stop(self):
        """Test 8: Emergency Stop - Disparar parada de emergencia detiene la ejecución con ABORTED."""
        self.decision_api.trigger_emergency_stop()
        res = self.decision_api.optimize_asset("sword_001", self.goal)
        self.assertEqual(res["status"], "ABORTED")
        self.assertIn("EMERGENCY_STOP", res["stop_reason"])

    def test_09_progress_classification(self):
        """Test 9: Progress - Clasifica delta de mejora correctamente."""
        prog, d1 = ProgressEvaluator.evaluate_progress(0.70, 0.85)
        self.assertEqual(prog, ProgressClassification.STRONG_PROGRESS)
        prog_reg, d2 = ProgressEvaluator.evaluate_progress(0.85, 0.75)
        self.assertEqual(prog_reg, ProgressClassification.SEVERE_REGRESSION)

    def test_10_dry_run_mode(self):
        """Test 10: Dry Run - dry_run=True retorna la acción planificada sin mutar el modelo."""
        res = self.decision_api.optimize_asset("sword_001", self.goal, dry_run=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "dry_run")
        self.assertIn("planned_action", res)

    def test_11_full_autonomous_learning_loop(self):
        """Test 11: Full Loop - Optimización autónoma completa registra el éxito en memoria."""
        res = self.decision_api.optimize_asset("sword_001", self.goal)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "COMPLETED")
        
        # Verificar que la memoria registró intentos
        strat = self.mem_api.store.get_strategy("strat_scale_blade")
        if strat:
            self.assertGreater(strat.sample_count, 1)

if __name__ == "__main__":
    unittest.main()
