import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    ProceduralTemplatesAPI, MockBlenderProvider, SpecificationCompilerAPI,
    VisualIntelligenceAPI, ConstructionDependencyGraph, ConstructionOperation
)

class TestProceduralTemplatesPhase15(unittest.TestCase):
    def setUp(self):
        self.provider = MockBlenderProvider()
        self.templates_api = ProceduralTemplatesAPI(self.provider)
        self.spec_api = SpecificationCompilerAPI()
        self.vi_api = VisualIntelligenceAPI()

    def test_01_template_matching_sword(self):
        """Test 1: Matching - AssetSpec(SWORD) selecciona weapon.sword.standard."""
        ok, spec, _ = self.spec_api.compile_request("Quiero una espada medieval de 120 cm")
        res = self.templates_api.build_from_spec("sword_test", spec)
        self.assertTrue(res["success"])
        self.assertEqual(res["template_id"], "weapon.sword.standard")
        self.assertEqual(res["construction_mode"], "TEMPLATE")

    def test_02_parameter_resolution(self):
        """Test 2: Parameter Resolution - Mapea 1.20m proporcionalmente a los componentes."""
        ok, spec, _ = self.spec_api.compile_request("Espada medieval de 120 cm")
        res = self.templates_api.build_from_spec("sword_test", spec)
        params = res["parameters"]
        self.assertEqual(params["total_length"], 1.20)
        self.assertEqual(params["blade_length"], 0.90)
        self.assertEqual(params["handle_length"], 0.216) # 18%

    def test_03_deterministic_construction(self):
        """Test 3: Construction - Inicializa 4 componentes en el provider."""
        ok, spec, _ = self.spec_api.compile_request("Espada de 120 cm")
        res = self.templates_api.build_from_spec("sword_01", spec)
        self.assertTrue(res["success"])
        comps = self.provider.assets["sword_01"]["components"]
        self.assertIn("blade", comps)
        self.assertIn("guard", comps)
        self.assertIn("grip", comps)
        self.assertIn("pommel", comps)

    def test_04_constraint_solver_rejection(self):
        """Test 4: Constraint solver - Rechaza blade_length <= handle_length."""
        ok, spec, _ = self.spec_api.compile_request("Espada de 120 cm")
        # Forzar parámetros inválidos
        template, _ = self.templates_api.registry.match_template(spec)
        invalid_params = {"blade_length": 0.10, "handle_length": 0.30}
        from src.procedural_templates.solver.constraint_solver import ParameterConstraintSolver
        ok_c, msg = ParameterConstraintSolver.validate_and_solve(invalid_params)
        self.assertFalse(ok_c)
        self.assertIn("RELATIONAL_CONSTRAINT_VIOLATION", msg)

    def test_05_dry_run_mode(self):
        """Test 5: Dry Run - dry_run=True no inicializa el asset en el provider."""
        ok, spec, _ = self.spec_api.compile_request("Espada de 120 cm")
        res = self.templates_api.build_from_spec("sword_dry", spec, dry_run=True)
        self.assertTrue(res["success"])
        self.assertNotIn("sword_dry", self.provider.assets)

    def test_06_partial_rebuild_isolation(self):
        """Test 6: Partial rebuild - Modifica únicamente la hoja preservando grip y guard."""
        ok, spec, _ = self.spec_api.compile_request("Espada de 120 cm")
        self.templates_api.build_from_spec("sword_01", spec)
        grip_dims_before = self.provider.assets["sword_01"]["components"]["grip"]["dimensions"]

        ok_patch, msg = self.templates_api.apply_parameter_patch("sword_01", "blade", "blade_length", 1.05)
        self.assertTrue(ok_patch)
        blade_dims_after = self.provider.assets["sword_01"]["components"]["blade"]["dimensions"]
        grip_dims_after = self.provider.assets["sword_01"]["components"]["grip"]["dimensions"]

        self.assertEqual(blade_dims_after[2], 1.05)
        self.assertEqual(grip_dims_before, grip_dims_after) # Intacto

    def test_07_circular_dependency_detection(self):
        """Test 7: Circular dependency - Ciclos en operaciones devuelven INVALID_CONSTRUCTION_GRAPH."""
        ops = [
            ConstructionOperation("op_1", "CREATE", "blade", {}, ["op_2"]),
            ConstructionOperation("op_2", "CREATE", "guard", {}, ["op_1"])
        ]
        ok_sort, _, msg = ConstructionDependencyGraph.sort_operations(ops)
        self.assertFalse(ok_sort)
        self.assertIn("INVALID_CONSTRUCTION_GRAPH", msg)

    def test_08_budget_exhaustion(self):
        """Test 8: Budget - Plan que excede max_operations_budget es bloqueado."""
        strict_api = ProceduralTemplatesAPI(self.provider, max_operations_budget=2)
        ok, spec, _ = self.spec_api.compile_request("Espada de 120 cm")
        res = strict_api.build_from_spec("sword_budget", spec)
        self.assertFalse(res["success"])
        self.assertIn("CONSTRUCTION_BUDGET_EXCEEDED", res["message"])

    def test_09_ai_fallback_for_unknown_asset(self):
        """Test 9: AI Fallback - Asset sin plantilla devuelve AI_FALLBACK."""
        from src.spec_compiler.core.asset_spec import AssetSpec
        unknown_spec = AssetSpec(spec_id="spec_unk", asset_type="FLYING_DRAGON")
        res = self.templates_api.build_from_spec("dragon_01", unknown_spec)
        self.assertFalse(res["success"])
        self.assertEqual(res["construction_mode"], "AI_FALLBACK")

    def test_10_end_to_end_spec_to_builder_to_qa(self):
        """Test 10: Full Pipeline - Spec -> Template -> Builder -> Visual QA verifica score >= 0.85."""
        ok, spec, _ = self.spec_api.compile_request("Quiero una espada medieval estilizada de 120 cm con hoja ancha y guardia metálica")
        res = self.templates_api.build_from_spec("sword_e2e", spec)
        self.assertTrue(res["success"])

        # Verificar en Visual QA (Fase 10)
        comps = self.provider.assets["sword_e2e"]["components"]
        dims = {k: v["dimensions"] for k, v in comps.items()}
        mats = {k: v.get("material", {}) for k, v in comps.items()}
        goal = self.vi_api.build_goal_spec(category="ONE_HANDED_MEDIEVAL_SWORD")
        report = self.vi_api.verify_asset("sword_e2e", dims, list(comps.keys()), materials=mats, goal_spec=goal)
        self.assertGreaterEqual(report.overall_score, 0.85)

if __name__ == "__main__":
    unittest.main()
