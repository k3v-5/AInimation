import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GameplayEngine, GameplayAPI, CapabilityType, StateMachine, GameplayEvent
)

class TestGameplayEnginePhase8(unittest.TestCase):
    def setUp(self):
        self.gp_engine = GameplayEngine()
        self.gp_api = GameplayAPI(self.gp_engine)

    def test_01_minimal_gameplay_diff_data_only(self):
        """Test 1: Minimal Gameplay Diff - Cambiar damage 25->40 modifica solo data, dejando el resto intacto."""
        res = self.gp_api.set_data("sword_01", "damage", 40.0)
        self.assertTrue(res["success"])
        diff = res["diff"]
        self.assertEqual(len(diff["modified_data"]), 1)
        self.assertEqual(diff["modified_data"][0]["after"], 40.0)
        self.assertIn("Mesh", diff["unchanged_aspects"])

    def test_02_declarative_capability_addition_auto_resolve(self):
        """Test 2: Capability Resolution - Agregar PICKUP resuelve y agrega automáticamente INTERACTABLE."""
        res = self.gp_api.add_capability("sword_01", "PICKUP")
        self.assertTrue(res["success"])
        caps = self.gp_engine.get_actor_capabilities("sword_01")
        self.assertIn("INTERACTABLE", caps)
        self.assertIn("PICKUP", caps)

    def test_03_capability_chain_resolution(self):
        """Test 3: Capability Chain - Agregar EQUIPPABLE resuelve INTERACTABLE, PICKUP y EQUIPPABLE."""
        res = self.gp_api.add_capability("sword_01", "EQUIPPABLE")
        self.assertTrue(res["success"])
        caps = self.gp_engine.get_actor_capabilities("sword_01")
        self.assertEqual(set(caps), {"INTERACTABLE", "PICKUP", "EQUIPPABLE"})

    def test_04_duplicate_capability_noop(self):
        """Test 4: NO_OP - Re-agregar capabilities existentes devuelve NO_OP."""
        self.gp_api.add_capability("sword_01", "PICKUP")
        res = self.gp_api.add_capability("sword_01", "PICKUP")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "NO_OP")

    def test_05_unknown_capability_validation(self):
        """Test 5: Unknown capability - Capacidad inexistente devuelve CAPABILITY_NOT_FOUND."""
        res = self.gp_api.add_capability("sword_01", "SUPER_MAGIC_FLYING")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "CAPABILITY_NOT_FOUND")

    def test_06_interaction_registration(self):
        """Test 6: Interaction registration - Registra interacción PICK_UP con condiciones y acciones."""
        res = self.gp_api.register_interaction(
            actor_id="sword_01",
            verb="PICK_UP",
            conditions=[{"type": "PLAYER_NEAR", "params": {"max_distance": 200.0}}],
            actions=[{"type": "REMOVE_WORLD_ITEM"}, {"type": "ADD_INVENTORY_ITEM"}]
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["verb"], "PICK_UP")

    def test_07_interaction_simulation_success(self):
        """Test 7: Simulation success - Simulación con jugador a 100cm (<200cm) ejecuta las acciones."""
        self.gp_api.register_interaction(
            actor_id="sword_01",
            verb="PICK_UP",
            conditions=[{"type": "PLAYER_NEAR", "params": {"max_distance": 200.0}}],
            actions=[{"type": "REMOVE_WORLD_ITEM"}, {"type": "ADD_INVENTORY_ITEM"}]
        )
        sim = self.gp_api.simulate("inter_pick_up_sword_01", {"player_distance": 100.0})
        self.assertTrue(sim["success"])
        self.assertEqual(sim["executed_actions"], ["REMOVE_WORLD_ITEM", "ADD_INVENTORY_ITEM"])

    def test_08_interaction_simulation_distance_failure(self):
        """Test 8: Simulation failure - Jugador a 300cm (>200cm) devuelve PLAYER_TOO_FAR."""
        self.gp_api.register_interaction(
            actor_id="sword_01",
            verb="PICK_UP",
            conditions=[{"type": "PLAYER_NEAR", "params": {"max_distance": 200.0}}],
            actions=[{"type": "REMOVE_WORLD_ITEM"}]
        )
        sim = self.gp_api.simulate("inter_pick_up_sword_01", {"player_distance": 300.0})
        self.assertFalse(sim["success"])
        self.assertEqual(sim["failure_reason"], "PLAYER_TOO_FAR")

    def test_09_state_machine_valid_transition(self):
        """Test 9: State Machine - Transición permitida CLOSED -> OPENING -> OPEN."""
        sm = StateMachine("door_sm", initial_state="CLOSED")
        sm.add_state("CLOSED", allowed_transitions=["OPENING"])
        sm.add_state("OPENING", allowed_transitions=["OPEN"])
        sm.add_state("OPEN", allowed_transitions=["CLOSING"])

        ok1, _ = sm.transition_to("OPENING")
        self.assertTrue(ok1)
        ok2, _ = sm.transition_to("OPEN")
        self.assertTrue(ok2)
        self.assertEqual(sm.current_state, "OPEN")

    def test_10_state_machine_invalid_transition(self):
        """Test 10: State Machine - Transición prohibida OPEN -> OPENING devuelve INVALID_STATE_TRANSITION."""
        sm = StateMachine("door_sm", initial_state="OPEN")
        sm.add_state("OPEN", allowed_transitions=["CLOSING"])
        ok, err = sm.transition_to("OPENING")
        self.assertFalse(ok)
        self.assertIn("INVALID_STATE_TRANSITION", err)

    def test_11_event_bus_publish_subscribe(self):
        """Test 11: EventBus - Publicar evento DAMAGED notifica al listener."""
        received = []
        self.gp_engine.event_bus.subscribe("DAMAGED", lambda e: received.append(e.payload.get("amount")))
        self.gp_engine.event_bus.publish(GameplayEvent("DAMAGED", "sword_01", "enemy_01", {"amount": 25}))
        self.assertEqual(received, [25])

    def test_12_event_bus_chain_limit(self):
        """Test 12: Event recursion protection - Exceder max_depth=32 devuelve EVENT_CHAIN_LIMIT."""
        ok, err = self.gp_engine.event_bus.publish(GameplayEvent("LOOP", "s1"), current_depth=35)
        self.assertFalse(ok)
        self.assertIn("EVENT_CHAIN_LIMIT", err)

    def test_13_data_instance_override_isolation(self):
        """Test 13: Data instance isolation - Override en sword_01 no afecta sword_02."""
        self.gp_api.set_data("sword_01", "damage", 50.0)
        self.gp_api.set_data("sword_02", "damage", 25.0)

        d1 = self.gp_engine.actor_data["sword_01"].get_effective("damage")
        d2 = self.gp_engine.actor_data["sword_02"].get_effective("damage")
        self.assertEqual(d1, 50.0)
        self.assertEqual(d2, 25.0)

    def test_14_dry_run_mode(self):
        """Test 14: Dry run - dry_run=True retorna diff sin registrar capability real."""
        res = self.gp_api.add_capability("sword_dry", "PICKUP", dry_run=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "dry_run")
        caps = self.gp_engine.get_actor_capabilities("sword_dry")
        self.assertEqual(caps, [])

    def test_15_scope_enforcement(self):
        """Test 15: Scope - Bloquea operaciones fuera del scope."""
        res = self.gp_api.add_capability("sword_01", "PICKUP", scope=["other_actor"])
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "GAMEPLAY_SCOPE_VIOLATION")

    def test_16_gameplay_manifest_export(self):
        """Test 16: Gameplay manifest - Exporta manifiesto completo."""
        self.gp_api.add_capability("sword_01", "EQUIPPABLE")
        self.gp_api.set_data("sword_01", "damage", 40.0)
        self.gp_api.register_interaction("sword_01", "PICK_UP")

        man = self.gp_api.get_manifest("sword_01")
        self.assertEqual(man["actor_id"], "sword_01")
        self.assertIn("EQUIPPABLE", man["capabilities"])
        self.assertEqual(man["data"]["damage"], 40.0)
        self.assertIn("PICK_UP", man["interactions"])

if __name__ == "__main__":
    unittest.main()
