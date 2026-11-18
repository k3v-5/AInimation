import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    VisualIntelligenceAPI, VisualGoalSpec, QualityScorer, QualityWeights
)

class TestVisualIntelligencePhase10(unittest.TestCase):
    def setUp(self):
        self.vi_api = VisualIntelligenceAPI()

    def test_01_incorrect_model_hard_constraint_failure(self):
        """Test 1: Modelo Incorrecto - Espada de dos manos sin componentes requeridos produce FAIL."""
        goal = self.vi_api.build_goal_spec(
            category="ONE_HANDED_MEDIEVAL_SWORD",
            required_components=["blade", "guard", "grip", "pommel"]
        )
        # Generado: solo blade gigante sin guarda
        report = self.vi_api.verify_asset(
            asset_id="sword_two_handed",
            component_dimensions={"blade": (0.1, 0.05, 1.80)},
            present_components=["blade", "grip"], # Falta guard y pommel
            goal_spec=goal
        )
        self.assertEqual(report.status, "FAIL")
        self.assertGreater(len(report.hard_failures), 0)
        self.assertIn("MISSING_REQUIRED_COMPONENTS", report.hard_failures[0])

    def test_02_partially_correct_model_known_good_parts(self):
        """Test 2: Modelo Parcialmente Correcto - Mango y guarda válidos, hoja corta produce corrección local."""
        goal = self.vi_api.build_goal_spec()
        # Hoja mide 0.35m sobre un total de 0.70m (50% vs target 72%)
        dims = {"handle": (0.03, 0.03, 0.25), "guard": (0.15, 0.03, 0.05), "blade": (0.05, 0.02, 0.35), "pommel": (0.05, 0.05, 0.05)}
        report = self.vi_api.verify_asset(
            asset_id="sword_short_blade",
            component_dimensions=dims,
            present_components=["blade", "guard", "grip", "pommel"],
            goal_spec=goal
        )
        self.assertIn(report.status, ["NEEDS_CORRECTION", "PASS_WITH_WARNINGS"])
        
        plan = self.vi_api.plan_correction(report)
        self.assertEqual(plan["action"], "EXECUTE_CORRECTIONS")
        self.assertEqual(plan["actions"][0]["target_component"], "blade")
        self.assertIn("guard", plan["preserved_components"])

    def test_03_incorrect_material_correction(self):
        """Test 3: Material Incorrecto - Geometría válida pero metallic=0.0 genera corrección de material."""
        goal = self.vi_api.build_goal_spec()
        dims = {"handle": (0.03, 0.03, 0.25), "guard": (0.15, 0.03, 0.05), "blade": (0.05, 0.02, 0.95), "pommel": (0.05, 0.05, 0.05)}
        materials = {"blade": {"metallic": 0.0, "roughness": 0.5}} # No metálico
        report = self.vi_api.verify_asset(
            asset_id="sword_non_metallic",
            component_dimensions=dims,
            present_components=["blade", "guard", "grip", "pommel"],
            materials=materials,
            goal_spec=goal
        )
        self.assertTrue(any("MATERIAL_METALLIC_MISMATCH" in w for w in report.warnings))

    def test_04_no_op_when_goal_satisfied(self):
        """Test 4: NO_OP - Dimensiones y componentes óptimos producen PASS sin corrección."""
        goal = self.vi_api.build_goal_spec()
        # Hoja = 0.95m sobre total 1.30m (73% ≈ target 72%)
        dims = {"handle": (0.03, 0.03, 0.25), "guard": (0.15, 0.03, 0.05), "blade": (0.05, 0.02, 0.95), "pommel": (0.05, 0.05, 0.05)}
        materials = {"blade": {"metallic": 0.90, "roughness": 0.25}}
        report = self.vi_api.verify_asset(
            asset_id="sword_optimal",
            component_dimensions=dims,
            present_components=["blade", "guard", "grip", "pommel"],
            materials=materials,
            goal_spec=goal
        )
        self.assertEqual(report.status, "PASS")
        plan = self.vi_api.plan_correction(report)
        self.assertEqual(plan["action"], "NONE")

    def test_05_forbidden_components_detected(self):
        """Test 5: Forbidden components - Presencia de alas o cristales genera fallo."""
        goal = self.vi_api.build_goal_spec(forbidden_components=["wings", "fire_fx"])
        report = self.vi_api.verify_asset(
            asset_id="sword_with_wings",
            component_dimensions={"blade": (0.05, 0.02, 0.95)},
            present_components=["blade", "guard", "grip", "pommel", "wings"],
            goal_spec=goal
        )
        self.assertEqual(report.status, "FAIL")
        self.assertTrue(any("FORBIDDEN_COMPONENTS_DETECTED" in f for f in report.hard_failures))

    def test_06_evidence_generation_measured_vs_target(self):
        """Test 6: Structured evidence - El reporte contiene mediciones exactas y tolerancias."""
        goal = self.vi_api.build_goal_spec()
        dims = {"handle": (0.03, 0.03, 0.25), "guard": (0.15, 0.03, 0.05), "blade": (0.05, 0.02, 0.40)}
        report = self.vi_api.verify_asset("sword_ev", dims, ["blade", "guard", "grip", "pommel"], goal_spec=goal)
        ev = report.evidence.get("proportion", {})
        self.assertIn("measured_blade_ratio", ev)
        self.assertIn("target", ev)

    def test_07_quality_weights_formula(self):
        """Test 7: Quality weights - Verifica la ponderación matemática."""
        metrics = {"silhouette": 1.0, "proportion": 0.8, "components": 1.0, "material": 1.0, "color": 1.0, "style": 1.0, "geometry": 1.0}
        report = QualityScorer.calculate_score("asset_q", metrics, [], [], {})
        # Overall = 0.25(1) + 0.20(0.8) + 0.20(1) + 0.10(1) + 0.05(1) + 0.10(1) + 0.10(1) = 0.25 + 0.16 + 0.20 + 0.10 + 0.05 + 0.10 + 0.10 = 0.96
        self.assertEqual(report.overall_score, 0.96)
        self.assertEqual(report.status, "PASS")

    def test_08_hard_constraint_override(self):
        """Test 8: Hard constraint override - Si hay hard failure, el estado es FAIL aunque el score sea 0.95."""
        metrics = {"silhouette": 1.0, "proportion": 1.0, "components": 1.0, "material": 1.0, "color": 1.0, "style": 1.0, "geometry": 1.0}
        report = QualityScorer.calculate_score("asset_hard", metrics, ["MISSING_GUARD"], [], {})
        self.assertEqual(report.status, "FAIL")

if __name__ == "__main__":
    unittest.main()
