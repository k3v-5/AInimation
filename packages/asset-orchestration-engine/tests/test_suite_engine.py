import sys
import os
import unittest

# Añadir directorio raíz a sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import AssetOrchestrationEngine, ChangeBudget

class TestAssetOrchestrationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AssetOrchestrationEngine()

    def test_01_create_cube(self):
        """Test 1: Crear cubo."""
        cube_spec = {
            "asset_id": "cube_001",
            "name": "Test Cube",
            "category": "prop",
            "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0, "unit": "meters"},
            "components": [
                {
                    "id": "body",
                    "type": "mesh",
                    "primitive": "box",
                    "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0, "unit": "meters"}
                }
            ]
        }
        res = self.engine.create_asset(cube_spec)
        self.assertTrue(res["success"])
        self.assertEqual(res["asset_id"], "cube_001")
        self.assertEqual(res["validation"]["status"], "READY")

        # Inspeccionar
        insp = self.engine.inspect_component("cube_001", "body")
        self.assertTrue(insp["success"])
        self.assertEqual(insp["dimensions"]["height"], 1.0)

    def test_02_modify_cube_dimensions(self):
        """Test 2: Modificar dimensiones del cubo sin recrearlo."""
        cube_spec = {
            "asset_id": "cube_002",
            "name": "Test Cube 2",
            "components": [
                {"id": "body", "type": "mesh", "primitive": "box", "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0}}
            ]
        }
        self.engine.create_asset(cube_spec)

        # Modificar a height = 2.0
        res = self.engine.apply_change("cube_002", "body", {"dimensions": {"width": 1.0, "depth": 1.0, "height": 2.0}})
        self.assertTrue(res["success"])
        self.assertEqual(res["version"], 2)

        insp = self.engine.inspect_component("cube_002", "body")
        self.assertEqual(insp["dimensions"]["height"], 2.0)
        self.assertEqual(insp["version"], 2)

    def test_03_modify_single_component_composite_asset(self):
        """Test 3: Modificar solamente una parte de un asset compuesto."""
        sword_spec = {
            "asset_id": "sword_001",
            "name": "Medieval Sword",
            "category": "weapon",
            "components": [
                {"id": "handle", "type": "handle", "primitive": "cylinder", "dimensions": {"width": 0.04, "depth": 0.04, "height": 0.25}},
                {"id": "guard", "type": "guard", "primitive": "box", "parent_id": "handle", "dimensions": {"width": 0.15, "depth": 0.03, "height": 0.03}},
                {"id": "blade", "type": "blade", "primitive": "box", "parent_id": "guard", "dimensions": {"width": 0.06, "depth": 0.02, "height": 0.85}}
            ]
        }
        self.engine.create_asset(sword_spec)

        # Alargar solo la hoja a 0.95m (+10cm)
        res = self.engine.apply_change("sword_001", "blade", {"dimensions": {"width": 0.06, "depth": 0.02, "height": 0.95}})
        self.assertTrue(res["success"])
        self.assertEqual(res["objects_modified"], ["sword_001.blade"])

        # Verificar que handle y guard quedaron intactos (version 1)
        insp_handle = self.engine.inspect_component("sword_001", "handle")
        insp_guard = self.engine.inspect_component("sword_001", "guard")
        insp_blade = self.engine.inspect_component("sword_001", "blade")

        self.assertEqual(insp_handle["version"], 1)
        self.assertEqual(insp_guard["version"], 1)
        self.assertEqual(insp_blade["version"], 2)
        self.assertEqual(insp_blade["dimensions"]["height"], 0.95)

    def test_04_modify_nonexistent_component_fail_safely(self):
        """Test 4: Solicitar modificación de componente inexistente -> FAIL WITHOUT MODIFICATION."""
        sword_spec = {
            "asset_id": "sword_002",
            "name": "Medieval Sword",
            "components": [
                {"id": "handle", "type": "handle", "primitive": "cylinder", "dimensions": {"width": 0.04, "depth": 0.04, "height": 0.25}}
            ]
        }
        self.engine.create_asset(sword_spec)

        # Intentar modificar 'dragon_wing' que no existe
        res = self.engine.apply_change("sword_002", "dragon_wing", {"dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0}})
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "COMPONENT_NOT_FOUND")

        # Comprobar que no se auto-creó nada espurio
        insp = self.engine.inspect_asset("sword_002")
        self.assertEqual(insp["components_count"], 1)

    def test_05_transaction_error_rollback(self):
        """Test 5: Provocar error durante una transacción -> ROLLBACK."""
        box_spec = {
            "asset_id": "box_tx",
            "name": "Box TX",
            "components": [
                {"id": "part1", "type": "mesh", "primitive": "box", "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0}}
            ]
        }
        self.engine.create_asset(box_spec)

        # Iniciar transacción manual con fallo
        tx = self.engine.tx_manager.begin_transaction("tx_fail_test", self.engine.state_manager.get_graph("box_tx"))
        node = tx.active_graph.get_node("box_tx.part1")
        node.dimensions.height = 999.0 # Cambio temporal sucio

        # Ejecutar rollback
        restored_graph = self.engine.tx_manager.rollback("tx_fail_test")
        self.assertIsNotNone(restored_graph)
        self.assertEqual(restored_graph.get_node("box_tx.part1").dimensions.height, 1.0)

    def test_06_duplicate_modification_is_no_op(self):
        """Test 6: Enviar dos veces la misma modificación -> segunda ejecución = NO_OP."""
        barrel_spec = {
            "asset_id": "barrel_001",
            "name": "Barrel",
            "components": [
                {"id": "body", "type": "body", "primitive": "cylinder", "dimensions": {"width": 0.7, "depth": 0.7, "height": 1.0}}
            ]
        }
        self.engine.create_asset(barrel_spec)

        # 1ra modificación
        res1 = self.engine.apply_change("barrel_001", "body", {"dimensions": {"width": 0.7, "depth": 0.7, "height": 1.2}})
        self.assertTrue(res1["success"])

        # 2da modificación idéntica
        plan2 = self.engine.plan_change("barrel_001", "body", {"dimensions": {"width": 0.7, "depth": 0.7, "height": 1.2}})
        self.assertTrue(plan2["success"])
        self.assertTrue(plan2["is_no_op"])

    def test_07_modify_already_valid_asset_minimal_change(self):
        """Test 7: Modificar un asset ya válido -> cambiar solo lo necesario."""
        chair_spec = {
            "asset_id": "chair_001",
            "name": "Chair",
            "components": [
                {"id": "seat", "type": "seat", "primitive": "box", "dimensions": {"width": 0.5, "depth": 0.5, "height": 0.05}},
                {"id": "leg1", "type": "leg", "primitive": "cylinder", "dimensions": {"width": 0.05, "depth": 0.05, "height": 0.45}}
            ]
        }
        create_res = self.engine.create_asset(chair_spec)
        self.assertEqual(create_res["validation"]["status"], "READY")

        # Modificar solo la pata leg1
        mod_res = self.engine.apply_change("chair_001", "leg1", {"dimensions": {"width": 0.06, "depth": 0.06, "height": 0.50}})
        self.assertTrue(mod_res["success"])
        self.assertEqual(mod_res["objects_modified"], ["chair_001.leg1"])

    def test_08_change_budget_exceeded(self):
        """Test 8: Exceder change budget -> STOP."""
        prop_spec = {
            "asset_id": "prop_budget",
            "name": "Prop",
            "components": [
                {"id": "base", "type": "mesh", "primitive": "box", "dimensions": {"width": 1.0, "depth": 1.0, "height": 1.0}}
            ]
        }
        self.engine.create_asset(prop_spec)

        # Budget restrictivo de 0 operaciones
        strict_budget = ChangeBudget(max_operations=0, max_objects_affected=0)
        res = self.engine.apply_change(
            "prop_budget", "base",
            {"dimensions": {"width": 2.0, "depth": 2.0, "height": 2.0}},
            budget=strict_budget
        )
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "CHANGE_BUDGET_EXCEEDED")

if __name__ == "__main__":
    unittest.main()
