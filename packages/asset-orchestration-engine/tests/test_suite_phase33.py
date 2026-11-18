import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.world_state_change_planning import (
    WorldStateAPI, AssetState, WorldAssetStatus, ChangeRequest,
    WorldChangeType, WorldChangeScope, ContextLevel
)

class TestWorldStateChangePlanningPhase33(unittest.TestCase):
    def setUp(self):
        self.api = WorldStateAPI()
        self.house1 = AssetState(
            asset_id="HOUSE_001",
            asset_type="HOUSE",
            version=1,
            status=WorldAssetStatus.VALID,
            geometry_hash="geo_hash_house_01",
            parameters={"door.width": 0.90, "roof.pitch": 40.0, "windows": 2},
            components=["FOUNDATION", "WALLS", "DOOR", "WINDOWS", "ROOF", "STAIRS"],
            locked_properties=["roof.shape"]
        )
        self.api.register_asset(self.house1)

    def test_01_minimal_change_planning_scenario_113(self):
        """Test 1: Scenario 113 - 'haz la puerta 20cm más ancha' aísla afectación a puerta y aperturas."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        plan = self.api.plan_change(req)
        self.assertIn("DOOR", plan.affected_components)
        self.assertIn("DOOR_FRAME", plan.affected_components)
        self.assertIn("WALL_OPENING", plan.affected_components)
        self.assertIn("ROOF", plan.unaffected_components)
        self.assertIn("WINDOWS", plan.unaffected_components)
        self.assertIn("STAIRS", plan.unaffected_components)
        self.assertIn("FOUNDATION", plan.unaffected_components)

    def test_02_constraint_conflict_protection_scenario_114(self):
        """Test 2: Scenario 114 - 'haz el techo plano' cuando ROOF.SHAPE=LOCKED produce CONSTRAINT_CONFLICT."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="roof.shape",
            new_value="FLAT"
        )
        with self.assertRaises(ValueError) as ctx:
            self.api.plan_change(req)
        self.assertIn("CONSTRAINT_CONFLICT", str(ctx.exception))

    def test_03_external_modification_detection_scenario_115(self):
        """Test 3: Scenario 115 - Modificación manual externa en Blender produce EXTERNAL_MODIFICATION."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        with self.assertRaises(ValueError) as ctx:
            self.api.execute_change(req, current_blender_hash="blender_tampered_hash_99")
        self.assertIn("EXTERNAL_MODIFICATION", str(ctx.exception))

    def test_04_target_ambiguity_detection_scenario_116(self):
        """Test 4: Scenario 116 - Dos casas presentes y petición 'la casa' produce AMBIGUOUS_TARGET."""
        house2 = AssetState(asset_id="HOUSE_002", asset_type="HOUSE", version=1)
        self.api.register_asset(house2)

        req = ChangeRequest(
            target_asset_id=None, # Sin ID explícito
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        with self.assertRaises(ValueError) as ctx:
            self.api.plan_change(req)
        self.assertIn("AMBIGUOUS_TARGET", str(ctx.exception))

    def test_05_idempotency_already_applied_scenario_117(self):
        """Test 5: Scenario 117 - Ejecutar el mismo ChangePlan dos veces produce ALREADY_APPLIED."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        tx1 = self.api.execute_change(req, current_blender_hash="geo_hash_house_01")
        self.assertIsNotNone(tx1)

        with self.assertRaises(ValueError) as ctx:
            self.api.execute_change(req, current_blender_hash="geo_hash_house_01")
        self.assertIn("ALREADY_APPLIED", str(ctx.exception))

    def test_06_dry_run_simulation(self):
        """Test 6: dry_run genera resumen previo sin mutar el estado del WorldState."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        res = self.api.dry_run_change(req)
        self.assertEqual(res.status, "PASS")
        self.assertGreater(len(res.what_will_change), 0)
        self.assertGreater(len(res.what_will_not_change), 0)
        self.assertEqual(self.api.state_mgr.get_asset("HOUSE_001").parameters["door.width"], 0.90)

    def test_07_atomic_transaction_commit(self):
        """Test 7: Transacción incrementa versión y actualiza parámetros atómicamente."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        tx = self.api.execute_change(req, current_blender_hash="geo_hash_house_01")
        self.assertEqual(tx.status.value, "COMMITTED")
        asset = self.api.state_mgr.get_asset("HOUSE_001")
        self.assertEqual(asset.version, 2)
        self.assertEqual(asset.parameters["door.width"], 1.10)

    def test_08_undo_and_redo_transaction(self):
        """Test 8: Undo restaura estado anterior y Redo vuelve a aplicar la mutación."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        self.api.execute_change(req, current_blender_hash="geo_hash_house_01")
        self.assertEqual(self.api.state_mgr.get_asset("HOUSE_001").version, 2)

        self.api.undo()
        self.assertEqual(self.api.state_mgr.get_asset("HOUSE_001").parameters["door.width"], 0.90)
        self.assertEqual(self.api.state_mgr.get_asset("HOUSE_001").version, 1)

        self.api.redo()
        self.assertEqual(self.api.state_mgr.get_asset("HOUSE_001").parameters["door.width"], 1.10)
        self.assertEqual(self.api.state_mgr.get_asset("HOUSE_001").version, 2)

    def test_09_ai_context_levels(self):
        """Test 9: Compresión de contexto por niveles (MINIMAL, STANDARD, DETAILED)."""
        c_min = self.api.get_asset_state("HOUSE_001", ContextLevel.MINIMAL)
        c_std = self.api.get_asset_state("HOUSE_001", ContextLevel.STANDARD)
        self.assertNotIn("parameters", c_min)
        self.assertIn("parameters", c_std)

    def test_10_target_resolution_explicit_id(self):
        """Test 10: TargetResolver resuelve correctamente con ID explícito."""
        req = ChangeRequest(
            target_asset_id="HOUSE_001",
            operation=WorldChangeType.MODIFY,
            property_path="door.width",
            new_value=1.10
        )
        plan = self.api.plan_change(req)
        self.assertEqual(plan.target_asset_id, "HOUSE_001")

if __name__ == "__main__":
    unittest.main()
