import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetLibraryAPI, BuildIntent, MockBlenderProvider, ParameterHierarchySolver,
    LibraryConstraintEngine, SocketSystem
)

class TestAssetLibraryPhase18(unittest.TestCase):
    def setUp(self):
        self.library_api = AssetLibraryAPI()
        self.provider = MockBlenderProvider()

    def test_01_library_search(self):
        """Test 1: Search - Búsqueda de 'medieval sword' devuelve template y variante."""
        res = self.library_api.search_library("medieval sword")
        self.assertIn("weapon.sword.standard", res["templates"])
        self.assertIn("Medieval", res["variants"])

    def test_02_sockets_composition_validation(self):
        """Test 2: Sockets - Rechaza ensamblaje al que le falta el rol blade."""
        comp_map = {
            "guard": self.library_api.comp_registry.get_component("guard_cross"),
            "handle": self.library_api.comp_registry.get_component("handle_leather")
        }
        ok, msg = SocketSystem.validate_composition(comp_map)
        self.assertFalse(ok)
        self.assertIn("SOCKET_COMPOSITION_ERROR", msg)

    def test_03_parameter_hierarchy_priority(self):
        """Test 3: Hierarchy - USER > EXPLICIT_AI > VARIANT > PRESET > TEMPLATE_DEFAULT."""
        tpl_def = {"blade_length": 0.80}
        preset = {"blade_length": 0.85}
        variant = {"blade_length": 0.90}
        ai_param = {"blade_length": 0.95}
        user_ovr = {"blade_length": 1.10}

        _, res, _ = ParameterHierarchySolver.solve_parameters(
            template_defaults=tpl_def,
            preset_overrides=preset,
            variant_overrides=variant,
            ai_parameters=ai_param,
            user_overrides=user_ovr
        )
        self.assertEqual(res["blade_length"], 1.10)

    def test_04_derived_parameter_calculation(self):
        """Test 4: Derived Parameter - Calcula guard_offset = blade_width * 0.15 automáticamente."""
        _, res, _ = ParameterHierarchySolver.solve_parameters(
            template_defaults={"blade_width": 0.10}
        )
        self.assertEqual(res["guard_offset"], 0.015)

    def test_05_constraint_bounds_validation(self):
        """Test 5: Bounds - blade_width=0.50m es rechazado con PARAMETER_OUT_OF_RANGE."""
        ok, msg = LibraryConstraintEngine.validate_constraints({"blade_width": 0.50})
        self.assertFalse(ok)
        self.assertIn("PARAMETER_OUT_OF_RANGE", msg)

    def test_06_build_intent_resolution_scenario_140(self):
        """Test 6: Scenario 140 - BuildIntent(Sword, Medieval, 0.90m) resuelve ResolvedBuildSpec."""
        intent = BuildIntent(
            template_id="weapon.sword.standard",
            variant_id="Medieval",
            parameters={"blade_length": 0.90}
        )
        ok, spec, msg = self.library_api.resolve_intent(intent)
        self.assertTrue(ok)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.resolved_parameters["blade_length"], 0.90)
        self.assertIn("blade", spec.components)
        self.assertIn("guard", spec.components)

    def test_07_adaptation_scenario_141(self):
        """Test 7: Scenario 141 - 'Más pesada' adapta parámetros sin reconstruir todo desde cero."""
        intent = BuildIntent(
            template_id="weapon.sword.standard",
            preset_id="HeavySword"
        )
        ok, spec, _ = self.library_api.resolve_intent(intent)
        self.assertTrue(ok)
        self.assertEqual(spec.resolved_parameters["blade_width"], 0.08)
        self.assertEqual(spec.resolved_parameters["blade_thickness"], 0.03)

    def test_08_swapping_component_scenario_142(self):
        """Test 8: Scenario 142 - Cambiar empuñadura a handle_wood preservando el resto de componentes."""
        intent = BuildIntent(
            template_id="weapon.sword.standard",
            variant_id="Medieval",
            component_overrides={"handle": "handle_wood"}
        )
        ok, spec, _ = self.library_api.resolve_intent(intent)
        self.assertTrue(ok)
        self.assertEqual(spec.components["handle"].component_id, "handle_wood")
        self.assertEqual(spec.components["blade"].component_id, "blade_standard")

    def test_09_manifest_hash_and_cache_hit(self):
        """Test 9: Cache - Construcción idéntica dispara Cache Hit."""
        intent = BuildIntent(template_id="weapon.sword.standard", variant_id="Medieval")
        ok, spec, _ = self.library_api.resolve_intent(intent)
        
        # Build 1
        ok_b1, is_cache1, _ = self.library_api.build_from_resolved_spec("sword_b1", spec, self.provider)
        self.assertTrue(ok_b1)
        self.assertFalse(is_cache1)

        # Build 2 con mismo manifest hash
        ok_b2, is_cache2, msg2 = self.library_api.build_from_resolved_spec("sword_b2", spec, self.provider)
        self.assertTrue(ok_b2)
        self.assertTrue(is_cache2)
        self.assertIn("Cache Hit", msg2)

    def test_10_unknown_parameter_and_component_rejection(self):
        """Test 10: Unknowns - Rechaza dragon_energy y DragonBlade."""
        int_param = BuildIntent(template_id="weapon.sword.standard", parameters={"dragon_energy": 9000})
        ok_p, _, msg_p = self.library_api.resolve_intent(int_param)
        self.assertFalse(ok_p)
        self.assertIn("UNKNOWN_PARAMETER", msg_p)

        int_comp = BuildIntent(template_id="weapon.sword.standard", component_overrides={"blade": "DragonBlade"})
        ok_c, _, msg_c = self.library_api.resolve_intent(int_comp)
        self.assertFalse(ok_c)
        self.assertIn("UNKNOWN_COMPONENT", msg_c)

    def test_11_end_to_end_library_build(self):
        """Test 11: Full Build - Construye asset en MockBlenderProvider con dimensiones exactas."""
        intent = BuildIntent(template_id="weapon.sword.standard", variant_id="Medieval", parameters={"blade_length": 0.95})
        ok, spec, _ = self.library_api.resolve_intent(intent)
        ok_b, _, _ = self.library_api.build_from_resolved_spec("sword_lib_01", spec, self.provider)
        self.assertTrue(ok_b)

        comps = self.provider.assets["sword_lib_01"]["components"]
        self.assertEqual(comps["blade"]["dimensions"][2], 0.95)
        self.assertEqual(comps["guard"]["dimensions"][0], 0.18)

if __name__ == "__main__":
    unittest.main()
