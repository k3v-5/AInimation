import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GameplayAwareAPI, ActorProfile, DoorGameplayDefinition, StairDefinition,
    SpawnPoint, InteractionPoint, InteractionType, GameplaySeverity
)

class TestGameplayAwareConstructionPhase29(unittest.TestCase):
    def setUp(self):
        self.player_profile = ActorProfile(
            height=1.80, width=0.60, clearance=0.80, step_height=0.35, max_slope=40.0
        )
        self.api = GameplayAwareAPI(self.player_profile)

    def test_01_door_width_scale_validation(self):
        """Test 1: Puerta estrecha (0.62m < 0.80m) produce fallo crítico DOOR_TOO_NARROW."""
        door_narrow = DoorGameplayDefinition(door_id="door_01", width=0.62, height=2.10)
        report = self.api.validate_asset_gameplay("house_narrow_door", door=door_narrow)
        self.assertFalse(report.is_valid)
        self.assertEqual(report.scale_status, GameplaySeverity.CRITICAL)
        self.assertTrue(any("DOOR_TOO_NARROW" in e for e in report.critical_errors))

    def test_02_stair_slope_traversal_validation(self):
        """Test 2: Escalera con pendiente 46° > 40° produce fallo crítico STAIR_TOO_STEEP."""
        stair_steep = StairDefinition(step_count=10, step_height=0.25, step_depth=0.24, slope=46.0)
        report = self.api.validate_asset_gameplay("house_steep_stair", stair=stair_steep)
        self.assertFalse(report.is_valid)
        self.assertEqual(report.traversal_status, GameplaySeverity.CRITICAL)
        self.assertTrue(any("STAIR_TOO_STEEP" in e for e in report.critical_errors))

    def test_03_interaction_point_blocked_validation(self):
        """Test 3: Punto de interacción bloqueado produce INTERACTION_BLOCKED."""
        inter_blocked = InteractionPoint(
            point_id="pt_chest",
            interaction_type=InteractionType.USE,
            position=(2.0, 1.0, 0.0),
            is_blocked=True
        )
        report = self.api.validate_asset_gameplay("chest_blocked", interaction=inter_blocked)
        self.assertFalse(report.is_valid)
        self.assertEqual(report.interaction_status, GameplaySeverity.CRITICAL)
        self.assertTrue(any("INTERACTION_BLOCKED" in e for e in report.critical_errors))

    def test_04_spawn_inside_geometry_validation(self):
        """Test 4: Spawn dentro de colisión sólida produce SPAWN_INSIDE_GEOMETRY."""
        spawn_bad = SpawnPoint(spawn_id="sp_player", position=(0.0, 0.0, 0.0), is_inside_geometry=True)
        report = self.api.validate_asset_gameplay("arena_bad_spawn", spawn=spawn_bad)
        self.assertFalse(report.is_valid)
        self.assertEqual(report.spawn_status, GameplaySeverity.CRITICAL)
        self.assertTrue(any("SPAWN_INSIDE_GEOMETRY" in e for e in report.critical_errors))

    def test_05_navigation_unreachable_goal_validation(self):
        """Test 5: Camino bloqueado a objetivo produce PATH_UNREACHABLE."""
        nav_graph = {"SPAWN": ["HALLWAY"], "HALLWAY": ["ROOM_A"], "ROOM_A": []}
        report = self.api.validate_asset_gameplay(
            "dungeon_blocked",
            nav_graph=nav_graph,
            start_node="SPAWN",
            goal_node="TREASURE_ROOM" # Inaccesible
        )
        self.assertFalse(report.is_valid)
        self.assertEqual(report.navigation_status, GameplaySeverity.CRITICAL)
        self.assertTrue(any("PATH_UNREACHABLE" in e for e in report.critical_errors))

    def test_06_combined_quality_score_calculation(self):
        """Test 6: Puntuación combinada ponderada (0.35 visual + 0.25 tech + 0.40 gameplay)."""
        score = self.api.compute_combined_quality_score(
            visual_score=0.90, technical_score=0.80, gameplay_score=1.00
        )
        # 0.90*0.35 + 0.80*0.25 + 1.00*0.40 = 0.315 + 0.20 + 0.40 = 0.915
        self.assertEqual(score, 0.915)

    def test_07_hard_gameplay_failure_rejection(self):
        """Test 7: Un fallo crítico en gameplay invalida el asset aunque el score visual sea 0.98."""
        door_narrow = DoorGameplayDefinition(door_id="door_01", width=0.50)
        report = self.api.validate_asset_gameplay("house_visual_gem_gameplay_fail", door=door_narrow)
        self.assertFalse(report.is_valid)
        self.assertGreaterEqual(len(report.critical_errors), 1)

    def test_08_automated_player_proxy_traversal(self):
        """Test 8: GameplayTestAgent ejecuta recorrido completo de extremo a extremo con éxito."""
        spawn = SpawnPoint(spawn_id="sp_01", position=(0.0, 0.0, 0.0))
        door = DoorGameplayDefinition(door_id="d_01", width=0.90, height=2.10)
        stair = StairDefinition(step_count=10, step_height=0.18, step_depth=0.28, slope=32.7)
        inter = InteractionPoint(point_id="pt_lever", interaction_type=InteractionType.ACTIVATE, position=(5.0, 2.0, 0.0))
        nav_g = {"SPAWN": ["DOOR"], "DOOR": ["STAIR"], "STAIR": ["OBJECTIVE"]}

        ok, logs, err = self.api.run_player_proxy_test(
            spawn=spawn, door=door, stair=stair, interaction=inter, nav_graph=nav_g, goal_node="OBJECTIVE"
        )
        self.assertTrue(ok)
        self.assertIsNone(err)
        self.assertEqual(len(logs), 5)
        self.assertIn("OBJECTIVE: Successfully reached", logs[-1])

    def test_09_parameter_impact_graph_analysis(self):
        """Test 9: ParameterImpactGraph identifica subsistemas afectados según el parámetro modificado."""
        door_impact = self.api.get_parameter_impact("door_width")
        self.assertIn("navigation", door_impact)
        self.assertIn("collision", door_impact)
        self.assertIn("interaction", door_impact)

        roof_impact = self.api.get_parameter_impact("roof_height")
        self.assertEqual(roof_impact, ["visual"])

    def test_10_fully_compliant_asset_gameplay_pass(self):
        """Test 10: Asset con puerta, escaleras y navegación conforme pasa al 100%."""
        door = DoorGameplayDefinition(door_id="d_valid", width=0.90, height=2.10)
        stair = StairDefinition(step_count=12, step_height=0.18, step_depth=0.28, slope=32.7)
        spawn = SpawnPoint(spawn_id="sp_valid", position=(0.0, 0.0, 0.0))
        inter = InteractionPoint(point_id="pt_door", interaction_type=InteractionType.OPEN, position=(0.0, 0.0, 0.0))
        nav_g = {"SPAWN": ["HALL"], "HALL": ["GOAL"]}

        report = self.api.validate_asset_gameplay(
            "house_perfect_gameplay",
            door=door,
            stair=stair,
            spawn=spawn,
            interaction=inter,
            nav_graph=nav_g,
            goal_node="GOAL"
        )
        self.assertTrue(report.is_valid)
        self.assertEqual(report.gameplay_score, 1.00)
        self.assertEqual(len(report.critical_errors), 0)

if __name__ == "__main__":
    unittest.main()
