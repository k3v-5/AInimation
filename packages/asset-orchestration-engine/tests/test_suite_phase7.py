import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.unreal import (
    UnrealEngine, UnrealAPI, SpatialRelation, UnrealActor
)

class TestUnrealSceneEnginePhase7(unittest.TestCase):
    def setUp(self):
        self.ue_engine = UnrealEngine("Test_Level_01")
        self.ue_api = UnrealAPI(self.ue_engine)

        # Registrar assets estándar
        self.ue_api.register_asset("sword_001", "/Game/Assets/Weapons/SM_Sword01/SM_Sword01")
        self.ue_api.register_asset("table_001", "/Game/Assets/Props/SM_Table01/SM_Table01")
        self.ue_api.register_asset("player_001", "/Game/Characters/Player/BP_PlayerCharacter", "Blueprint")

        # Spawnear actores iniciales
        self.table = self.ue_api.spawn_actor(
            asset_id="table_001",
            name="Table_Actor",
            location=(0.0, 0.0, 0.0),
            dimensions_cm=(120.0, 80.0, 90.0),
            actor_id="actor_table_01"
        )
        self.sword = self.ue_api.spawn_actor(
            asset_id="sword_001",
            name="Sword_Actor",
            location=(0.0, 0.0, 0.0),
            tags=["Weapon", "Interactable"],
            dimensions_cm=(15.0, 5.0, 95.0),
            actor_id="actor_sword_01"
        )

    def test_01_minimal_diff_no_world_rebuild(self):
        """Test 1: Minimal Diff - Mover la espada 20cm modifica 1 propiedad y 1 actor sin recrear la escena."""
        res = self.ue_api.move_actor("actor_sword_01", delta=(20.0, 0.0, 0.0))
        self.assertTrue(res["success"])
        diff = res["diff"]
        self.assertEqual(diff["total_actors_affected"], 1)
        self.assertEqual(len(diff["property_changes"]), 1)
        self.assertEqual(diff["property_changes"][0]["after"], (20.0, 0.0, 0.0))

    def test_02_stable_actor_ids(self):
        """Test 2: Stable Actor IDs - Cambiar el nombre visible conserva el actor_id inmutable."""
        actor = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        actor.name = "Renamed_Sword"
        found = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Renamed_Sword")

    def test_03_actor_registry_queries(self):
        """Test 3: Actor Registry Queries - Búsqueda por ID, Tag, Clase y Asset."""
        self.assertIsNotNone(self.ue_engine.scene.registry.find_by_id("actor_sword_01"))
        by_tag = self.ue_engine.scene.registry.find_by_tag("Weapon")
        self.assertEqual(len(by_tag), 1)
        by_asset = self.ue_engine.scene.registry.find_by_asset("sword_001")
        self.assertEqual(len(by_asset), 1)

    def test_04_asset_resolution(self):
        """Test 4: Asset Resolution - Resuelve logical_id a la ruta de Unreal."""
        path = self.ue_engine.assets.resolve_path("sword_001")
        self.assertEqual(path, "/Game/Assets/Weapons/SM_Sword01/SM_Sword01")

    def test_05_ambiguous_target_detection(self):
        """Test 5: Ambiguous target - Nombres duplicados sin ID explícito devuelven AMBIGUOUS_TARGET."""
        self.ue_api.spawn_actor("sword_001", "Sword_Actor", actor_id="actor_sword_02")
        res = self.ue_api.move_actor("Sword_Actor", delta=(10, 0, 0))
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "AMBIGUOUS_TARGET")

    def test_06_attachment_to_socket(self):
        """Test 6: Attachment to socket - Adjuntar espada a la mano del jugador."""
        player = self.ue_api.spawn_actor("player_001", "Player_Actor", actor_id="actor_player_01")
        res = self.ue_api.attach_actor("actor_sword_01", "actor_player_01", socket_name="RightHandSocket")
        self.assertTrue(res["success"])
        self.assertEqual(res["attached_socket"], "RightHandSocket")
        sword = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        self.assertEqual(sword.parent_id, "actor_player_01")

    def test_07_spatial_solver_on_top_of(self):
        """Test 7: Spatial solver - ON_TOP_OF coloca la espada sobre la mesa considerando su altura (90cm)."""
        res = self.ue_api.apply_spatial_relation("actor_sword_01", "ON_TOP_OF", "actor_table_01")
        self.assertTrue(res["success"])
        sword = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        self.assertEqual(sword.transform.location[2], 90.0) # Mesa altura = 90cm

    def test_08_material_instance_isolation(self):
        """Test 8: Material instance isolation - Override en la espada no muta otros actores."""
        res = self.ue_api.override_material("actor_sword_01", 0, "/Game/Materials/MI_GoldBlade")
        self.assertTrue(res["success"])
        sword = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        table = self.ue_engine.scene.registry.find_by_id("actor_table_01")
        self.assertEqual(sword.material_overrides[0], "/Game/Materials/MI_GoldBlade")
        self.assertEqual(table.material_overrides.get(0), None)

    def test_09_property_exposure_check(self):
        """Test 9: Property exposure - Modificar propiedad oculta devuelve PROPERTY_NOT_EDITABLE."""
        res = self.ue_api.set_property("actor_sword_01", "internal_guid", "123", is_exposed=False)
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "PROPERTY_NOT_EDITABLE")

    def test_10_dependency_conflict_on_delete(self):
        """Test 10: Dependency conflict - Eliminar padre con hijos produce DEPENDENCY_CONFLICT."""
        self.ue_api.attach_actor("actor_sword_01", "actor_table_01")
        res = self.ue_api.delete_actor("actor_table_01")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "DEPENDENCY_CONFLICT")

    def test_11_safe_delete_after_detach(self):
        """Test 11: Safe delete - Desacoplar hijo y eliminar mesa procede limpiamente."""
        self.ue_api.attach_actor("actor_sword_01", "actor_table_01")
        sword = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        sword.parent_id = None # Detach
        res = self.ue_api.delete_actor("actor_table_01")
        self.assertTrue(res["success"])
        self.assertIsNone(self.ue_engine.scene.registry.find_by_id("actor_table_01"))

    def test_12_rollback_snapshot(self):
        """Test 12: Rollback - Snapshot restaura el estado exacto anterior."""
        snap = self.ue_engine.scene.create_snapshot()
        self.ue_api.move_actor("actor_sword_01", new_location=(500, 500, 500))
        self.assertEqual(self.sword.transform.location, (500, 500, 500))
        self.ue_engine.scene.restore_snapshot(snap)
        restored = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        self.assertEqual(restored.transform.location, (0.0, 0.0, 0.0))

    def test_13_dry_run_mode(self):
        """Test 13: Dry run - dry_run=True calcula el diff sin mutar la posición real."""
        res = self.ue_api.move_actor("actor_sword_01", delta=(100, 0, 0), dry_run=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "dry_run")
        sword = self.ue_engine.scene.registry.find_by_id("actor_sword_01")
        self.assertEqual(sword.transform.location, (0.0, 0.0, 0.0))

    def test_14_no_op_detection(self):
        """Test 14: NO_OP - Mover a la misma posición produce NO_OP sin cambios."""
        res = self.ue_api.move_actor("actor_sword_01", new_location=(0.0, 0.0, 0.0))
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "NO_OP")

    def test_15_scope_enforcement(self):
        """Test 15: Scope - Bloquea operaciones fuera del scope permitido."""
        res = self.ue_api.move_actor("actor_sword_01", delta=(10, 0, 0), scope=["other_actor"])
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "UNREAL_SCOPE_VIOLATION")

    def test_16_scene_validation(self):
        """Test 16: Scene validation - Escena sin referencias rotas obtiene PASS."""
        val = self.ue_api.validate_scene()
        self.assertEqual(val["status"], "PASS")
        self.assertEqual(val["invalid_references"], 0)
        self.assertEqual(val["missing_assets"], 0)

if __name__ == "__main__":
    unittest.main()
