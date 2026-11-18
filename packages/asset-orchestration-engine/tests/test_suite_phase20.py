import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    VisualEvaluationQAAPI, ExpectedVisualProfile, EvaluationSeverity,
    RepairScope, RegressionDetector, OscillationDetector
)

class TestVisualEvaluationQAPhase20(unittest.TestCase):
    def setUp(self):
        self.qa_api = VisualEvaluationQAAPI()

    def test_01_scale_mismatch_detection_scenario_141(self):
        """Test 1: Scenario 141 - Espada de 90cm que mide 1.34m produce SCALE_MISMATCH."""
        exp = ExpectedVisualProfile("sword_exp", target_dimensions={"length": 0.90})
        act = {"dimensions": {"length": 1.34}, "components": []}
        report = self.qa_api.evaluate("sword_001", act, exp)
        self.assertFalse(report.is_pass)
        self.assertEqual(len(report.failures), 1)
        self.assertEqual(report.failures[0].code, "SCALE_MISMATCH")
        self.assertEqual(report.failures[0].parameter_name, "length")

    def test_02_parameter_repair_plan_and_pass_scenario_142_143(self):
        """Test 2: Scenario 142-143 - Genera RepairPlan(scope=PARAMETER) y re-evaluación da PASS."""
        exp = ExpectedVisualProfile("sword_exp", target_dimensions={"length": 0.90})
        act = {"dimensions": {"length": 1.34}, "components": []}
        report = self.qa_api.evaluate("sword_001", act, exp)
        plan = self.qa_api.diagnose_and_plan_repair(report)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.candidates[0].scope, RepairScope.PARAMETER)

        # Aplicar reparación
        act["dimensions"]["length"] = plan.candidates[0].target_value
        report_after = self.qa_api.evaluate("sword_001", act, exp)
        self.assertTrue(report_after.is_pass)
        self.assertEqual(len(report_after.failures), 0)

    def test_03_spatial_relationship_failure_scenario_144(self):
        """Test 3: Scenario 144 - Torre al este de la plaza genera SPATIAL_RELATIONSHIP_FAILURE."""
        exp = ExpectedVisualProfile("scene_exp", expected_spatial_relations={"tower_001": "north_of plaza"})
        act = {"spatial_relations": {"tower_001": "east_of plaza"}}
        report = self.qa_api.evaluate("village_01", act, exp)
        self.assertFalse(report.is_pass)
        self.assertEqual(report.failures[0].code, "SPATIAL_RELATIONSHIP_FAILURE")

    def test_04_component_scoped_repair_scenario_145(self):
        """Test 4: Scenario 145 - Tejado demasiado alto (1.35m vs 0.80m) produce RepairScope.COMPONENT."""
        exp = ExpectedVisualProfile("house_exp")
        act = {"component_measurements": {"roof_height": 1.35}}
        report = self.qa_api.evaluate("house_003", act, exp)
        self.assertFalse(report.is_pass)
        self.assertEqual(report.failures[0].code, "PROPORTION_MISMATCH")
        self.assertEqual(report.failures[0].component_id, "roof")
        self.assertEqual(report.failures[0].suggested_scope, RepairScope.COMPONENT)

    def test_05_regression_detection_and_rejection_scenario_146(self):
        """Test 5: Scenario 146 - Reparación que mejora forma pero degrada escala es rechazada."""
        exp = ExpectedVisualProfile("sword_exp", target_dimensions={"length": 0.90})
        act_before = {"dimensions": {"length": 0.90}, "shape_score": 0.81}
        act_after = {"dimensions": {"length": 1.45}, "shape_score": 0.93}

        rep_before = self.qa_api.evaluate("sword_001", act_before, exp)
        rep_after = self.qa_api.evaluate("sword_001", act_after, exp)

        is_regr, msg = RegressionDetector.check_regression(rep_before, rep_after)
        self.assertTrue(is_regr)
        self.assertIn("REGRESSION_DETECTED", msg)

    def test_06_stagnation_stop_condition_scenario_147(self):
        """Test 6: Scenario 147 - Delta de mejora < 0.02 detiene con NO_MEANINGFUL_IMPROVEMENT."""
        history = [0.71, 0.76, 0.75, 0.75]
        is_stag, msg = OscillationDetector.check_stagnation_or_cycle(history, threshold=0.02)
        self.assertTrue(is_stag)
        self.assertIn("NO_MEANINGFUL_IMPROVEMENT", msg)

    def test_07_oscillation_detection(self):
        """Test 7: Oscillation - Detección de ciclo A -> B -> A -> B."""
        history = [0.70, 0.85, 0.70, 0.85]
        is_osc, msg = OscillationDetector.check_stagnation_or_cycle(history)
        self.assertTrue(is_osc)
        self.assertIn("REPAIR_OSCILLATION", msg)

    def test_08_semantic_missing_asset_detection(self):
        """Test 8: Semantic - Falta de escudo obligatorio produce MISSING_REQUIRED_ASSET."""
        exp = ExpectedVisualProfile("loadout_exp", expected_components=["sword", "shield"])
        act = {"components": ["sword"]}
        report = self.qa_api.evaluate("player_loadout", act, exp)
        self.assertFalse(report.is_pass)
        self.assertEqual(report.failures[0].code, "MISSING_REQUIRED_ASSET")
        self.assertEqual(report.failures[0].severity, EvaluationSeverity.CRITICAL)

    def test_09_technical_polycount_exceeded(self):
        """Test 9: Technical - Polycount > 10000 genera POLYCOUNT_EXCEEDED."""
        exp = ExpectedVisualProfile("prop_exp", target_polycount=5000)
        act = {"polycount": 12000}
        report = self.qa_api.evaluate("prop_01", act, exp)
        self.assertEqual(report.failures[0].code, "POLYCOUNT_EXCEEDED")

    def test_10_closed_loop_end_to_end_optimization(self):
        """Test 10: Closed Loop - Optimiza en bucle cerrado de 1 iteración pasando a ACCEPT."""
        exp = ExpectedVisualProfile("sword_exp", target_dimensions={"length": 0.90})
        initial_act = {"dimensions": {"length": 1.34}, "components": []}

        def dummy_repair(curr_data, candidate):
            updated = dict(curr_data)
            updated["dimensions"] = dict(curr_data.get("dimensions", {}))
            updated["dimensions"][candidate.parameter_name] = candidate.target_value
            return updated

        res = self.qa_api.optimize_closed_loop("sword_opt", initial_act, exp, dummy_repair)
        self.assertEqual(res["final_status"], "ACCEPT")
        self.assertEqual(res["iterations"], 1)
        self.assertTrue(res["last_report"].is_pass)

if __name__ == "__main__":
    unittest.main()
