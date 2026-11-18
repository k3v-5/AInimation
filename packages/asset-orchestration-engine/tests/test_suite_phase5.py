import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GeometryEngine, AppearanceEngine, AppearanceAPI, TextureMetadata,
    TextureUsage, ColorSpace, UVMethod, UVSet
)

class TestAppearanceEnginePhase5(unittest.TestCase):
    def setUp(self):
        self.geo_engine = GeometryEngine()
        self.app_engine = AppearanceEngine(self.geo_engine)
        self.app_api = AppearanceAPI(self.app_engine)

    def test_01_shared_material_instance_isolation(self):
        """Test 1: Shared Material - Dos componentes usan metal_dark. Modificar solo blade no altera guard."""
        self.app_engine.create_material("metal_dark", "Dark Metal", "PBR", {"metallic": 0.90, "roughness": 0.20})
        self.app_engine.assign_material("blade", "metal_dark")
        self.app_engine.assign_material("guard", "metal_dark")

        # Modificar solo la instancia de blade
        res = self.app_engine.modify_material("blade", {"roughness": 0.35})
        self.assertTrue(res["success"])

        # Verificar instancias
        inst_blade = self.app_engine.materials.get_instance_for_component("blade")
        inst_guard = self.app_engine.materials.get_instance_for_component("guard")
        base_mat = self.app_engine.materials.get_material("metal_dark")

        self.assertEqual(inst_blade.parameter_overrides["roughness"], 0.35)
        self.assertEqual(inst_guard.parameter_overrides.get("roughness"), None)
        self.assertEqual(base_mat.parameters.roughness, 0.20) # Base permanece intacto

    def test_02_geometry_isolation(self):
        """Test 2: Geometry Isolation - Modificar apariencia produce geometry_changes = 0."""
        # Crear geometría
        self.geo_engine.create_component("sword_app", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})
        insp_before = self.geo_engine.inspect_component("sword_app.blade")

        self.app_engine.create_material("blade_mat", "Blade Mat", "PBR", {"roughness": 0.20})
        self.app_engine.assign_material("sword_app.blade", "blade_mat")

        # Modificar roughness
        res = self.app_engine.modify_material("sword_app.blade", {"roughness": 0.40})
        self.assertTrue(res["success"])
        self.assertEqual(res["geometry_changes"], [])

        # Comprobar que vértices y caras no cambiaron
        insp_after = self.geo_engine.inspect_component("sword_app.blade")
        self.assertEqual(insp_before["vertices_count"], insp_after["vertices_count"])
        self.assertEqual(insp_before["dimensions"], insp_after["dimensions"])

    def test_03_texture_color_space_validation(self):
        """Test 3: Texture Color Space - Asignar ROUGHNESS como sRGB produce INVALID_COLOR_SPACE."""
        res = self.app_api.register_texture("tex_rough", "/path/rough.png", "ROUGHNESS", "sRGB")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "INVALID_COLOR_SPACE")

        # Non-Color debe ser válido
        res_ok = self.app_api.register_texture("tex_rough_ok", "/path/rough.png", "ROUGHNESS", "Non-Color")
        self.assertTrue(res_ok["success"])

    def test_04_missing_material_validation(self):
        """Test 4: Missing Material - Solicitar material inexistente produce MATERIAL_NOT_FOUND."""
        res = self.app_engine.assign_material("blade", "non_existent_material")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "MATERIAL_NOT_FOUND")

    def test_05_uv_validation_and_failure_isolation(self):
        """Test 5: UV Validation - Coordenadas NaN devuelven UV_VALIDATION_FAILED."""
        invalid_uv = UVSet("uv_inv", "comp_1", "UV0", UVMethod.BOX, [(float('nan'), 0.5)])
        self.app_engine.uv_sets["comp_1"] = invalid_uv

        val_res = self.app_engine.validate_appearance()
        self.assertFalse(val_res["is_valid"])
        self.assertIn("UV_VALIDATION_FAILED", val_res["errors"][0])

    def test_06_material_rollback_and_failure_isolation(self):
        """Test 6: Material Rollback - Parámetro PBR fuera de rango devuelve INVALID_MATERIAL_PARAMETER."""
        self.app_engine.create_material("mat_test", "Test Mat", "PBR", {"roughness": 0.5})

        res = self.app_engine.modify_material("mat_test", {"roughness": 2.5}) # Inválido > 1.0
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "INVALID_MATERIAL_PARAMETER")

        # Comprobar que roughness sigue en 0.5
        mat = self.app_engine.materials.get_material("mat_test")
        self.assertEqual(mat.parameters.roughness, 0.5)

    def test_07_determinism_manifest(self):
        """Test 7: Determinismo - Misma especificación produce mismo manifest."""
        self.app_engine.create_material("mat_det", "Det Mat", "PBR", {"metallic": 0.8, "roughness": 0.3})
        m1 = self.app_engine.get_appearance_manifest("asset_det")
        m2 = self.app_engine.get_appearance_manifest("asset_det")
        self.assertEqual(m1, m2)

    def test_08_scope_enforcement(self):
        """Test 8: Scope Enforcement - Intentar modificar material fuera de scope produce SCOPE_VIOLATION."""
        self.app_engine.create_material("mat_scoped", "Scoped Mat", "PBR", {"roughness": 0.5})
        res = self.app_engine.modify_material("mat_scoped", {"roughness": 0.2}, scope=["other_mat"])
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "SCOPE_VIOLATION")

    def test_09_instance_isolation_base_preserved(self):
        """Test 9: Instance Isolation - Modificar una instancia local no altera el material base."""
        self.app_engine.create_material("leather_base", "Leather", "PBR", {"roughness": 0.7})
        self.app_engine.assign_material("handle", "leather_base")

        self.app_engine.modify_material("handle", {"roughness": 0.85})
        base = self.app_engine.materials.get_material("leather_base")
        self.assertEqual(base.parameters.roughness, 0.7)

    def test_10_no_op_detection(self):
        """Test 10: NO_OP - Solicitar roughness = 0.25 cuando ya es 0.25 produce NO_OP."""
        self.app_engine.create_material("mat_noop", "Noop Mat", "PBR", {"roughness": 0.25})
        res = self.app_engine.modify_material("mat_noop", {"roughness": 0.25})
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "NO_OP")

    def test_11_appearance_diff_material_changes_only(self):
        """Test 11: Appearance Diff - Modificar roughness produce material_changes y geometry_changes vacíos."""
        self.app_engine.create_material("mat_diff", "Diff Mat", "PBR", {"roughness": 0.60})
        res = self.app_engine.modify_material("mat_diff", {"roughness": 0.30})
        self.assertTrue(res["success"])
        diff = res["diff"]
        self.assertEqual(len(diff["material_changes"]), 1)
        self.assertEqual(diff["material_changes"][0]["before"], 0.60)
        self.assertEqual(diff["material_changes"][0]["after"], 0.30)
        self.assertEqual(diff["geometry_changes"], [])

if __name__ == "__main__":
    unittest.main()
