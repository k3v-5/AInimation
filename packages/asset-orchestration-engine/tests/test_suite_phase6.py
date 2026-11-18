import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GeometryEngine, AppearanceEngine, GameReadyEngine, GameReadyAPI,
    GameReadyLODProfile, LODLevelConfig, CollisionProfile, CollisionType,
    PivotType, NamingValidator, ApprovalValidator, UVMethod
)

class TestGameReadyEnginePhase6(unittest.TestCase):
    def setUp(self):
        self.geo_engine = GeometryEngine()
        self.app_engine = AppearanceEngine(self.geo_engine)
        self.gr_engine = GameReadyEngine(self.geo_engine, self.app_engine)
        self.gr_api = GameReadyAPI(self.gr_engine)

        # Crear asset fuente estándar (Espada)
        self.geo_engine.create_component("sword_gr", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
        self.geo_engine.create_component("sword_gr", "guard", "primitive", {"primitive": "box", "width": 0.15, "depth": 0.03, "height": 0.03}, parent_id="sword_gr.handle")
        self.geo_engine.create_component("sword_gr", "blade", "profile", {"length": 0.95, "width": 0.05, "thickness": 0.015}, parent_id="sword_gr.guard")
        self.geo_engine.create_component("sword_gr", "pommel", "primitive", {"primitive": "sphere", "width": 0.05, "depth": 0.05, "height": 0.05}, parent_id="sword_gr.handle")

        self.app_engine.create_material("metal_dark", "Dark Metal", "PBR", {"metallic": 0.9, "roughness": 0.25})
        self.app_engine.assign_material("sword_gr.blade", "metal_dark")
        self.app_engine.assign_material("sword_gr.guard", "metal_dark")

    def test_01_approved_source_processes_to_game_ready(self):
        """Test 1: Approved source - Asset con aprobaciones procesa a GAME_READY."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr", category="Weapons", geometry_status="APPROVED", appearance_status="APPROVED")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "GAME_READY")
        self.assertEqual(res["unreal_asset_name"], "SM_SwordGr")

    def test_02_unapproved_geometry_blocked(self):
        """Test 2: Unapproved geometry - Bloquea con GEOMETRY_NOT_APPROVED."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr", geometry_status="PENDING", appearance_status="APPROVED")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "GEOMETRY_NOT_APPROVED")

    def test_03_polygon_budget_exceeded(self):
        """Test 3: Polygon budget - Superar presupuesto de triángulos produce POLYGON_BUDGET_EXCEEDED."""
        strict_profile = GameReadyLODProfile(levels={
            0: LODLevelConfig(level=0, screen_size=1.0, reduction_ratio=1.0, max_triangles=10, max_visual_deviation=0.0)
        })
        res = self.gr_engine.process_game_ready("sword_gr", lod_profile=strict_profile)
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "POLYGON_BUDGET_EXCEEDED")

    def test_04_lod_generation_chain(self):
        """Test 4: LOD chain - Genera cadena LOD0..LOD3 con reducción progresiva."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr")
        self.assertTrue(res["success"])
        triangles = res["triangles"]
        self.assertIn("LOD0", triangles)
        self.assertIn("LOD1", triangles)
        self.assertIn("LOD2", triangles)
        self.assertIn("LOD3", triangles)
        self.assertGreaterEqual(triangles["LOD0"], triangles["LOD1"])
        self.assertGreaterEqual(triangles["LOD1"], triangles["LOD2"])

    def test_05_lod_visual_deviation_rejection(self):
        """Test 5: LOD visual deviation - Rechazo si excede max_visual_deviation."""
        invalid_dev_profile = GameReadyLODProfile(levels={
            0: LODLevelConfig(level=0, screen_size=1.0, reduction_ratio=1.0, max_triangles=10000, max_visual_deviation=0.00),
            1: LODLevelConfig(level=1, screen_size=0.5, reduction_ratio=0.1, max_triangles=5000, max_visual_deviation=0.0001)
        })
        res = self.gr_engine.process_game_ready("sword_gr", lod_profile=invalid_dev_profile)
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "VISUAL_DEVIATION_EXCEEDED")

    def test_06_collision_generation_ucx(self):
        """Test 6: Collision generation - Genera envolvente simplificada UCX_."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr")
        self.assertTrue(res["success"])
        manifest = res["manifest"]
        self.assertGreater(len(manifest.collision_hulls), 0)
        self.assertTrue(manifest.collision_hulls[0].startswith("UCX_SM_SwordGr"))

    def test_07_pivot_adjustment(self):
        """Test 7: Pivot - Ajuste de pivote a BOTTOM_CENTER y ORIGIN."""
        res_bc = self.gr_engine.process_game_ready("sword_gr", pivot_type=PivotType.BOTTOM_CENTER)
        self.assertTrue(res_bc["success"])
        res_orig = self.gr_engine.process_game_ready("sword_gr", pivot_type=PivotType.ORIGIN)
        self.assertTrue(res_orig["success"])

    def test_08_naming_validation(self):
        """Test 8: Naming - Validación de prefijos y no-colisiones."""
        ok_sm, _ = NamingValidator.validate_name("SM_Sword_001", "SM_")
        self.assertTrue(ok_sm)
        ok_bad, err = NamingValidator.validate_name("Cube.001", "SM_")
        self.assertFalse(ok_bad)
        self.assertIn("NAMING_INVALID", err)

    def test_09_material_preservation(self):
        """Test 9: Material preservation - La optimización preserva los slots de material."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr")
        self.assertTrue(res["success"])
        manifest = res["manifest"]
        self.assertIn("metal_dark", manifest.material_slots)

    def test_10_uv_preservation(self):
        """Test 10: UV preservation - Coordenadas UV permanecen válidas."""
        self.app_engine.generate_uv("sword_gr.blade", method=UVMethod.PLANAR)
        res = self.gr_api.prepare_asset_for_unreal("sword_gr")
        self.assertTrue(res["success"])

    def test_11_source_immutability(self):
        """Test 11: Source immutability - La versión original no es alterada."""
        insp_before = self.geo_engine.inspect_component("sword_gr.blade")
        self.gr_api.prepare_asset_for_unreal("sword_gr")
        insp_after = self.geo_engine.inspect_component("sword_gr.blade")

        self.assertEqual(insp_before["vertices_count"], insp_after["vertices_count"])
        self.assertEqual(insp_before["dimensions"], insp_after["dimensions"])

    def test_12_rollback_on_failure(self):
        """Test 12: Rollback - Ante fallo en colisión o presupuesto, el estado previo se preserva."""
        invalid_col_profile = CollisionProfile(max_convex_hulls=0)
        res = self.gr_engine.process_game_ready("sword_gr", collision_profile=invalid_col_profile)
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "COLLISION_BUDGET_EXCEEDED")

    def test_13_fbx_export_manifest(self):
        """Test 13: Export - El manifiesto de exportación FBX es válido."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr")
        self.assertTrue(res["success"])
        manifest = res["manifest"]
        self.assertEqual(manifest.unreal_mapping.fbx_filename, "SM_SwordGr.fbx")

    def test_14_unreal_import_mapping(self):
        """Test 14: Unreal import - Ruta /Game/Assets/... y settings de importación."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr", category="Weapons")
        self.assertTrue(res["success"])
        self.assertEqual(res["unreal_package_path"], "/Game/Assets/Weapons/SM_SwordGr/SM_SwordGr")

    def test_15_unauthorized_change_detected(self):
        """Test 15: Unauthorized change - Asset sin aprobar produce fallo inmediato."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr", appearance_status="REJECTED")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "APPEARANCE_NOT_APPROVED")

    def test_16_dry_run_mode(self):
        """Test 16: Dry run - dry_run=True reporta estimaciones sin registrar manifest final."""
        res = self.gr_api.prepare_asset_for_unreal("sword_gr", dry_run=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "dry_run")
        self.assertIn("expected_manifest", res)

    def test_17_determinism(self):
        """Test 17: Determinismo - Misma entrada produce idénticos LODs y dimensiones en cm."""
        res1 = self.gr_engine.process_game_ready("sword_gr")
        res2 = self.gr_engine.process_game_ready("sword_gr")
        self.assertEqual(res1["triangles"], res2["triangles"])
        self.assertEqual(res1["dimensions_cm"], res2["dimensions_cm"])

    def test_18_scope_enforcement(self):
        """Test 18: Scope - Bloquea operaciones fuera del scope permitido."""
        res = self.gr_engine.process_game_ready("sword_gr", scope=["other_asset"])
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "GAME_READY_SCOPE_VIOLATION")

if __name__ == "__main__":
    unittest.main()
