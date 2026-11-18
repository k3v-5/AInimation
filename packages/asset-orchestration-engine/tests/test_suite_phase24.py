import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    ParametricBuilderAPI, ParametricAssetType, BuildStage, BuildState,
    ParameterChange, ParameterFormulaEngine
)

class TestParametricBuilderPhase24(unittest.TestCase):
    def setUp(self):
        self.builder = ParametricBuilderAPI()

    def test_01_full_parametric_build_scenario_163(self):
        """Test 1: Scenario 163 - Construcción determinista completa de casa medieval."""
        params = {"width": 4.0, "depth": 3.5, "height": 5.0, "roof_angle": 38.0, "window_count": 4}
        res = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params)
        self.assertEqual(res.status, BuildState.COMPLETED)
        self.assertEqual(len(res.created_components), 4)
        self.assertIn("foundation", res.created_components)
        self.assertIn("walls", res.created_components)
        self.assertIn("roof", res.created_components)
        self.assertIn("windows", res.created_components)
        self.assertEqual(res.geometry_stats["vertex_count"], 200) # 24+48+64 + 4*16

    def test_02_local_rebuild_scenario_164(self):
        """Test 2: Scenario 164 - Modificar solo roof_height reconstruye únicamente el tejado."""
        initial_params = {"width": 4.0, "depth": 3.5, "height": 5.0, "roof_height": 1.75}
        self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, initial_params)

        changes = [ParameterChange("roof_height", 1.75, 2.10, operation="SET")]
        ok_upd, res_upd, logs = self.builder.update_parameters(
            ParametricAssetType.MEDIEVAL_HOUSE, initial_params, changes
        )
        self.assertTrue(ok_upd)
        self.assertEqual(res_upd.modified_components, ["roof"])

    def test_03_hard_dimension_precision_scenario_165(self):
        """Test 3: Scenario 165 - Ancho exacto de 4.0m respetado dentro de tolerancia."""
        params = {"width": 4.0, "depth": 3.5, "height": 5.0}
        res = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params)
        self.assertAlmostEqual(res.dimensions["width"], 4.00, delta=0.005)

    def test_04_automatic_dependency_recalculation_scenario_166(self):
        """Test 4: Scenario 166 - Cambiar width de 4m a 6m recalcula spacing, roof_width y foundation_width."""
        params = {"width": 6.0, "window_count": 4}
        res = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params)
        self.assertEqual(res.parameters["roof_width"], 6.40)
        self.assertEqual(res.parameters["foundation_width"], 6.20)
        self.assertEqual(res.parameters["window_spacing"], 1.6667) # (6-1)/3

    def test_05_invalid_parameter_rollback_scenario_167(self):
        """Test 5: Scenario 167 - roof_height = 10m >= height = 5m produce ROLLBACK."""
        initial_params = {"width": 4.0, "height": 5.0, "roof_height": 1.75}
        changes = [ParameterChange("roof_height", 1.75, 10.0, operation="SET")]
        ok_upd, res_upd, logs = self.builder.update_parameters(
            ParametricAssetType.MEDIEVAL_HOUSE, initial_params, changes
        )
        self.assertFalse(ok_upd)
        self.assertEqual(res_upd.status, BuildState.ROLLED_BACK)
        self.assertTrue(any("CROSS_PARAMETER_VIOLATION" in l for l in logs))

    def test_06_deterministic_build_fingerprint_scenario_168(self):
        """Test 6: Scenario 168 - Dos builds idénticos producen exactamente el mismo fingerprint."""
        params = {"width": 4.0, "depth": 3.5, "height": 5.0}
        res1 = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params, seed=42)
        res2 = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params, seed=42)
        self.assertEqual(res1.build_fingerprint, res2.build_fingerprint)

    def test_07_controlled_seed_variation_scenario_169(self):
        """Test 7: Scenario 169 - Mismo seed produce idéntico resultado."""
        params = {"width": 4.0, "depth": 3.5, "height": 5.0}
        resA = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params, seed=100)
        self.builder.cache.cache.clear()
        resB = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params, seed=100)
        self.assertEqual(resA.build_fingerprint, resB.build_fingerprint)

    def test_08_geometry_cache_hit_scenario_170(self):
        """Test 8: Scenario 170 - Construir configuración existente genera CACHE HIT."""
        params = {"width": 4.0, "depth": 3.5, "height": 5.0}
        res1 = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params)
        self.assertFalse(res1.is_cache_hit)

        res2 = self.builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params)
        self.assertTrue(res2.is_cache_hit)

    def test_09_progressive_blockout_gate_scenario_171(self):
        """Test 9: Scenario 171 - Fallo en Blockout detiene la construcción antes de detalles."""
        params = {"width": 4.0, "depth": 3.5, "height": 5.0}
        res = self.builder.build_parametric_asset(
            ParametricAssetType.MEDIEVAL_HOUSE, params, fail_blockout_check=True
        )
        self.assertEqual(res.status, BuildState.FAILED)
        self.assertEqual(res.stage_reached, BuildStage.BLOCKOUT)
        self.assertTrue(any("BLOCKOUT_SILHOUETTE_FAILED" in e for e in res.errors))

    def test_10_custom_geometry_fallback_scenario_172(self):
        """Test 10: Scenario 172 - Tipo no mapeado activa CUSTOM_GEOMETRY_FALLBACK."""
        res = self.builder.build_parametric_asset(ParametricAssetType.CUSTOM, {"mesh": "dragon_statue"})
        self.assertTrue(any("CUSTOM_GEOMETRY_FALLBACK" in e for e in res.errors))

    def test_11_relative_intent_parsing(self):
        """Test 11: Intent - 'hazla un 20% más ancha' sobre 4m produce 4.8m."""
        val = self.builder.parse_relative_intent(4.0, "hazla un 20% más ancha")
        self.assertEqual(val, 4.80)

    def test_12_formula_engine_safety(self):
        """Test 12: Formula - Evaluación segura de fórmulas y división por cero."""
        res = ParameterFormulaEngine.evaluate("(width - 2 * margin) / count", {"width": 10.0, "margin": 1.0, "count": 4.0})
        self.assertEqual(res, 2.0)

        # División por cero
        res_z = ParameterFormulaEngine.evaluate("width / count", {"width": 10.0, "count": 0.0})
        self.assertEqual(res_z, 0.0)

if __name__ == "__main__":
    unittest.main()
