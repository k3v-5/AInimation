import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parametric_asset_engine import (
    ParametricAssetAPI, ParameterResolver, GeneratorRegistry
)

class TestParametricAssetEnginePhase40(unittest.TestCase):
    def setUp(self):
        self.api = ParametricAssetAPI()
        self.house = self.api.create_asset("HOUSE_001", {
            "width": 8.0,
            "depth": 6.0,
            "wall_height": 3.0,
            "roof_height": 1.8,
            "window_count": 4,
            "door_count": 1,
            "wall_material": "STONE",
            "roof_material": "WOOD"
        }, seed=42)

    def test_01_acceptance_1_roof_height_partial_regeneration(self):
        """Acceptance Test 1: Cambiar roof_height regenera únicamente el tejado, dejando muros y cimientos intactos."""
        initial_wall_mesh = self.house.components["walls"].object_ids[0]
        initial_found_mesh = self.house.components["foundation"].object_ids[0]

        updated = self.api.update_asset("HOUSE_001", {"roof_height": 1.4})
        self.assertEqual(updated.parameters["roof_height"], 1.4)
        self.assertEqual(updated.components["roof"].parameters["height"], 1.4)
        # Muros y cimientos no se regeneraron
        self.assertEqual(updated.components["walls"].object_ids[0], initial_wall_mesh)
        self.assertEqual(updated.components["foundation"].object_ids[0], initial_found_mesh)

    def test_02_acceptance_2_window_count_updates_walls_and_openings_only(self):
        """Acceptance Test 2: Cambiar window_count (4 -> 6) regenera ventanas y muros pero cimientos intactos."""
        initial_found_mesh = self.house.components["foundation"].object_ids[0]
        updated = self.api.update_asset("HOUSE_001", {"window_count": 6})
        self.assertEqual(len(updated.components["windows"].object_ids), 6)
        self.assertEqual(updated.components["foundation"].object_ids[0], initial_found_mesh)

    def test_03_acceptance_3_material_change_without_geometry_regeneration(self):
        """Acceptance Test 3: Cambiar wall_material actualiza el material sin regenerar geometría."""
        initial_wall_mesh = self.house.components["walls"].object_ids[0]
        updated = self.api.update_asset("HOUSE_001", {"wall_material": "BRICK"})
        self.assertEqual(updated.components["walls"].materials["wall_mat"], "BRICK")
        self.assertEqual(updated.components["walls"].object_ids[0], initial_wall_mesh)

    def test_04_acceptance_4_width_change_recalculates_dependent_geometry(self):
        """Acceptance Test 4: Cambiar width (8m -> 10m) recalcula la geometría dependiente."""
        updated = self.api.update_asset("HOUSE_001", {"width": 10.0})
        self.assertEqual(updated.components["walls"].parameters["width"], 10.0)
        self.assertEqual(updated.components["roof"].parameters["width"], 10.0)

    def test_05_acceptance_5_deterministic_reproducibility(self):
        """Acceptance Test 5: Misma configuración y seed produce exactamente el mismo resultado."""
        h1 = self.api.create_asset("H_TEST_A", {"width": 8.0, "roof_height": 1.8}, seed=100)
        h2 = self.api.create_asset("H_TEST_B", {"width": 8.0, "roof_height": 1.8}, seed=100)
        self.assertEqual(h1.parameters, h2.parameters)

    def test_06_acceptance_6_parameter_bounds_enforcement(self):
        """Acceptance Test 6: Parámetro fuera de límites mínimos (width < 1.0m) lanza PARAMETER_ERROR."""
        with self.assertRaises(ValueError) as ctx:
            self.api.create_asset("H_INVALID", {"width": 0.5})
        self.assertIn("PARAMETER_ERROR", str(ctx.exception))

    def test_07_acceptance_7_vague_request_rejection(self):
        """Acceptance Test 7: Petición vaga 'make it better' es rechazada exigiendo parámetros."""
        with self.assertRaises(ValueError) as ctx:
            self.api.interpret_request("HOUSE_001", "make it better")
        self.assertIn("VAGUE_REQUEST", str(ctx.exception))

    def test_08_acceptance_8_relative_reduction_interpretation(self):
        """Acceptance Test 8: 'make roof 20% shorter' multiplica roof_height *= 0.8."""
        res = self.api.interpret_request("HOUSE_001", "make roof 20% shorter")
        self.assertEqual(res["roof_height"], 1.44) # 1.8 * 0.8 = 1.44

    def test_09_acceptance_9_ambiguous_request_clarification(self):
        """Acceptance Test 9: 'make house taller' genera AMBIGUOUS_REQUEST para clarificar."""
        with self.assertRaises(ValueError) as ctx:
            self.api.interpret_request("HOUSE_001", "make house taller")
        self.assertIn("AMBIGUOUS_REQUEST", str(ctx.exception))

    def test_10_acceptance_10_unsupported_component_rejection(self):
        """Acceptance Test 10: Componente no soportado lanza UNSUPPORTED_COMPONENT."""
        with self.assertRaises(ValueError) as ctx:
            GeneratorRegistry.get_generator("gothic_flying_buttress")
        self.assertIn("UNSUPPORTED_COMPONENT", str(ctx.exception))

    def test_11_acceptance_11_constraint_insufficient_wall_margin(self):
        """Acceptance Test 11: Constraint solver detecta margen de pared insuficiente."""
        with self.assertRaises(ValueError) as ctx:
            self.api.create_asset("H_MARGIN", {
                "wall_height": 2.0,
                "window_height": 1.5,
                "window_sill_height": 0.8
            })
        self.assertIn("CONSTRAINT_ERROR", str(ctx.exception))

    def test_12_acceptance_12_transaction_undo(self):
        """Acceptance Test 12: Undo restaura la versión anterior exacta."""
        self.api.update_asset("HOUSE_001", {"roof_height": 2.5})
        self.assertEqual(self.house.parameters["roof_height"], 2.5)
        restored = self.api.undo_asset("HOUSE_001")
        self.assertEqual(restored.parameters["roof_height"], 1.8)

    def test_13_acceptance_13_parameter_cycle_detection(self):
        """Acceptance Test 13: Detección de ciclos de dependencia en grafo de parámetros."""
        graph = {"width": ["roof"], "roof": ["width"]}
        with self.assertRaises(ValueError) as ctx:
            ParameterResolver.check_cycles(graph)
        self.assertIn("PARAMETER_CYCLE_DETECTED", str(ctx.exception))

    def test_14_acceptance_14_external_modification_reconciliation(self):
        """Acceptance Test 14: Reconciliación detecta EXTERNAL_MODIFICATION cuando la escena difiere."""
        with self.assertRaises(RuntimeError) as ctx:
            self.api.reconcile_scene("HOUSE_001", {"HOUSE_001_WALLS_mesh", "ANONYMOUS_EXTRA_OBJECT"})
        self.assertIn("EXTERNAL_MODIFICATION", str(ctx.exception))

    def test_15_acceptance_15_derived_parameter_resolution(self):
        """Acceptance Test 15: Resolución de parámetro derivado roof_ratio a roof_height."""
        res = ParameterResolver.resolve_parameters({"width": 10.0, "roof_ratio": 0.25})
        self.assertEqual(res.values["roof_height"], 2.5)

    def test_16_acceptance_16_canonical_components_created(self):
        """Acceptance Test 16: La generación inicial crea los 5 componentes canónicos."""
        comps = self.house.components
        self.assertIn("foundation", comps)
        self.assertIn("walls", comps)
        self.assertIn("roof", comps)
        self.assertIn("windows", comps)
        self.assertIn("doors", comps)

if __name__ == "__main__":
    unittest.main()
