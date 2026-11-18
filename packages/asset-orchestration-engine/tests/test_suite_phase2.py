import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetOrchestrationEngine, ChangeBudget, ScopeSpec, UnitNormalizer, DimensionsSpec
)

class TestAssetOrchestrationPhase2(unittest.TestCase):
    def setUp(self):
        self.engine = AssetOrchestrationEngine()

    def test_01_creation_from_natural_language(self):
        """Test 1: Creación - 'Crea un cubo de 1m'."""
        plan_res = self.engine.plan_intent("Crea un cubo de 1m", active_asset_id="cube_nl_01")
        self.assertTrue(plan_res["success"])
        self.assertEqual(plan_res["intent"]["intent_type"], "CREATE_ASSET")
        self.assertEqual(plan_res["operations_count"], 1)
        self.assertEqual(plan_res["operations"][0]["operation_type"], "CREATE_COMPONENT")

    def test_02_exact_modification(self):
        """Test 2: Modificación exacta - 'Hazlo de 2m'."""
        # Setup: crear cubo de 1m
        self.engine.create_asset({
            "asset_id": "cube_mod_01",
            "name": "Cube",
            "components": [{"id": "body", "type": "mesh", "primitive": "box", "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0}}]
        })

        # Planificar cambio exacto a 2m
        plan_res = self.engine.plan_intent("Hazlo de 2m", active_asset_id="cube_mod_01")
        self.assertTrue(plan_res["success"])
        self.assertEqual(plan_res["operations_count"], 1)
        op = plan_res["operations"][0]
        self.assertEqual(op["operation_type"], "SET_DIMENSIONS")
        self.assertEqual(op["parameters"]["value"][2], 2.0) # height = 2.0

    def test_03_relative_increment(self):
        """Test 3: Incremento - 'Agrega 20cm'."""
        self.engine.create_asset({
            "asset_id": "sword_inc",
            "name": "Sword",
            "components": [{"id": "blade", "type": "blade", "primitive": "box", "dimensions": {"width": 0.05, "depth": 0.02, "height": 0.85}}]
        })

        plan_res = self.engine.plan_intent("Agrega 20cm a la hoja", active_asset_id="sword_inc")
        self.assertTrue(plan_res["success"])
        op = plan_res["operations"][0]
        self.assertEqual(op["operation_type"], "SET_DIMENSIONS")
        # 0.85 + 0.20 = 1.05
        self.assertAlmostEqual(op["parameters"]["value"][2], 1.05, places=4)

    def test_04_percentage_multiply(self):
        """Test 4: Porcentaje - 'Hazlo 20% más grande'."""
        self.engine.create_asset({
            "asset_id": "barrel_pct",
            "name": "Barrel",
            "components": [{"id": "body", "type": "body", "primitive": "cylinder", "dimensions": {"width": 0.5, "depth": 0.5, "height": 1.0}}]
        })

        plan_res = self.engine.plan_intent("Haz la hoja 20% mas larga", active_asset_id="barrel_pct")
        # En barrel el único componente es body, target resolver resolverá body si se pide la forma general
        plan_res2 = self.engine.plan_intent("Hazlo 20% mas grande", active_asset_id="barrel_pct")
        self.assertTrue(plan_res2["success"])
        op = plan_res2["operations"][0]
        # 1.0 * 1.20 = 1.20
        self.assertAlmostEqual(op["parameters"]["value"][2], 1.20, places=4)

    def test_05_no_op_detection(self):
        """Test 5: No-op - 'Déjalo en 2m' cuando ya mide 2m."""
        self.engine.create_asset({
            "asset_id": "pillar_01",
            "name": "Pillar",
            "components": [{"id": "body", "type": "mesh", "primitive": "cylinder", "dimensions": {"width": 0.4, "depth": 0.4, "height": 2.0}}]
        })

        plan_res = self.engine.plan_intent("Déjalo en 2m", active_asset_id="pillar_01")
        self.assertTrue(plan_res["success"])
        self.assertTrue(plan_res["is_no_op"])
        self.assertEqual(plan_res["operations"][0]["operation_type"], "NO_OP")

    def test_06_target_ambiguity(self):
        """Test 6: Ambigüedad - Dos objetos llamados hoja (blade_left, blade_right)."""
        self.engine.create_asset({
            "asset_id": "dual_dagger",
            "name": "Dual Daggers",
            "components": [
                {"id": "blade_left", "type": "blade", "primitive": "box", "dimensions": {"width": 0.04, "depth": 0.02, "height": 0.40}},
                {"id": "blade_right", "type": "blade", "primitive": "box", "dimensions": {"width": 0.04, "depth": 0.02, "height": 0.40}}
            ]
        })

        plan_res = self.engine.plan_intent("Alarga la hoja 10cm", active_asset_id="dual_dagger")
        self.assertFalse(plan_res["success"])
        self.assertIn("AMBIGUOUS_TARGET", plan_res["error_message"])

    def test_07_scope_violation(self):
        """Test 7: Scope - Petición para modificar objeto fuera del scope."""
        self.engine.create_asset({
            "asset_id": "sword_scope",
            "name": "Sword",
            "components": [
                {"id": "blade", "type": "blade", "primitive": "box", "dimensions": {"width": 0.05, "depth": 0.02, "height": 0.85}},
                {"id": "handle", "type": "handle", "primitive": "cylinder", "dimensions": {"width": 0.04, "depth": 0.04, "height": 0.25}}
            ]
        })

        # Scope que solo permite modificar 'blade'
        scope = ScopeSpec(asset_ids=["sword_scope"], allowed_components=["blade"])
        plan_res = self.engine.plan_intent("Alarga el mango 10cm", active_asset_id="sword_scope", scope=scope)
        self.assertFalse(plan_res["success"])
        self.assertIn("SCOPE_VIOLATION", plan_res["error_message"])

    def test_08_destructive_operation_not_allowed(self):
        """Test 8: Destructive operation - Intentar borrar cuando allow_delete = false."""
        self.engine.create_asset({
            "asset_id": "prop_del",
            "name": "Prop",
            "components": [{"id": "body", "type": "mesh", "primitive": "box", "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0}}]
        })

        scope = ScopeSpec(allow_delete=False)
        plan_res = self.engine.plan_intent("Elimina el cuerpo", active_asset_id="prop_del", scope=scope)
        self.assertFalse(plan_res["success"])
        self.assertIn("OPERATION_NOT_ALLOWED", plan_res["error_message"])

    def test_09_change_budget_exceeded(self):
        """Test 9: Change budget - Plan que supera max_operations."""
        self.engine.create_asset({
            "asset_id": "budget_test",
            "name": "Budget Test",
            "components": [{"id": "body", "type": "mesh", "primitive": "box", "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0}}]
        })

        strict_budget = ChangeBudget(max_operations=0)
        plan_res = self.engine.plan_intent("Hazlo de 2m", active_asset_id="budget_test", budget=strict_budget)
        self.assertFalse(plan_res["success"])
        self.assertIn("CHANGE_BUDGET_EXCEEDED", plan_res["error_message"])

    def test_10_idempotency(self):
        """Test 10: Idempotencia - Ejecutar dos veces SET blade = 0.95."""
        self.engine.create_asset({
            "asset_id": "sword_idemp",
            "name": "Sword",
            "components": [{"id": "blade", "type": "blade", "primitive": "box", "dimensions": {"width": 0.05, "depth": 0.02, "height": 0.85}}]
        })

        # 1ra vez: SET a 0.95m
        self.engine.apply_change("sword_idemp", "blade", {"dimensions": {"width": 0.05, "depth": 0.02, "height": 0.95}})
        insp1 = self.engine.inspect_component("sword_idemp", "blade")
        self.assertEqual(insp1["dimensions"]["height"], 0.95)

        # 2da vez: Re-ejecutar SET a 0.95m
        self.engine.apply_change("sword_idemp", "blade", {"dimensions": {"width": 0.05, "depth": 0.02, "height": 0.95}})
        insp2 = self.engine.inspect_component("sword_idemp", "blade")
        self.assertEqual(insp2["dimensions"]["height"], 0.95) # Permanece 0.95, no 1.05

    def test_11_unit_conversion_normalization(self):
        """Test 11: Conversión de unidades - 10cm, 1m, 2ft, 100mm."""
        d1 = UnitNormalizer.normalize_dimensions(DimensionsSpec(height=10.0, unit="cm"))
        self.assertAlmostEqual(d1.height, 0.10, places=4)

        d2 = UnitNormalizer.normalize_dimensions(DimensionsSpec(height=1.0, unit="m"))
        self.assertAlmostEqual(d2.height, 1.00, places=4)

        d3 = UnitNormalizer.normalize_dimensions(DimensionsSpec(height=2.0, unit="ft"))
        self.assertAlmostEqual(d3.height, 0.6096, places=4)

        d4 = UnitNormalizer.normalize_dimensions(DimensionsSpec(height=100.0, unit="mm"))
        self.assertAlmostEqual(d4.height, 0.10, places=4)

if __name__ == "__main__":
    unittest.main()
