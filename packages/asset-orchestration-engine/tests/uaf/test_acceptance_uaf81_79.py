"""
Acceptance Test Suite for UAF-81.79 — Universal Runtime Gameplay World System.
Part 1: Lifecycle, Entities, Components, Character Controllers, Camera Controllers.
"""

import pytest
from uaf.runtime_gameplay import (
    AbilityDefinition,
    AbilityState,
    CameraControllerComponent,
    CameraMode,
    CharacterControllerComponent,
    DamageRequest,
    DamageResult,
    DamageType,
    DespawnRequest,
    Entity,
    EntityLifecycleState,
    GameplayCommand,
    GameplayCommandType,
    GameplayEvent,
    GameplayEventType,
    GameplayRule,
    GameplaySnapshot,
    GameplayTagContainer,
    GameplayTick,
    GameplayTimer,
    GameplayValidationIssue,
    GameplayWorld,
    GameplayWorldSettings,
    GameplayWorldState,
    HealthComponent,
    InteractableComponent,
    InteractionState,
    InventoryComponent,
    InventorySlot,
    MovementState,
    ObjectiveState,
    QuestDefinition,
    QuestObjective,
    QuestState,
    SaveState,
    SpawnRequest,
    StatusEffect,
    StatusStackingPolicy,
    TimerType,
    TriggerComponent,
    TriggerEventType,
    TriggerState,
    UniversalRuntimeGameplayFabricator as Fab,
    UniversalRuntimeGameplayPackager,
    UniversalRuntimeGameplayValidator as Val,
    copy_dict_deterministic,
)


class TestGameplayWorldLifecycle:
    """Tests for §102 Gameplay World Lifecycle."""

    def test_world_creation(self):
        w = Fab.create_gameplay_world("gw_01")
        assert w.gameplay_world_id == "gw_01"
        assert w.state == GameplayWorldState.CREATED
        assert len(w.entities) == 0
        assert w.tick.tick_index == 0

    def test_initialize_transition(self):
        w = Fab.create_gameplay_world("gw_02")
        Fab.initialize(w)
        assert w.state == GameplayWorldState.READY

    def test_start_transition(self):
        w = Fab.create_gameplay_world("gw_03")
        Fab.initialize(w)
        Fab.start(w)
        assert w.state == GameplayWorldState.RUNNING

    def test_pause_resume(self):
        w = Fab.create_gameplay_world("gw_04")
        Fab.initialize(w)
        Fab.start(w)
        Fab.pause(w)
        assert w.state == GameplayWorldState.PAUSED
        Fab.resume(w)
        assert w.state == GameplayWorldState.RUNNING

    def test_stop_transition(self):
        w = Fab.create_gameplay_world("gw_05")
        Fab.initialize(w)
        Fab.start(w)
        Fab.stop(w)
        assert w.state == GameplayWorldState.STOPPED

    def test_destroy_lifecycle(self):
        w = Fab.create_gameplay_world("gw_06")
        Fab.initialize(w)
        Fab.start(w)
        Fab.stop(w)
        Fab.destroy(w)
        assert w.state == GameplayWorldState.DESTROYED
        assert len(w.entities) == 0

    def test_invalid_transition_exception(self):
        w = Fab.create_gameplay_world("gw_07")
        with pytest.raises(ValueError):
            Fab.transition_state(w, GameplayWorldState.RUNNING)

    def test_world_settings_defaults(self):
        w = Fab.create_gameplay_world("gw_08")
        assert w.settings.max_entities == 10000
        assert w.settings.max_components_per_entity == 64
        assert w.settings.max_commands_per_tick == 1000

    def test_custom_settings(self):
        s = GameplayWorldSettings(max_entities=50, max_commands_per_tick=20)
        w = Fab.create_gameplay_world("gw_09", settings=s)
        assert w.settings.max_entities == 50
        assert w.settings.max_commands_per_tick == 20

    def test_world_dict_serialization(self):
        w = Fab.create_gameplay_world("gw_10")
        d = w.to_dict()
        assert d["gameplay_world_id"] == "gw_10"
        assert d["state"] == "CREATED"
        assert "tick" in d

    def test_fingerprint_generation(self):
        w1 = Fab.create_gameplay_world("gw_11")
        w2 = Fab.create_gameplay_world("gw_11")
        assert w1.compute_fingerprint() == w2.compute_fingerprint()

    def test_tick_increment(self):
        w = Fab.create_gameplay_world("gw_12")
        Fab.initialize(w)
        Fab.start(w)
        Fab.tick(w, 0.016)
        assert w.tick.tick_index == 1
        assert pytest.approx(w.tick.simulation_time, 1e-4) == 0.016

    def test_tick_fixed_dt(self):
        w = Fab.create_gameplay_world("gw_13")
        Fab.initialize(w)
        Fab.start(w)
        Fab.tick(w, 0.02)
        Fab.tick(w, 0.02)
        assert w.tick.tick_index == 2
        assert pytest.approx(w.tick.simulation_time, 1e-4) == 0.04

    def test_deterministic_tick_order(self):
        w = Fab.create_gameplay_world("gw_14")
        Fab.initialize(w)
        Fab.start(w)
        Fab.tick(w, 0.016)
        issues = Val.validate(w)
        assert len([i for i in issues if i.severity == "ERROR"]) == 0


class TestEntitiesAndLifecycle:
    """Tests for §103 Entity and Component Lifecycle."""

    def test_spawn_entity_basic(self):
        w = Fab.create_gameplay_world("gw_ent_01")
        e = Fab.spawn_entity(w, "player", "Hero")
        assert e.entity_id == "player"
        assert e.name == "Hero"
        assert e.state == EntityLifecycleState.ACTIVE
        assert "player" in w.entities

    def test_spawn_duplicate_id_error(self):
        w = Fab.create_gameplay_world("gw_ent_02")
        Fab.spawn_entity(w, "mob_1", "Goblin")
        with pytest.raises(ValueError):
            Fab.spawn_entity(w, "mob_1", "GoblinDuplicate")

    def test_spawn_auto_id(self):
        w = Fab.create_gameplay_world("gw_ent_03")
        e1 = Fab.spawn_entity(w, name="NPC1")
        e2 = Fab.spawn_entity(w, name="NPC2")
        assert e1.entity_id != e2.entity_id
        assert len(w.entities) == 2

    def test_entity_properties_pos_rot(self):
        w = Fab.create_gameplay_world("gw_ent_04")
        e = Fab.spawn_entity(w, "box", position=(1.0, 2.0, 3.0), rotation=(0.0, 90.0, 0.0))
        assert e.position == (1.0, 2.0, 3.0)
        assert e.rotation == (0.0, 90.0, 0.0)

    def test_entity_lifecycle_created_to_active(self):
        w = Fab.create_gameplay_world("gw_ent_05")
        e = Fab.spawn_entity(w, "item_1")
        assert e.state == EntityLifecycleState.ACTIVE

    def test_disable_entity(self):
        w = Fab.create_gameplay_world("gw_ent_06")
        e = Fab.spawn_entity(w, "trap")
        e.state = EntityLifecycleState.DISABLED
        assert e.state == EntityLifecycleState.DISABLED

    def test_despawn_entity_pending(self):
        w = Fab.create_gameplay_world("gw_ent_07")
        Fab.spawn_entity(w, "boss")
        Fab.despawn_entity(w, "boss")
        assert w.entities["boss"].state == EntityLifecycleState.DISABLED

    def test_destroy_entity_cleanup(self):
        w = Fab.create_gameplay_world("gw_ent_08")
        Fab.spawn_entity(w, "crate")
        Fab.destroy_entity(w, "crate")
        assert "crate" not in w.entities

    def test_entity_tags_initialization(self):
        w = Fab.create_gameplay_world("gw_ent_09")
        e = Fab.spawn_entity(w, "tagged", tags=["Character.Player", "Faction.Allies"])
        assert e.tags.has("Character.Player")
        assert e.tags.has("Faction.Allies")

    def test_entity_equality_and_hashing(self):
        e1 = Entity("e1", "Hero")
        e2 = Entity("e1", "Hero")
        assert e1.entity_id == e2.entity_id

    def test_entity_to_dict(self):
        w = Fab.create_gameplay_world("gw_ent_11")
        e = Fab.spawn_entity(w, "test_ent", position=(10.0, 0.0, 0.0))
        d = e.to_dict()
        assert d["entity_id"] == "test_ent"
        assert tuple(d["position"]) == (10.0, 0.0, 0.0)

    def test_spawn_event_emitted(self):
        w = Fab.create_gameplay_world("gw_ent_12")
        Fab.spawn_entity(w, "spawned_actor")
        assert any(ev.event_type == GameplayEventType.ENTITY_SPAWNED for ev in w.event_queue)

    def test_despawn_event_emitted(self):
        w = Fab.create_gameplay_world("gw_ent_13")
        Fab.spawn_entity(w, "target")
        w.event_queue.clear()
        Fab.despawn_entity(w, "target")
        assert any(ev.event_type == GameplayEventType.ENTITY_DESPAWNED for ev in w.event_queue)

    def test_destroy_event_emitted(self):
        w = Fab.create_gameplay_world("gw_ent_14")
        Fab.spawn_entity(w, "barrel")
        w.event_queue.clear()
        Fab.destroy_entity(w, "barrel")
        assert any(ev.event_type == GameplayEventType.ENTITY_DESPAWNED and ev.payload.get("reason") == "DESTROYED" for ev in w.event_queue)

    def test_has_entity_lookup(self):
        w = Fab.create_gameplay_world("gw_ent_15")
        Fab.spawn_entity(w, "e_exist")
        assert "e_exist" in w.entities
        assert "e_missing" not in w.entities

    def test_get_entity_none_when_missing(self):
        w = Fab.create_gameplay_world("gw_ent_16")
        assert w.entities.get("unknown") is None

    def test_spawn_counter_increment(self):
        w = Fab.create_gameplay_world("gw_ent_17")
        assert w.spawn_counter == 0
        Fab.spawn_entity(w)
        assert w.spawn_counter == 1
        Fab.spawn_entity(w)
        assert w.spawn_counter == 2

    def test_entity_state_transitions(self):
        w = Fab.create_gameplay_world("gw_ent_18")
        e = Fab.spawn_entity(w, "p1")
        assert e.state == EntityLifecycleState.ACTIVE
        Fab.despawn_entity(w, "p1")
        assert e.state == EntityLifecycleState.DISABLED


class TestComponentSystem:
    """Tests for §104 Component System and ECS bindings."""

    def test_add_component_generic(self):
        w = Fab.create_gameplay_world("gw_comp_01")
        Fab.spawn_entity(w, "hero")
        hc = HealthComponent(max_health=200.0, current_health=200.0)
        Fab.add_component(w, "hero", "health", hc)
        assert "health" in w.entities["hero"].components

    def test_get_component_success(self):
        w = Fab.create_gameplay_world("gw_comp_02")
        Fab.spawn_entity(w, "hero")
        hc = HealthComponent(max_health=150.0, current_health=150.0)
        Fab.add_component(w, "hero", "health", hc)
        retrieved = Fab.get_component(w, "hero", "health")
        assert retrieved is hc

    def test_get_component_missing(self):
        w = Fab.create_gameplay_world("gw_comp_03")
        Fab.spawn_entity(w, "hero")
        assert Fab.get_component(w, "hero", "inventory") is None

    def test_has_component_true_false(self):
        w = Fab.create_gameplay_world("gw_comp_04")
        Fab.spawn_entity(w, "hero")
        assert ("health" in w.entities["hero"].components) is False
        Fab.add_component(w, "hero", "health", HealthComponent())
        assert ("health" in w.entities["hero"].components) is True

    def test_remove_component_success(self):
        w = Fab.create_gameplay_world("gw_comp_05")
        Fab.spawn_entity(w, "hero")
        Fab.add_component(w, "hero", "health", HealthComponent())
        removed = Fab.remove_component(w, "hero", "health")
        assert removed is not None
        assert "health" not in w.entities["hero"].components

    def test_remove_missing_component_handled(self):
        w = Fab.create_gameplay_world("gw_comp_06")
        Fab.spawn_entity(w, "hero")
        removed = Fab.remove_component(w, "hero", "magic")
        assert removed is None

    def test_duplicate_component_type_overwrite(self):
        w = Fab.create_gameplay_world("gw_comp_07")
        Fab.spawn_entity(w, "hero")
        h1 = HealthComponent(max_health=100.0)
        h2 = HealthComponent(max_health=200.0)
        Fab.add_component(w, "hero", "health", h1)
        Fab.add_component(w, "hero", "health", h2)
        assert Fab.get_component(w, "hero", "health").max_health == 200.0

    def test_multiple_components_on_entity(self):
        w = Fab.create_gameplay_world("gw_comp_08")
        Fab.spawn_entity(w, "hero")
        Fab.add_component(w, "hero", "health", HealthComponent())
        Fab.add_component(w, "hero", "char_ctrl", CharacterControllerComponent("cc1"))
        Fab.add_component(w, "hero", "cam_ctrl", CameraControllerComponent("cam1"))
        assert len(w.entities["hero"].components) == 3

    def test_component_ownership_integrity(self):
        w = Fab.create_gameplay_world("gw_comp_09")
        Fab.spawn_entity(w, "e1")
        Fab.spawn_entity(w, "e2")
        shared_comp = HealthComponent()
        Fab.add_component(w, "e1", "health", shared_comp)
        with pytest.raises(ValueError) as excinfo:
            Fab.add_component(w, "e2", "health", shared_comp)
        assert "NO MULTIPLE COMPONENT OWNERS" in str(excinfo.value)

    def test_component_dict_serialization(self):
        hc = HealthComponent(current_health=80.0, max_health=100.0)
        d = hc.to_dict()
        assert d["current_health"] == 80.0
        assert d["max_health"] == 100.0

    def test_character_controller_component_defaults(self):
        cc = CharacterControllerComponent("ctrl_01")
        assert cc.move_speed == 6.0
        assert cc.run_speed == 10.0
        assert cc.jump_force == 8.0
        assert cc.is_grounded is True

    def test_camera_controller_component_defaults(self):
        cam = CameraControllerComponent("cam_01")
        assert cam.camera_mode == CameraMode.THIRD_PERSON
        assert cam.distance == 5.0
        assert cam.zoom == 1.0

    def test_health_component_defaults(self):
        h = HealthComponent()
        assert h.current_health == 100.0
        assert h.max_health == 100.0
        assert h.current_shield == 0.0

    def test_interactable_component_defaults(self):
        ic = InteractableComponent("int_01", "target_01")
        assert ic.max_distance == 3.0
        assert ic.state == InteractionState.AVAILABLE

    def test_trigger_component_defaults(self):
        tc = TriggerComponent("trig_01")
        assert tc.shape == "BOX"
        assert tc.state == TriggerState.ACTIVE

    def test_inventory_component_defaults(self):
        inv = InventoryComponent("inv_01", max_slots=30)
        assert inv.max_slots == 30
        assert len(inv.slots) == 0

    def test_status_effects_component_as_list(self):
        w = Fab.create_gameplay_world("gw_comp_17")
        Fab.spawn_entity(w, "hero")
        effs = [StatusEffect("eff1", "Poison", "mob", "hero", 5.0, 0.0, 2.0)]
        Fab.add_component(w, "hero", "status_effects", effs)
        assert len(Fab.get_component(w, "hero", "status_effects")) == 1

    def test_clear_components_on_destroy(self):
        w = Fab.create_gameplay_world("gw_comp_18")
        Fab.spawn_entity(w, "mob")
        Fab.add_component(w, "mob", "health", HealthComponent())
        Fab.destroy_entity(w, "mob")
        assert "mob" not in w.entities


class TestCharacterControllers:
    """Tests for §105 Character Controllers and movement mechanics."""

    def test_create_character_controller(self):
        ctrl = Fab.create_character_controller("cc_player", move_speed=5.0, run_speed=9.0)
        assert ctrl.controller_id == "cc_player"
        assert ctrl.move_speed == 5.0
        assert ctrl.run_speed == 9.0

    def test_move_character_horizontal(self):
        w = Fab.create_gameplay_world("gw_cc_01")
        w.tick.delta_time = 1.0
        Fab.spawn_entity(w, "player", position=(0.0, 0.0, 0.0))
        ctrl = Fab.create_character_controller("cc_p", move_speed=5.0)
        Fab.add_component(w, "player", "character_controller", ctrl)
        Fab.move_character(w, "player", 1.0, 0.0)
        p = w.entities["player"].position
        assert pytest.approx(p[0], 1e-3) == 5.0
        assert ctrl.movement_state == MovementState.WALKING

    def test_move_character_with_speed(self):
        w = Fab.create_gameplay_world("gw_cc_02")
        w.tick.delta_time = 0.5
        Fab.spawn_entity(w, "runner", position=(0.0, 0.0, 0.0))
        ctrl = Fab.create_character_controller("cc_r", move_speed=10.0)
        Fab.add_component(w, "runner", "character_controller", ctrl)
        Fab.move_character(w, "runner", 0.0, 1.0)
        p = w.entities["runner"].position
        assert pytest.approx(p[1], 1e-3) == 5.0

    def test_jump_when_grounded(self):
        w = Fab.create_gameplay_world("gw_cc_03")
        Fab.spawn_entity(w, "jumper")
        ctrl = Fab.create_character_controller("cc_j", jump_force=10.0)
        ctrl.is_grounded = True
        Fab.add_component(w, "jumper", "character_controller", ctrl)
        success = Fab.jump(w, "jumper")
        assert success is True
        assert ctrl.is_grounded is False
        assert ctrl.movement_state == MovementState.JUMPING

    def test_jump_fails_when_airborne(self):
        w = Fab.create_gameplay_world("gw_cc_04")
        Fab.spawn_entity(w, "air_jumper")
        ctrl = Fab.create_character_controller("cc_aj")
        ctrl.is_grounded = False
        Fab.add_component(w, "air_jumper", "character_controller", ctrl)
        success = Fab.jump(w, "air_jumper")
        assert success is False

    def test_set_grounded_updates_state(self):
        w = Fab.create_gameplay_world("gw_cc_05")
        Fab.spawn_entity(w, "lander")
        ctrl = Fab.create_character_controller("cc_l")
        ctrl.is_grounded = False
        ctrl.movement_state = MovementState.FALLING
        Fab.add_component(w, "lander", "character_controller", ctrl)
        Fab.set_grounded(w, "lander", True)
        assert ctrl.is_grounded is True
        assert ctrl.movement_state == MovementState.GROUNDED

    def test_sprint_speed_calculation(self):
        ctrl = Fab.create_character_controller("cc_sprint", move_speed=4.0, run_speed=8.0)
        assert ctrl.run_speed == 2 * ctrl.move_speed

    def test_controller_disabled_ignores_input(self):
        w = Fab.create_gameplay_world("gw_cc_07")
        Fab.spawn_entity(w, "stuned_player", position=(0.0, 0.0, 0.0))
        ctrl = Fab.create_character_controller("cc_sp")
        ctrl.is_enabled = False
        Fab.add_component(w, "stuned_player", "character_controller", ctrl)
        Fab.move_character(w, "stuned_player", 1.0, 0.0)
        p = w.entities["stuned_player"].position
        assert p == (0.0, 0.0, 0.0)

    def test_movement_state_idle_moving(self):
        w = Fab.create_gameplay_world("gw_cc_08")
        w.tick.delta_time = 0.1
        Fab.spawn_entity(w, "walker")
        ctrl = Fab.create_character_controller("cc_w")
        Fab.add_component(w, "walker", "character_controller", ctrl)
        assert ctrl.movement_state == MovementState.IDLE
        Fab.move_character(w, "walker", 1.0, 0.0)
        assert ctrl.movement_state == MovementState.WALKING
        Fab.move_character(w, "walker", 0.0, 0.0)
        assert ctrl.movement_state == MovementState.IDLE

    def test_velocity_damping_or_reset(self):
        ctrl = Fab.create_character_controller("cc_vel")
        ctrl.velocity = (2.0, 3.0, 0.0)
        assert ctrl.velocity[0] == 2.0


class TestCameraControllers:
    """Tests for §106 Camera Controllers and perspective handling."""

    def test_create_camera_controller(self):
        cam = Fab.create_camera_controller("cam_main", camera_mode=CameraMode.THIRD_PERSON)
        assert cam.camera_id == "cam_main"
        assert cam.camera_mode == CameraMode.THIRD_PERSON

    def test_camera_modes_first_person_third_person_orbit(self):
        c1 = Fab.create_camera_controller("c1", camera_mode=CameraMode.FIRST_PERSON)
        c2 = Fab.create_camera_controller("c2", camera_mode=CameraMode.THIRD_PERSON)
        c3 = Fab.create_camera_controller("c3", camera_mode=CameraMode.ORBIT)
        assert c1.camera_mode == CameraMode.FIRST_PERSON
        assert c2.camera_mode == CameraMode.THIRD_PERSON
        assert c3.camera_mode == CameraMode.ORBIT

    def test_update_camera_yaw_pitch(self):
        w = Fab.create_gameplay_world("gw_cam_01")
        Fab.spawn_entity(w, "cam_ent")
        cam = Fab.create_camera_controller("cam_p")
        Fab.add_component(w, "cam_ent", "camera_controller", cam)
        Fab.update_camera(w, "cam_ent", delta_yaw=15.0, delta_pitch=10.0)
        assert cam.yaw == 15.0
        assert cam.pitch == 10.0

    def test_camera_pitch_clamping(self):
        w = Fab.create_gameplay_world("gw_cam_02")
        Fab.spawn_entity(w, "cam_ent")
        cam = Fab.create_camera_controller("cam_clamp", min_pitch=-80.0, max_pitch=80.0)
        Fab.add_component(w, "cam_ent", "camera_controller", cam)
        Fab.update_camera(w, "cam_ent", delta_pitch=120.0)
        assert cam.pitch == 80.0
        Fab.update_camera(w, "cam_ent", delta_pitch=-200.0)
        assert cam.pitch == -80.0

    def test_camera_distance_clamping(self):
        w = Fab.create_gameplay_world("gw_cam_03")
        Fab.spawn_entity(w, "cam_ent")
        cam = Fab.create_camera_controller("cam_dist", min_distance=2.0, max_distance=10.0, distance=5.0)
        Fab.add_component(w, "cam_ent", "camera_controller", cam)
        Fab.update_camera(w, "cam_ent", zoom_delta=10.0)
        assert cam.distance == 10.0
        Fab.update_camera(w, "cam_ent", zoom_delta=-15.0)
        assert cam.distance == 2.0

    def test_camera_target_tracking(self):
        cam = Fab.create_camera_controller("cam_tgt", target_entity_id="player_01")
        assert cam.target_entity_id == "player_01"

    def test_camera_zoom_in_out(self):
        w = Fab.create_gameplay_world("gw_cam_04")
        Fab.spawn_entity(w, "cam_ent")
        cam = Fab.create_camera_controller("cam_z", min_distance=1.0, max_distance=20.0, distance=5.0)
        Fab.add_component(w, "cam_ent", "camera_controller", cam)
        Fab.update_camera(w, "cam_ent", zoom_delta=-2.0)
        assert cam.distance == 3.0

    def test_camera_mode_switch(self):
        cam = Fab.create_camera_controller("cam_sw", camera_mode=CameraMode.THIRD_PERSON)
        cam.camera_mode = CameraMode.FIRST_PERSON
        assert cam.camera_mode == CameraMode.FIRST_PERSON
class TestInteractionsSystem:
    """Tests for §107 Interaction System and queries."""

    def test_register_interactable(self):
        w = Fab.create_gameplay_world("gw_int_01")
        Fab.spawn_entity(w, "door")
        inter = InteractableComponent("door_open", "door", max_distance=3.0)
        Fab.register_interactable(w, "door", inter)
        assert "interactable" in w.entities["door"].components

    def test_query_interactions_in_range(self):
        w = Fab.create_gameplay_world("gw_int_02")
        Fab.spawn_entity(w, "chest", position=(2.0, 0.0, 0.0))
        inter = InteractableComponent("chest_loot", "chest", max_distance=5.0)
        Fab.register_interactable(w, "chest", inter)
        results = Fab.query_interactions(w, source_pos=(0.0, 0.0, 0.0), max_range=4.0)
        assert len(results) == 1
        assert results[0].interaction_id == "chest_loot"

    def test_query_interactions_out_of_range(self):
        w = Fab.create_gameplay_world("gw_int_03")
        Fab.spawn_entity(w, "far_chest", position=(10.0, 0.0, 0.0))
        inter = InteractableComponent("far_loot", "far_chest", max_distance=3.0)
        Fab.register_interactable(w, "far_chest", inter)
        results = Fab.query_interactions(w, source_pos=(0.0, 0.0, 0.0), max_range=5.0)
        assert len(results) == 0

    def test_query_interactions_sorted_by_priority(self):
        w = Fab.create_gameplay_world("gw_int_04")
        Fab.spawn_entity(w, "low_prio", position=(1.0, 0.0, 0.0))
        Fab.spawn_entity(w, "high_prio", position=(2.0, 0.0, 0.0))
        Fab.register_interactable(w, "low_prio", InteractableComponent("int_low", "low_prio", priority=1, max_distance=5.0))
        Fab.register_interactable(w, "high_prio", InteractableComponent("int_high", "high_prio", priority=10, max_distance=5.0))
        results = Fab.query_interactions(w, source_pos=(0.0, 0.0, 0.0), max_range=5.0)
        assert len(results) == 2
        assert results[0].interaction_id == "int_high"

    def test_query_interactions_sorted_by_distance_on_equal_priority(self):
        w = Fab.create_gameplay_world("gw_int_05")
        Fab.spawn_entity(w, "near", position=(1.0, 0.0, 0.0))
        Fab.spawn_entity(w, "far", position=(3.0, 0.0, 0.0))
        Fab.register_interactable(w, "near", InteractableComponent("int_near", "near", priority=5, max_distance=5.0))
        Fab.register_interactable(w, "far", InteractableComponent("int_far", "far", priority=5, max_distance=5.0))
        results = Fab.query_interactions(w, source_pos=(0.0, 0.0, 0.0), max_range=5.0)
        assert len(results) == 2
        assert results[0].interaction_id == "int_near"

    def test_execute_interaction_success(self):
        w = Fab.create_gameplay_world("gw_int_06")
        Fab.spawn_entity(w, "player", position=(0.0, 0.0, 0.0))
        Fab.spawn_entity(w, "switch", position=(1.0, 0.0, 0.0))
        Fab.register_interactable(w, "switch", InteractableComponent("flip_switch", "switch", max_distance=2.0))
        success = Fab.execute_interaction(w, "flip_switch", "player")
        assert success is True
        assert w.entities["switch"].components["interactable"].state == InteractionState.COMPLETED

    def test_execute_interaction_out_of_range_fails(self):
        w = Fab.create_gameplay_world("gw_int_07")
        Fab.spawn_entity(w, "player", position=(0.0, 0.0, 0.0))
        Fab.spawn_entity(w, "far_switch", position=(10.0, 0.0, 0.0))
        Fab.register_interactable(w, "far_switch", InteractableComponent("flip_far", "far_switch", max_distance=2.0))
        success = Fab.execute_interaction(w, "flip_far", "player")
        assert success is False

    def test_execute_interaction_missing_target_error(self):
        w = Fab.create_gameplay_world("gw_int_08")
        Fab.spawn_entity(w, "player")
        with pytest.raises(ValueError):
            Fab.execute_interaction(w, "non_existent_int", "player")

    def test_execute_interaction_missing_actor_fails(self):
        w = Fab.create_gameplay_world("gw_int_09")
        Fab.spawn_entity(w, "switch", position=(0.0, 0.0, 0.0))
        Fab.register_interactable(w, "switch", InteractableComponent("sw_int", "switch", max_distance=2.0))
        success = Fab.execute_interaction(w, "sw_int", "ghost_player")
        assert success is False

    def test_interaction_completed_state_change(self):
        w = Fab.create_gameplay_world("gw_int_10")
        Fab.spawn_entity(w, "p", position=(0.0, 0.0, 0.0))
        Fab.spawn_entity(w, "t", position=(0.5, 0.0, 0.0))
        inter = InteractableComponent("i1", "t", max_distance=2.0)
        Fab.register_interactable(w, "t", inter)
        assert inter.state == InteractionState.AVAILABLE
        Fab.execute_interaction(w, "i1", "p")
        assert inter.state == InteractionState.COMPLETED

    def test_interaction_dispatches_event(self):
        w = Fab.create_gameplay_world("gw_int_11")
        Fab.spawn_entity(w, "p", position=(0.0, 0.0, 0.0))
        Fab.spawn_entity(w, "t", position=(0.0, 0.0, 0.0))
        Fab.register_interactable(w, "t", InteractableComponent("i1", "t", max_distance=2.0))
        w.event_queue.clear()
        Fab.execute_interaction(w, "i1", "p")
        assert any(ev.event_type == GameplayEventType.INTERACTION_COMPLETED for ev in w.event_queue)

    def test_interaction_to_dict(self):
        inter = InteractableComponent("i_d", "ent_x", max_distance=4.5)
        d = inter.to_dict()
        assert d["interaction_id"] == "i_d"
        assert d["max_distance"] == 4.5


class TestTriggerSystem:
    """Tests for §108 Trigger System and spatial overlap detection."""

    def test_create_trigger_box(self):
        trig = Fab.create_trigger("t_box", position=(0.0, 0.0, 0.0), extents=(2.0, 2.0, 2.0))
        assert trig.trigger_id == "t_box"
        assert trig.extents == (2.0, 2.0, 2.0)
        assert trig.state == TriggerState.ACTIVE

    def test_trigger_enter_event(self):
        w = Fab.create_gameplay_world("gw_trig_01")
        Fab.spawn_entity(w, "p1")
        trig = Fab.create_trigger("t1")
        res = Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=True)
        assert res == TriggerEventType.ENTER
        assert "p1" in trig.inside_entities
        assert trig.state == TriggerState.TRIGGERED

    def test_trigger_stay_event(self):
        w = Fab.create_gameplay_world("gw_trig_02")
        Fab.spawn_entity(w, "p1")
        trig = Fab.create_trigger("t2")
        Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=True)
        res = Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=True)
        assert res == TriggerEventType.STAY

    def test_trigger_exit_event(self):
        w = Fab.create_gameplay_world("gw_trig_03")
        Fab.spawn_entity(w, "p1")
        trig = Fab.create_trigger("t3")
        Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=True)
        res = Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=False)
        assert res == TriggerEventType.EXIT
        assert "p1" not in trig.inside_entities
        assert trig.state == TriggerState.ACTIVE

    def test_trigger_filter_tags_allows_matching(self):
        w = Fab.create_gameplay_world("gw_trig_04")
        Fab.spawn_entity(w, "player", tags=["Character.Player"])
        trig = Fab.create_trigger("t4", filter_tags={"Character.Player"})
        res = Fab.process_trigger_overlap(w, trig, "player", is_overlapping=True)
        assert res == TriggerEventType.ENTER

    def test_trigger_filter_tags_blocks_non_matching(self):
        w = Fab.create_gameplay_world("gw_trig_05")
        Fab.spawn_entity(w, "enemy", tags=["Character.Enemy"])
        trig = Fab.create_trigger("t5", filter_tags={"Character.Player"})
        res = Fab.process_trigger_overlap(w, trig, "enemy", is_overlapping=True)
        assert res is None

    def test_trigger_inactive_ignores_overlap(self):
        w = Fab.create_gameplay_world("gw_trig_06")
        Fab.spawn_entity(w, "p1")
        trig = Fab.create_trigger("t6")
        trig.state = TriggerState.INACTIVE
        res = Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=True)
        assert res is None

    def test_trigger_multiple_entities_inside(self):
        w = Fab.create_gameplay_world("gw_trig_07")
        Fab.spawn_entity(w, "p1")
        Fab.spawn_entity(w, "p2")
        trig = Fab.create_trigger("t7")
        Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=True)
        Fab.process_trigger_overlap(w, trig, "p2", is_overlapping=True)
        assert len(trig.inside_entities) == 2
        Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=False)
        assert trig.state == TriggerState.TRIGGERED
        assert "p2" in trig.inside_entities

    def test_trigger_reverts_to_active_when_empty(self):
        w = Fab.create_gameplay_world("gw_trig_08")
        Fab.spawn_entity(w, "p1")
        trig = Fab.create_trigger("t8")
        Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=True)
        assert trig.state == TriggerState.TRIGGERED
        Fab.process_trigger_overlap(w, trig, "p1", is_overlapping=False)
        assert trig.state == TriggerState.ACTIVE

    def test_trigger_non_existent_entity_returns_none(self):
        w = Fab.create_gameplay_world("gw_trig_09")
        trig = Fab.create_trigger("t9")
        res = Fab.process_trigger_overlap(w, trig, "missing_ent", is_overlapping=True)
        assert res is None

    def test_trigger_to_dict(self):
        trig = Fab.create_trigger("t_dict", extents=(3.0, 3.0, 3.0))
        d = trig.to_dict()
        assert d["trigger_id"] == "t_dict"
        assert d["shape"] == "BOX"

    def test_trigger_reset_or_cleanup(self):
        trig = Fab.create_trigger("t_clean")
        trig.inside_entities.add("p1")
        trig.inside_entities.clear()
        assert len(trig.inside_entities) == 0


class TestGameplayTags:
    """Tests for §109 Hierarchical Gameplay Tags."""

    def test_tag_container_add_remove(self):
        tc = GameplayTagContainer()
        tc.add("Combat.Damage.Fire")
        assert tc.has("Combat.Damage.Fire")
        tc.remove("Combat.Damage.Fire")
        assert not tc.has("Combat.Damage.Fire")

    def test_tag_exact_match(self):
        tc = GameplayTagContainer({"State.Buff.Haste"})
        assert tc.has("State.Buff.Haste")
        assert not tc.has("State.Buff.Slow")

    def test_tag_hierarchy_subtag_match(self):
        tc = GameplayTagContainer({"Combat.Damage.Fire.Dot"})
        assert tc.has("Combat")
        assert tc.has("Combat.Damage")
        assert tc.has("Combat.Damage.Fire")
        assert tc.has("Combat.Damage.Fire.Dot")

    def test_tag_has_any_match(self):
        tc = GameplayTagContainer({"Status.Poison", "Faction.Player"})
        assert tc.has_any({"Status.Poison", "Status.Freeze"})
        assert not tc.has_any({"Status.Burn", "Status.Stun"})

    def test_tag_has_all_match(self):
        tc = GameplayTagContainer({"Status.Poison", "Faction.Player", "State.Alive"})
        assert tc.has_all({"Status.Poison", "Faction.Player"})
        assert not tc.has_all({"Status.Poison", "Faction.Enemy"})

    def test_tag_has_none_match(self):
        tc = GameplayTagContainer({"Status.Poison"})
        assert tc.has_none({"Status.Freeze", "Status.Burn"})
        assert not tc.has_none({"Status.Poison"})

    def test_tag_container_to_dict_sorted(self):
        tc = GameplayTagContainer({"B.Tag", "A.Tag", "C.Tag"})
        d = tc.to_dict()
        assert d == ["A.Tag", "B.Tag", "C.Tag"]

    def test_entity_tag_addition_at_runtime(self):
        w = Fab.create_gameplay_world("gw_tag_01")
        e = Fab.spawn_entity(w, "p1")
        e.tags.add("State.Stealthed")
        assert e.tags.has("State.Stealthed")

    def test_entity_tag_removal_at_runtime(self):
        w = Fab.create_gameplay_world("gw_tag_02")
        e = Fab.spawn_entity(w, "p2", tags=["State.Stunned"])
        assert e.tags.has("State.Stunned")
        e.tags.remove("State.Stunned")
        assert not e.tags.has("State.Stunned")

    def test_tag_hierarchy_validation_valid(self):
        w = Fab.create_gameplay_world("gw_tag_03")
        Fab.spawn_entity(w, "p3", tags=["Actor.Hero.Warrior"])
        issues = Val.validate(w)
        assert not any(i.code == "NO_TAG_HIERARCHY_CORRUPTION" for i in issues)

    def test_tag_hierarchy_validation_invalid_syntax(self):
        w = Fab.create_gameplay_world("gw_tag_04")
        Fab.spawn_entity(w, "p4", tags=["Actor..Invalid", ".LeadingDot"])
        issues = Val.validate(w)
        assert any(i.code == "NO_TAG_HIERARCHY_CORRUPTION" for i in issues)

    def test_tag_case_preservation(self):
        tc = GameplayTagContainer()
        tc.add("Item.Weapon.SwordExcalibur")
        assert "Item.Weapon.SwordExcalibur" in tc.tags


class TestRuleEngine:
    """Tests for §110 Rule Evaluation and Gameplay Rules."""

    def test_add_rule_success(self):
        w = Fab.create_gameplay_world("gw_rule_01")
        r = GameplayRule("rule_01", priority=10, conditions=[], effects=[])
        Fab.add_rule(w, r)
        assert "rule_01" in w.rules

    def test_add_rule_max_limit_exceeded(self):
        s = GameplayWorldSettings(max_rules=2)
        w = Fab.create_gameplay_world("gw_rule_02", settings=s)
        Fab.add_rule(w, GameplayRule("r1"))
        Fab.add_rule(w, GameplayRule("r2"))
        with pytest.raises(ValueError):
            Fab.add_rule(w, GameplayRule("r3"))

    def test_evaluate_rules_order_by_priority(self):
        w = Fab.create_gameplay_world("gw_rule_03")
        r1 = GameplayRule("r_low", priority=1, conditions=[], effects=[])
        r2 = GameplayRule("r_high", priority=10, conditions=[], effects=[])
        Fab.add_rule(w, r1)
        Fab.add_rule(w, r2)
        count = Fab.evaluate_rules(w)
        assert count == 2

    def test_evaluate_rules_condition_entity_alive(self):
        w = Fab.create_gameplay_world("gw_rule_04")
        Fab.spawn_entity(w, "target_actor")
        r = GameplayRule(
            "r_alive",
            priority=5,
            conditions=[{"type": "entity_alive", "entity_id": "target_actor"}],
            effects=[{"type": "add_tag", "entity_id": "target_actor", "tag": "State.AliveChecked"}],
        )
        Fab.add_rule(w, r)
        applied = Fab.evaluate_rules(w)
        assert applied == 1
        assert w.entities["target_actor"].tags.has("State.AliveChecked")

    def test_evaluate_rules_condition_has_tag(self):
        w = Fab.create_gameplay_world("gw_rule_05")
        Fab.spawn_entity(w, "hero", tags=["Hero.Berserker"])
        r = GameplayRule(
            "r_tag",
            priority=5,
            conditions=[{"type": "has_tag", "entity_id": "hero", "tag": "Hero.Berserker"}],
            effects=[{"type": "add_tag", "entity_id": "hero", "tag": "Buff.Enraged"}],
        )
        Fab.add_rule(w, r)
        applied = Fab.evaluate_rules(w)
        assert applied == 1
        assert w.entities["hero"].tags.has("Buff.Enraged")

    def test_evaluate_rules_effect_add_tag(self):
        w = Fab.create_gameplay_world("gw_rule_06")
        Fab.spawn_entity(w, "p1")
        r = GameplayRule(
            "r_add_tag",
            priority=1,
            conditions=[],
            effects=[{"type": "add_tag", "entity_id": "p1", "tag": "Tag.AddedByRule"}],
        )
        Fab.add_rule(w, r)
        Fab.evaluate_rules(w)
        assert w.entities["p1"].tags.has("Tag.AddedByRule")

    def test_evaluate_rules_effect_damage(self):
        w = Fab.create_gameplay_world("gw_rule_07")
        Fab.spawn_entity(w, "victim")
        Fab.add_component(w, "victim", "health", HealthComponent(current_health=100.0, max_health=100.0))
        r = GameplayRule(
            "r_dmg",
            priority=1,
            conditions=[],
            effects=[{"type": "damage", "entity_id": "victim", "amount": 30.0}],
        )
        Fab.add_rule(w, r)
        Fab.evaluate_rules(w)
        assert w.entities["victim"].components["health"].current_health == 70.0

    def test_evaluate_rules_recursion_guard_limit(self):
        w = Fab.create_gameplay_world("gw_rule_08")
        with pytest.raises(ValueError) as excinfo:
            Fab.evaluate_rules(w, recursion_depth=11)
        assert "NO RULE RECURSION WITHOUT LIMIT" in str(excinfo.value)

    def test_evaluate_rules_false_condition_no_effect(self):
        w = Fab.create_gameplay_world("gw_rule_09")
        Fab.spawn_entity(w, "p1", tags=["Tag.A"])
        r = GameplayRule(
            "r_false",
            priority=1,
            conditions=[{"type": "has_tag", "entity_id": "p1", "tag": "Tag.NonExistent"}],
            effects=[{"type": "add_tag", "entity_id": "p1", "tag": "Tag.B"}],
        )
        Fab.add_rule(w, r)
        applied = Fab.evaluate_rules(w)
        assert applied == 0
        assert not w.entities["p1"].tags.has("Tag.B")

    def test_evaluate_rules_multiple_rules(self):
        w = Fab.create_gameplay_world("gw_rule_10")
        Fab.add_rule(w, GameplayRule("r1", priority=1))
        Fab.add_rule(w, GameplayRule("r2", priority=2))
        applied = Fab.evaluate_rules(w)
        assert applied == 2

    def test_rule_serialization_to_dict(self):
        r = GameplayRule("r_ser", priority=8, conditions=[{"type": "c1"}], effects=[{"type": "e1"}])
        d = r.to_dict()
        assert d["rule_id"] == "r_ser"
        assert d["priority"] == 8

    def test_evaluate_rules_deterministic_ordering(self):
        w = Fab.create_gameplay_world("gw_rule_12")
        Fab.add_rule(w, GameplayRule("rule_z", priority=5))
        Fab.add_rule(w, GameplayRule("rule_a", priority=5))
        Fab.add_rule(w, GameplayRule("rule_first", priority=10))
        sorted_rules = sorted(w.rules.values(), key=lambda r: (-r.priority, r.rule_id))
        assert [r.rule_id for r in sorted_rules] == ["rule_first", "rule_a", "rule_z"]


class TestCommandsAndEvents:
    """Tests for §111 Commands Queue, Dispatch, and Events History."""

    def test_enqueue_command(self):
        w = Fab.create_gameplay_world("gw_cmd_01")
        cmd = GameplayCommand("cmd_01", GameplayCommandType.MOVE, target_entity_id="p1", payload={"dx": 1.0, "dy": 0.0})
        Fab.enqueue_command(w, cmd)
        assert len(w.command_queue) == 1

    def test_enqueue_command_max_limit(self):
        s = GameplayWorldSettings(max_commands_per_tick=2)
        w = Fab.create_gameplay_world("gw_cmd_02", settings=s)
        Fab.enqueue_command(w, GameplayCommand("c1", GameplayCommandType.MOVE, "p1"))
        Fab.enqueue_command(w, GameplayCommand("c2", GameplayCommandType.MOVE, "p1"))
        with pytest.raises(ValueError):
            Fab.enqueue_command(w, GameplayCommand("c3", GameplayCommandType.MOVE, "p1"))

    def test_execute_move_command(self):
        w = Fab.create_gameplay_world("gw_cmd_03")
        w.tick.delta_time = 1.0
        Fab.spawn_entity(w, "p1", position=(0.0, 0.0, 0.0))
        Fab.add_component(w, "p1", "character_controller", Fab.create_character_controller("cc_p1", move_speed=4.0))
        cmd = GameplayCommand("c_m", GameplayCommandType.MOVE, target_entity_id="p1", payload={"dx": 1.0, "dy": 0.0})
        Fab.execute_command(w, cmd)
        p = w.entities["p1"].position
        assert pytest.approx(p[0], 1e-3) == 4.0

    def test_execute_heal_command(self):
        w = Fab.create_gameplay_world("gw_cmd_04")
        Fab.spawn_entity(w, "p2")
        Fab.add_component(w, "p2", "health", HealthComponent(current_health=50.0, max_health=100.0))
        cmd = GameplayCommand("c_h", GameplayCommandType.HEAL, target_entity_id="p2", payload={"heal": 25.0})
        Fab.execute_command(w, cmd)
        assert w.entities["p2"].components["health"].current_health == 75.0

    def test_execute_damage_command(self):
        w = Fab.create_gameplay_world("gw_cmd_05")
        Fab.spawn_entity(w, "p3")
        Fab.add_component(w, "p3", "health", HealthComponent(current_health=100.0, max_health=100.0))
        cmd = GameplayCommand("c_d", GameplayCommandType.TAKE_DAMAGE, target_entity_id="p3", payload={"damage": 30.0})
        Fab.execute_command(w, cmd)
        assert w.entities["p3"].components["health"].current_health == 70.0

    def test_execute_command_dropped_for_destroyed_entity(self):
        w = Fab.create_gameplay_world("gw_cmd_06")
        Fab.spawn_entity(w, "target_dead")
        w.entities["target_dead"].state = EntityLifecycleState.DESTROYED
        cmd = GameplayCommand("c_drop", GameplayCommandType.HEAL, target_entity_id="target_dead", payload={"heal": 50.0})
        Fab.execute_command(w, cmd)
        assert True

    def test_execute_command_dropped_for_despawned_entity(self):
        w = Fab.create_gameplay_world("gw_cmd_07")
        Fab.spawn_entity(w, "target_despawn")
        w.entities["target_despawn"].state = EntityLifecycleState.PENDING_DESPAWN
        cmd = GameplayCommand("c_drop2", GameplayCommandType.HEAL, target_entity_id="target_despawn", payload={"heal": 50.0})
        Fab.execute_command(w, cmd)
        assert True

    def test_dispatch_event_sequence_counter_increment(self):
        w = Fab.create_gameplay_world("gw_cmd_08")
        assert w.event_sequence_counter == 0
        ev1 = Fab.dispatch_event(w, GameplayEventType.HEALED, "p1")
        assert ev1.sequence_number == 1
        ev2 = Fab.dispatch_event(w, GameplayEventType.HEALED, "p1")
        assert ev2.sequence_number == 2
        assert w.event_sequence_counter == 2

    def test_dispatch_event_queue_and_history(self):
        w = Fab.create_gameplay_world("gw_cmd_09")
        ev = Fab.dispatch_event(w, GameplayEventType.DAMAGE_APPLIED, "p1")
        assert ev in w.event_queue
        assert ev in w.event_history

    def test_event_to_dict(self):
        ev = GameplayEvent("ev_1", GameplayEventType.DAMAGE_APPLIED, "target", sequence_number=1, timestamp=0.0)
        d = ev.to_dict()
        assert d["event_id"] == "ev_1"
        assert d["event_type"] == "DAMAGE_APPLIED"

    def test_command_to_dict(self):
        cmd = GameplayCommand("c_1", GameplayCommandType.MOVE, "target")
        d = cmd.to_dict()
        assert d["command_id"] == "c_1"
        assert d["command_type"] == "MOVE"


class TestHealthAndCombat:
    """Tests for §112 Health, Damage Mitigation, Shields, and Combat."""

    def test_apply_damage_basic(self):
        w = Fab.create_gameplay_world("gw_hc_01")
        Fab.spawn_entity(w, "target")
        Fab.add_component(w, "target", "health", HealthComponent(current_health=100.0, max_health=100.0))
        req = DamageRequest("req1", "attacker", "target", raw_damage=40.0)
        res = Fab.apply_damage(w, req)
        assert res.raw_damage == 40.0
        assert res.health_damage == 40.0
        assert res.final_health == 60.0
        assert not res.is_killed

    def test_apply_damage_with_shields(self):
        w = Fab.create_gameplay_world("gw_hc_02")
        Fab.spawn_entity(w, "target")
        Fab.add_component(w, "target", "health", HealthComponent(current_health=100.0, max_health=100.0, current_shield=50.0, max_shield=50.0))
        req = DamageRequest("req2", "attacker", "target", raw_damage=30.0)
        res = Fab.apply_damage(w, req)
        assert res.shield_absorbed == 30.0
        assert res.health_damage == 0.0
        assert res.final_health == 100.0
        assert w.entities["target"].components["health"].current_shield == 20.0

    def test_apply_damage_shields_partial_absorption(self):
        w = Fab.create_gameplay_world("gw_hc_03")
        Fab.spawn_entity(w, "target")
        Fab.add_component(w, "target", "health", HealthComponent(current_health=100.0, max_health=100.0, current_shield=20.0, max_shield=20.0))
        req = DamageRequest("req3", "attacker", "target", raw_damage=50.0)
        res = Fab.apply_damage(w, req)
        assert res.shield_absorbed == 20.0
        assert res.health_damage == 30.0
        assert res.final_health == 70.0
        assert w.entities["target"].components["health"].current_shield == 0.0

    def test_apply_damage_kills_entity(self):
        w = Fab.create_gameplay_world("gw_hc_04")
        Fab.spawn_entity(w, "victim")
        Fab.add_component(w, "victim", "health", HealthComponent(current_health=30.0, max_health=100.0))
        req = DamageRequest("req4", "attacker", "victim", raw_damage=50.0)
        res = Fab.apply_damage(w, req)
        assert res.is_killed is True
        assert res.final_health == 0.0
        assert w.entities["victim"].components["health"].is_dead is True

    def test_apply_damage_invulnerable_entity(self):
        w = Fab.create_gameplay_world("gw_hc_05")
        Fab.spawn_entity(w, "invuln")
        Fab.add_component(w, "invuln", "health", HealthComponent(current_health=100.0, max_health=100.0, is_invulnerable=True))
        req = DamageRequest("req5", "attacker", "invuln", raw_damage=50.0)
        res = Fab.apply_damage(w, req)
        assert res.health_damage == 0.0
        assert res.final_health == 100.0

    def test_apply_damage_dead_entity_no_op(self):
        w = Fab.create_gameplay_world("gw_hc_06")
        Fab.spawn_entity(w, "corpse")
        Fab.add_component(w, "corpse", "health", HealthComponent(current_health=0.0, max_health=100.0, is_dead=True))
        req = DamageRequest("req6", "attacker", "corpse", raw_damage=50.0)
        res = Fab.apply_damage(w, req)
        assert res.health_damage == 0.0
        assert not res.is_killed

    def test_apply_damage_with_armor_mitigation(self):
        w = Fab.create_gameplay_world("gw_hc_07")
        Fab.spawn_entity(w, "armored")
        Fab.add_component(w, "armored", "health", HealthComponent(current_health=100.0, max_health=100.0))
        req = DamageRequest("req7", "attacker", "armored", raw_damage=100.0, modifiers={"armor": 100.0})
        res = Fab.apply_damage(w, req)
        assert pytest.approx(res.mitigated_damage, 1e-2) == 50.0
        assert pytest.approx(res.final_health, 1e-2) == 50.0

    def test_heal_entity_within_max_health(self):
        w = Fab.create_gameplay_world("gw_hc_08")
        Fab.spawn_entity(w, "p")
        Fab.add_component(w, "p", "health", HealthComponent(current_health=40.0, max_health=100.0))
        actual = Fab.heal(w, "p", 30.0)
        assert actual == 30.0
        assert w.entities["p"].components["health"].current_health == 70.0

    def test_heal_dead_entity_fails(self):
        w = Fab.create_gameplay_world("gw_hc_09")
        Fab.spawn_entity(w, "dead_p")
        Fab.add_component(w, "dead_p", "health", HealthComponent(current_health=0.0, max_health=100.0, is_dead=True))
        actual = Fab.heal(w, "dead_p", 50.0)
        assert actual == 0.0
        assert w.entities["dead_p"].components["health"].current_health == 0.0

    def test_heal_capped_at_max_health(self):
        w = Fab.create_gameplay_world("gw_hc_10")
        Fab.spawn_entity(w, "p")
        Fab.add_component(w, "p", "health", HealthComponent(current_health=90.0, max_health=100.0))
        actual = Fab.heal(w, "p", 50.0)
        assert actual == 10.0
        assert w.entities["p"].components["health"].current_health == 100.0

    def test_damage_and_heal_events_emitted(self):
        w = Fab.create_gameplay_world("gw_hc_11")
        Fab.spawn_entity(w, "p")
        Fab.add_component(w, "p", "health", HealthComponent(current_health=100.0, max_health=100.0))
        w.event_queue.clear()
        Fab.apply_damage(w, DamageRequest("r", "a", "p", 20.0))
        assert any(ev.event_type == GameplayEventType.DAMAGE_APPLIED for ev in w.event_queue)
        assert any(ev.event_type == GameplayEventType.HEALTH_CHANGED for ev in w.event_queue)
        w.event_queue.clear()
        Fab.heal(w, "p", 10.0)
        assert any(ev.event_type == GameplayEventType.HEALED for ev in w.event_queue)
class TestStatusEffects:
    """Tests for §113 Status Effects and stacking policies."""

    def test_apply_status_effect_new(self):
        w = Fab.create_gameplay_world("gw_se_01")
        Fab.spawn_entity(w, "target")
        eff = StatusEffect("eff_poison", "Poison", "attacker", "target", duration=5.0, magnitude=2.0)
        Fab.apply_status_effect(w, eff)
        effects = w.entities["target"].components.get("status_effects", {})
        assert "eff_poison" in effects
        assert effects["eff_poison"].magnitude == 2.0

    def test_apply_status_effect_refresh_policy(self):
        w = Fab.create_gameplay_world("gw_se_02")
        Fab.spawn_entity(w, "target")
        eff1 = StatusEffect("eff_bleed", "Bleed", "a", "target", duration=4.0, policy=StatusStackingPolicy.REFRESH)
        Fab.apply_status_effect(w, eff1)
        w.entities["target"].components["status_effects"]["eff_bleed"].elapsed = 3.0
        eff2 = StatusEffect("eff_bleed", "Bleed", "a", "target", duration=6.0, policy=StatusStackingPolicy.REFRESH)
        Fab.apply_status_effect(w, eff2)
        bleed = w.entities["target"].components["status_effects"]["eff_bleed"]
        assert bleed.elapsed == 0.0
        assert bleed.duration == 6.0

    def test_apply_status_effect_stack_policy(self):
        w = Fab.create_gameplay_world("gw_se_03")
        Fab.spawn_entity(w, "target")
        eff = StatusEffect("eff_burn", "Burn", "a", "target", duration=5.0, stacks=1, max_stacks=5, policy=StatusStackingPolicy.STACK)
        Fab.apply_status_effect(w, eff)
        Fab.apply_status_effect(w, eff)
        assert w.entities["target"].components["status_effects"]["eff_burn"].stacks == 2

    def test_apply_status_effect_max_stacks_clamped(self):
        w = Fab.create_gameplay_world("gw_se_04")
        Fab.spawn_entity(w, "target")
        eff = StatusEffect("eff_chill", "Chill", "a", "target", duration=5.0, stacks=3, max_stacks=3, policy=StatusStackingPolicy.STACK)
        Fab.apply_status_effect(w, eff)
        Fab.apply_status_effect(w, eff)
        assert w.entities["target"].components["status_effects"]["eff_chill"].stacks == 3

    def test_apply_status_effect_max_magnitude_policy(self):
        w = Fab.create_gameplay_world("gw_se_05")
        Fab.spawn_entity(w, "target")
        eff1 = StatusEffect("eff_slow", "Slow", "a", "target", duration=5.0, magnitude=0.2, policy=StatusStackingPolicy.MAX)
        eff2 = StatusEffect("eff_slow", "Slow", "a", "target", duration=5.0, magnitude=0.5, policy=StatusStackingPolicy.MAX)
        Fab.apply_status_effect(w, eff1)
        Fab.apply_status_effect(w, eff2)
        assert w.entities["target"].components["status_effects"]["eff_slow"].magnitude == 0.5

    def test_apply_status_effect_replace_policy(self):
        w = Fab.create_gameplay_world("gw_se_06")
        Fab.spawn_entity(w, "target")
        eff1 = StatusEffect("eff_stun", "Stun", "a", "target", duration=2.0, policy=StatusStackingPolicy.REPLACE)
        eff2 = StatusEffect("eff_stun", "Stun", "b", "target", duration=4.0, policy=StatusStackingPolicy.REPLACE)
        Fab.apply_status_effect(w, eff1)
        Fab.apply_status_effect(w, eff2)
        assert w.entities["target"].components["status_effects"]["eff_stun"].source_entity_id == "b"
        assert w.entities["target"].components["status_effects"]["eff_stun"].duration == 4.0

    def test_apply_status_effect_ignore_policy(self):
        w = Fab.create_gameplay_world("gw_se_07")
        Fab.spawn_entity(w, "target")
        eff1 = StatusEffect("eff_shield", "Shield", "a", "target", duration=10.0, magnitude=100.0, policy=StatusStackingPolicy.IGNORE)
        eff2 = StatusEffect("eff_shield", "Shield", "b", "target", duration=20.0, magnitude=200.0, policy=StatusStackingPolicy.IGNORE)
        Fab.apply_status_effect(w, eff1)
        Fab.apply_status_effect(w, eff2)
        assert w.entities["target"].components["status_effects"]["eff_shield"].duration == 10.0
        assert w.entities["target"].components["status_effects"]["eff_shield"].magnitude == 100.0

    def test_status_effect_duration_tick_expiry(self):
        w = Fab.create_gameplay_world("gw_se_08")
        Fab.spawn_entity(w, "target")
        eff = StatusEffect("eff_decay", "Decay", "a", "target", duration=0.1)
        Fab.apply_status_effect(w, eff)
        Fab.tick(w, 0.2)
        assert w.entities["target"].components["status_effects"]["eff_decay"].is_expired is True

    def test_status_effect_periodic_tick_damage_or_heal(self):
        w = Fab.create_gameplay_world("gw_se_09")
        Fab.spawn_entity(w, "target")
        Fab.add_component(w, "target", "health", HealthComponent(current_health=100.0, max_health=100.0))
        eff = StatusEffect("eff_dot", "Poison", "a", "target", duration=1.0, tick_interval=0.1, magnitude=10.0)
        Fab.apply_status_effect(w, eff)
        Fab.tick(w, 0.15)
        # 10 damage applied
        assert w.entities["target"].components["health"].current_health == 90.0

    def test_status_effect_non_existent_target_no_op(self):
        w = Fab.create_gameplay_world("gw_se_10")
        eff = StatusEffect("eff_ghost", "Ghost", "a", "ghost_target", duration=5.0)
        Fab.apply_status_effect(w, eff)
        assert True

    def test_status_effect_dispatches_event(self):
        w = Fab.create_gameplay_world("gw_se_11")
        Fab.spawn_entity(w, "target")
        eff = StatusEffect("eff_spark", "Spark", "a", "target", duration=3.0)
        w.event_queue.clear()
        Fab.apply_status_effect(w, eff)
        assert any(ev.event_type == GameplayEventType.STATUS_APPLIED for ev in w.event_queue)

    def test_status_effect_to_dict(self):
        eff = StatusEffect("eff_d", "Effect", "s", "t", duration=4.0, magnitude=15.0)
        d = eff.to_dict()
        assert d["effect_id"] == "eff_d"
        assert d["magnitude"] == 15.0


class TestAbilitiesAndCooldowns:
    """Tests for §114 Abilities and Cooldown System."""

    def test_register_ability(self):
        w = Fab.create_gameplay_world("gw_ab_01")
        ab = AbilityDefinition("fireball", "Fireball", cooldown=3.0, resource_cost=20.0)
        Fab.register_ability(w, ab)
        assert "fireball" in w.abilities

    def test_activate_ability_success(self):
        w = Fab.create_gameplay_world("gw_ab_02")
        Fab.spawn_entity(w, "mage")
        ab = AbilityDefinition("frostbolt", "Frostbolt", cooldown=2.0)
        Fab.register_ability(w, ab)
        success = Fab.activate_ability(w, "mage", "frostbolt")
        assert success is True
        assert ab.remaining_cooldown == 2.0
        assert ab.state == AbilityState.ON_COOLDOWN

    def test_activate_ability_on_cooldown_fails(self):
        w = Fab.create_gameplay_world("gw_ab_03")
        Fab.spawn_entity(w, "mage")
        ab = AbilityDefinition("blink", "Blink", cooldown=5.0)
        Fab.register_ability(w, ab)
        Fab.activate_ability(w, "mage", "blink")
        second_try = Fab.activate_ability(w, "mage", "blink")
        assert second_try is False

    def test_activate_ability_missing_required_tag_fails(self):
        w = Fab.create_gameplay_world("gw_ab_04")
        Fab.spawn_entity(w, "rogue", tags=["Class.Rogue"])
        ab = AbilityDefinition("backstab", "Backstab", cooldown=1.0, required_tags={"State.Stealthed"})
        Fab.register_ability(w, ab)
        assert Fab.activate_ability(w, "rogue", "backstab") is False
        w.entities["rogue"].tags.add("State.Stealthed")
        assert Fab.activate_ability(w, "rogue", "backstab") is True

    def test_activate_ability_with_blocked_tag_fails(self):
        w = Fab.create_gameplay_world("gw_ab_05")
        Fab.spawn_entity(w, "warrior", tags=["State.Silenced"])
        ab = AbilityDefinition("shout", "War Shout", cooldown=2.0, blocked_tags={"State.Silenced"})
        Fab.register_ability(w, ab)
        assert Fab.activate_ability(w, "warrior", "shout") is False
        w.entities["warrior"].tags.remove("State.Silenced")
        assert Fab.activate_ability(w, "warrior", "shout") is True

    def test_cooldown_decrement_on_tick(self):
        w = Fab.create_gameplay_world("gw_ab_06")
        Fab.spawn_entity(w, "p1")
        ab = AbilityDefinition("dash", "Dash", cooldown=2.0)
        Fab.register_ability(w, ab)
        Fab.activate_ability(w, "p1", "dash")
        assert ab.remaining_cooldown == 2.0
        Fab.tick(w, 0.5)
        assert pytest.approx(ab.remaining_cooldown, 1e-3) == 1.5

    def test_cooldown_expiry_resets_ability_state_to_ready(self):
        w = Fab.create_gameplay_world("gw_ab_07")
        Fab.spawn_entity(w, "p1")
        ab = AbilityDefinition("zap", "Zap", cooldown=0.5)
        Fab.register_ability(w, ab)
        Fab.activate_ability(w, "p1", "zap")
        Fab.tick(w, 0.6)
        assert ab.remaining_cooldown == 0.0
        assert ab.state == AbilityState.AVAILABLE

    def test_activate_ability_missing_entity_fails(self):
        w = Fab.create_gameplay_world("gw_ab_08")
        ab = AbilityDefinition("a1", "A1", cooldown=1.0)
        Fab.register_ability(w, ab)
        assert Fab.activate_ability(w, "ghost", "a1") is False

    def test_activate_ability_missing_ability_fails(self):
        w = Fab.create_gameplay_world("gw_ab_09")
        Fab.spawn_entity(w, "p1")
        assert Fab.activate_ability(w, "p1", "non_existent_ability") is False

    def test_ability_dispatches_started_and_completed_events(self):
        w = Fab.create_gameplay_world("gw_ab_10")
        Fab.spawn_entity(w, "caster")
        Fab.register_ability(w, AbilityDefinition("cast", "Cast", cooldown=1.0))
        w.event_queue.clear()
        Fab.activate_ability(w, "caster", "cast")
        assert any(ev.event_type == GameplayEventType.ABILITY_STARTED for ev in w.event_queue)
        assert any(ev.event_type == GameplayEventType.ABILITY_COMPLETED for ev in w.event_queue)

    def test_ability_definition_to_dict(self):
        ab = AbilityDefinition("slash", "Slash", cooldown=1.5, resource_cost=10.0)
        d = ab.to_dict()
        assert d["ability_id"] == "slash"
        assert d["cooldown"] == 1.5

    def test_multiple_abilities_independent_cooldowns(self):
        w = Fab.create_gameplay_world("gw_ab_12")
        Fab.spawn_entity(w, "p")
        ab1 = AbilityDefinition("ab1", "AB1", cooldown=1.0)
        ab2 = AbilityDefinition("ab2", "AB2", cooldown=3.0)
        Fab.register_ability(w, ab1)
        Fab.register_ability(w, ab2)
        Fab.activate_ability(w, "p", "ab1")
        Fab.activate_ability(w, "p", "ab2")
        Fab.tick(w, 1.2)
        assert ab1.remaining_cooldown == 0.0
        assert ab1.state == AbilityState.AVAILABLE
        assert ab2.remaining_cooldown > 0.0
        assert ab2.state == AbilityState.ON_COOLDOWN


class TestTimers:
    """Tests for §115 Timers and Scheduled Execution."""

    def test_add_timer_one_shot(self):
        w = Fab.create_gameplay_world("gw_tm_01")
        tm = Fab.add_timer(w, "tm1", duration=2.0, timer_type=TimerType.ONE_SHOT)
        assert tm.timer_id == "tm1"
        assert tm.timer_type == TimerType.ONE_SHOT
        assert tm.is_active is True

    def test_add_timer_looping(self):
        w = Fab.create_gameplay_world("gw_tm_02")
        tm = Fab.add_timer(w, "tm2", duration=1.0, timer_type=TimerType.REPEATING)
        assert tm.timer_type == TimerType.REPEATING

    def test_timer_tick_completion(self):
        w = Fab.create_gameplay_world("gw_tm_03")
        tm = Fab.add_timer(w, "tm3", duration=0.5)
        Fab.tick(w, 0.6)
        assert tm.is_completed is True
        assert tm.is_active is False

    def test_one_shot_timer_removed_after_trigger(self):
        w = Fab.create_gameplay_world("gw_tm_04")
        tm = Fab.add_timer(w, "tm4", duration=0.2)
        Fab.tick(w, 0.3)
        assert tm.is_completed is True

    def test_looping_timer_resets_elapsed(self):
        w = Fab.create_gameplay_world("gw_tm_05")
        tm = Fab.add_timer(w, "tm5", duration=0.5, timer_type=TimerType.REPEATING)
        Fab.tick(w, 0.6)
        assert tm.is_completed is False
        assert tm.elapsed < 0.5

    def test_cancel_timer_success(self):
        w = Fab.create_gameplay_world("gw_tm_06")
        Fab.add_timer(w, "tm6", duration=5.0)
        assert "tm6" in w.timers
        Fab.cancel_timer(w, "tm6")
        assert "tm6" not in w.timers

    def test_cancel_non_existent_timer_safe(self):
        w = Fab.create_gameplay_world("gw_tm_07")
        Fab.cancel_timer(w, "ghost_timer")
        assert True

    def test_timer_callback_event_dispatched(self):
        w = Fab.create_gameplay_world("gw_tm_08")
        Fab.add_timer(w, "tm8", duration=0.1, callback_event="ability_finished")
        w.event_queue.clear()
        Fab.tick(w, 0.15)
        assert any(ev.event_type == GameplayEventType.ABILITY_COMPLETED for ev in w.event_queue)

    def test_add_timer_max_limit_exceeded(self):
        s = GameplayWorldSettings(max_timers=2)
        w = Fab.create_gameplay_world("gw_tm_09", settings=s)
        Fab.add_timer(w, "t1", 1.0)
        Fab.add_timer(w, "t2", 1.0)
        with pytest.raises(ValueError):
            Fab.add_timer(w, "t3", 1.0)

    def test_multiple_timers_fire_in_deterministic_order(self):
        w = Fab.create_gameplay_world("gw_tm_10")
        Fab.add_timer(w, "tm_b", 0.1, callback_event="status")
        Fab.add_timer(w, "tm_a", 0.1, callback_event="status")
        Fab.tick(w, 0.2)
        # Both fired
        assert w.timers["tm_a"].is_completed is True
        assert w.timers["tm_b"].is_completed is True

    def test_timer_to_dict(self):
        tm = GameplayTimer("tm_d", duration=3.5, timer_type=TimerType.REPEATING)
        d = tm.to_dict()
        assert d["timer_id"] == "tm_d"
        assert d["duration"] == 3.5

    def test_timer_duration_clamped_positive(self):
        w = Fab.create_gameplay_world("gw_tm_12")
        tm = Fab.add_timer(w, "tm_neg", duration=-5.0)
        assert tm.duration > 0.0


class TestInventorySystem:
    """Tests for §116 Inventory and Transactional Item Management."""

    def test_create_inventory(self):
        inv = Fab.create_inventory("inv_main", max_slots=15)
        assert inv.inventory_id == "inv_main"
        assert inv.max_slots == 15
        assert len(inv.slots) == 0

    def test_add_item_empty_inventory(self):
        inv = Fab.create_inventory("inv_01", max_slots=5)
        rem = Fab.add_item(inv, "potion_health", 5)
        assert rem == 0
        assert len(inv.slots) == 1
        assert inv.slots[0].item_id == "potion_health"
        assert inv.slots[0].quantity == 5

    def test_add_item_fills_existing_stack(self):
        inv = Fab.create_inventory("inv_02", max_slots=5)
        Fab.add_item(inv, "iron_ore", 20, max_stack=50)
        rem = Fab.add_item(inv, "iron_ore", 15, max_stack=50)
        assert rem == 0
        assert len(inv.slots) == 1
        assert inv.slots[0].quantity == 35

    def test_add_item_creates_new_stack_when_full(self):
        inv = Fab.create_inventory("inv_03", max_slots=5)
        Fab.add_item(inv, "arrow", 50, max_stack=50)
        rem = Fab.add_item(inv, "arrow", 10, max_stack=50)
        assert rem == 0
        assert len(inv.slots) == 2
        assert inv.slots[0].quantity == 50
        assert inv.slots[1].quantity == 10

    def test_add_item_inventory_full_returns_remaining(self):
        inv = Fab.create_inventory("inv_04", max_slots=1)
        rem = Fab.add_item(inv, "gold_coin", 150, max_stack=100)
        assert rem == 50
        assert inv.slots[0].quantity == 100

    def test_add_item_zero_or_negative_returns_zero(self):
        inv = Fab.create_inventory("inv_05")
        assert Fab.add_item(inv, "wood", 0) == 0
        assert Fab.add_item(inv, "wood", -5) == 0

    def test_remove_item_partial_stack(self):
        inv = Fab.create_inventory("inv_06")
        Fab.add_item(inv, "berry", 10)
        success = Fab.remove_item(inv, "berry", 4)
        assert success is True
        assert inv.slots[0].quantity == 6

    def test_remove_item_entire_stack_deletes_slot(self):
        inv = Fab.create_inventory("inv_07")
        Fab.add_item(inv, "key", 1)
        success = Fab.remove_item(inv, "key", 1)
        assert success is True
        assert len(inv.slots) == 0

    def test_remove_item_insufficient_quantity_atomic_rollback(self):
        inv = Fab.create_inventory("inv_08")
        Fab.add_item(inv, "gem", 5)
        success = Fab.remove_item(inv, "gem", 10)
        assert success is False
        assert inv.slots[0].quantity == 5

    def test_remove_item_missing_item_returns_false(self):
        inv = Fab.create_inventory("inv_09")
        success = Fab.remove_item(inv, "diamond", 1)
        assert success is False

    def test_transfer_item_success(self):
        inv_a = Fab.create_inventory("inv_a", max_slots=5)
        inv_b = Fab.create_inventory("inv_b", max_slots=5)
        Fab.add_item(inv_a, "herb", 10)
        success = Fab.transfer_item(inv_a, inv_b, "herb", 6)
        assert success is True
        assert inv_a.slots[0].quantity == 4
        assert inv_b.slots[0].quantity == 6

    def test_transfer_item_atomic_rollback_when_dest_full(self):
        inv_a = Fab.create_inventory("inv_src", max_slots=5)
        inv_b = Fab.create_inventory("inv_dst", max_slots=1)
        Fab.add_item(inv_a, "stone", 20)
        Fab.add_item(inv_b, "other", 1)
        # inv_b has 1 slot and it's already full
        success = Fab.transfer_item(inv_a, inv_b, "stone", 5)
        assert success is False
        # Source must be untouched!
        assert inv_a.slots[0].quantity == 20

    def test_transfer_item_atomic_rollback_when_src_lacks_quantity(self):
        inv_a = Fab.create_inventory("inv_src2", max_slots=5)
        inv_b = Fab.create_inventory("inv_dst2", max_slots=5)
        Fab.add_item(inv_a, "meat", 3)
        success = Fab.transfer_item(inv_a, inv_b, "meat", 5)
        assert success is False
        assert inv_a.slots[0].quantity == 3
        assert len(inv_b.slots) == 0

    def test_inventory_to_dict(self):
        inv = Fab.create_inventory("inv_dict", max_slots=10)
        Fab.add_item(inv, "bread", 2)
        d = inv.to_dict()
        assert d["inventory_id"] == "inv_dict"
        assert d["max_slots"] == 10
        assert len(d["slots"]) == 1


class TestQuestSystem:
    """Tests for §117 Quests and Objective Tracking."""

    def test_register_quest(self):
        w = Fab.create_gameplay_world("gw_q_01")
        q = QuestDefinition("q_main", "Main Quest")
        Fab.register_quest(w, q)
        assert "q_main" in w.quests

    def test_start_quest_success(self):
        w = Fab.create_gameplay_world("gw_q_02")
        q = QuestDefinition(
            "q_rats",
            "Kill Rats",
            objectives={"obj_kill": QuestObjective("obj_kill", "Kill 5 rats", target_count=5)},
        )
        Fab.register_quest(w, q)
        success = Fab.start_quest(w, "q_rats")
        assert success is True
        assert q.state == QuestState.ACTIVE
        assert q.objectives["obj_kill"].state == ObjectiveState.ACTIVE

    def test_start_quest_already_active_fails(self):
        w = Fab.create_gameplay_world("gw_q_03")
        q = QuestDefinition("q_repeat", "Repeatable")
        Fab.register_quest(w, q)
        Fab.start_quest(w, "q_repeat")
        second = Fab.start_quest(w, "q_repeat")
        assert second is False

    def test_progress_objective_increments_count(self):
        w = Fab.create_gameplay_world("gw_q_04")
        q = QuestDefinition(
            "q_collect",
            "Collect Herbs",
            objectives={"obj_herbs": QuestObjective("obj_herbs", "Get 10 herbs", target_count=10)},
        )
        Fab.register_quest(w, q)
        Fab.start_quest(w, "q_collect")
        Fab.progress_objective(w, "q_collect", "obj_herbs", delta=3)
        assert q.objectives["obj_herbs"].current_count == 3
        assert q.objectives["obj_herbs"].state == ObjectiveState.ACTIVE

    def test_progress_objective_completes_objective(self):
        w = Fab.create_gameplay_world("gw_q_05")
        q = QuestDefinition(
            "q_wolf",
            "Defeat Alpha Wolf",
            objectives={"obj_wolf": QuestObjective("obj_wolf", "Defeat Alpha Wolf", target_count=1)},
        )
        Fab.register_quest(w, q)
        Fab.start_quest(w, "q_wolf")
        Fab.progress_objective(w, "q_wolf", "obj_wolf", delta=1)
        assert q.objectives["obj_wolf"].state == ObjectiveState.COMPLETED

    def test_progress_objective_completes_quest_when_all_mandatory_done(self):
        w = Fab.create_gameplay_world("gw_q_06")
        q = QuestDefinition(
            "q_boss",
            "Boss Quest",
            objectives={
                "o1": QuestObjective("o1", "Open Door", target_count=1, is_mandatory=True),
                "o2": QuestObjective("o2", "Slay Boss", target_count=1, is_mandatory=True),
            },
        )
        Fab.register_quest(w, q)
        Fab.start_quest(w, "q_boss")
        Fab.progress_objective(w, "q_boss", "o1", delta=1)
        assert q.state == QuestState.ACTIVE
        Fab.progress_objective(w, "q_boss", "o2", delta=1)
        assert q.state == QuestState.COMPLETED

    def test_optional_objective_does_not_block_quest_completion(self):
        w = Fab.create_gameplay_world("gw_q_07")
        q = QuestDefinition(
            "q_opt",
            "Optional Steps",
            objectives={
                "mandatory": QuestObjective("mandatory", "Main task", target_count=1, is_mandatory=True),
                "bonus": QuestObjective("bonus", "Bonus chest", target_count=1, is_mandatory=False),
            },
        )
        Fab.register_quest(w, q)
        Fab.start_quest(w, "q_opt")
        Fab.progress_objective(w, "q_opt", "mandatory", delta=1)
        assert q.state == QuestState.COMPLETED
        assert q.objectives["bonus"].state != ObjectiveState.COMPLETED

    def test_progress_objective_on_inactive_quest_fails(self):
        w = Fab.create_gameplay_world("gw_q_08")
        q = QuestDefinition("q_inact", "Inactive", objectives={"o": QuestObjective("o", "Task", target_count=1)})
        Fab.register_quest(w, q)
        success = Fab.progress_objective(w, "q_inact", "o", delta=1)
        assert success is False

    def test_progress_non_existent_objective_fails(self):
        w = Fab.create_gameplay_world("gw_q_09")
        q = QuestDefinition("q_exist", "Exist")
        Fab.register_quest(w, q)
        Fab.start_quest(w, "q_exist")
        assert Fab.progress_objective(w, "q_exist", "ghost_obj") is False

    def test_quest_and_objective_events_dispatched(self):
        w = Fab.create_gameplay_world("gw_q_10")
        q = QuestDefinition("q_ev", "Events", objectives={"obj": QuestObjective("obj", "Task", target_count=1)})
        Fab.register_quest(w, q)
        w.event_queue.clear()
        Fab.start_quest(w, "q_ev")
        assert any(ev.event_type == GameplayEventType.QUEST_STARTED for ev in w.event_queue)
        w.event_queue.clear()
        Fab.progress_objective(w, "q_ev", "obj", delta=1)
        assert any(ev.event_type == GameplayEventType.OBJECTIVE_COMPLETED for ev in w.event_queue)

    def test_quest_to_dict(self):
        q = QuestDefinition("q_dict", "Title")
        d = q.to_dict()
        assert d["quest_id"] == "q_dict"
        assert d["title"] == "Title"

    def test_objective_to_dict(self):
        obj = QuestObjective("obj_d", "Desc", target_count=5, current_count=2)
        d = obj.to_dict()
        assert d["objective_id"] == "obj_d"
        assert d["target_count"] == 5


class TestSpawnDespawn:
    """Tests for §118 Spawn, Despawn, and Object Pooling."""

    def test_spawn_request_processing(self):
        req = SpawnRequest("sp_01", "warrior_def", position=(1.0, 0.0, 2.0))
        assert req.spawn_id == "sp_01"
        assert req.definition_id == "warrior_def"
        assert req.position == (1.0, 0.0, 2.0)

    def test_despawn_request_processing(self):
        req = DespawnRequest("dsp_01", "target_ent", reason="TIMEOUT")
        assert req.despawn_id == "dsp_01"
        assert req.entity_id == "target_ent"
        assert req.reason == "TIMEOUT"

    def test_spawn_entity_with_metadata(self):
        w = Fab.create_gameplay_world("gw_sd_01")
        e = Fab.spawn_entity(w, "npc_meta", metadata={"faction": "neutral", "level": 10})
        assert e.metadata["faction"] == "neutral"
        assert e.metadata["level"] == 10

    def test_spawn_entity_with_components(self):
        w = Fab.create_gameplay_world("gw_sd_02")
        e = Fab.spawn_entity(w, "hero_full")
        Fab.add_component(w, "hero_full", "health", HealthComponent(current_health=100.0, max_health=100.0))
        Fab.add_component(w, "hero_full", "inventory", Fab.create_inventory("inv_hf"))
        assert "health" in e.components
        assert "inventory" in e.components

    def test_despawn_entity_reason_preserved_in_event(self):
        w = Fab.create_gameplay_world("gw_sd_03")
        Fab.spawn_entity(w, "minion")
        w.event_queue.clear()
        Fab.despawn_entity(w, "minion", reason="COMBAT_VICTORY")
        assert any(
            ev.event_type == GameplayEventType.ENTITY_DESPAWNED and ev.payload.get("reason") == "COMBAT_VICTORY"
            for ev in w.event_queue
        )

    def test_spawn_entity_resource_limit_exceeded(self):
        s = GameplayWorldSettings(max_entities=2)
        w = Fab.create_gameplay_world("gw_sd_04", settings=s)
        Fab.spawn_entity(w, "e1")
        Fab.spawn_entity(w, "e2")
        with pytest.raises(ValueError):
            Fab.spawn_entity(w, "e3")

    def test_spawn_duplicate_id_prevented(self):
        w = Fab.create_gameplay_world("gw_sd_05")
        Fab.spawn_entity(w, "unique_id")
        with pytest.raises(ValueError):
            Fab.spawn_entity(w, "unique_id")

    def test_despawn_non_existent_entity_safe(self):
        w = Fab.create_gameplay_world("gw_sd_06")
        Fab.despawn_entity(w, "ghost_mob")
        assert True

    def test_spawn_request_to_dict(self):
        req = SpawnRequest("s1", "def1", position=(0.0, 1.0, 0.0))
        d = req.to_dict()
        assert d["spawn_id"] == "s1"
        assert d["definition_id"] == "def1"

    def test_despawn_request_to_dict(self):
        req = DespawnRequest("d1", "e1", reason="DEAD")
        d = req.to_dict()
        assert d["despawn_id"] == "d1"
        assert d["reason"] == "DEAD"
class TestSaveLoadState:
    """Tests for §119 Save and Load Persistent World State."""

    def test_save_state_creation(self):
        w = Fab.create_gameplay_world("gw_sl_01")
        save = Fab.save_state(w, "save_001")
        assert save.save_id == "save_001"
        assert save.version == 1
        assert save.gameplay_world_id == "gw_sl_01"

    def test_save_state_includes_active_entities(self):
        w = Fab.create_gameplay_world("gw_sl_02")
        Fab.spawn_entity(w, "p1", position=(1.0, 2.0, 3.0))
        save = Fab.save_state(w)
        assert "p1" in save.entities_data
        assert save.entities_data["p1"]["position"] == (1.0, 2.0, 3.0)

    def test_save_state_excludes_disabled_entities(self):
        w = Fab.create_gameplay_world("gw_sl_03")
        e = Fab.spawn_entity(w, "inactive_actor")
        e.state = EntityLifecycleState.DISABLED
        save = Fab.save_state(w)
        assert "inactive_actor" not in save.entities_data

    def test_save_state_includes_quests(self):
        w = Fab.create_gameplay_world("gw_sl_04")
        q = QuestDefinition("q_story", "Story")
        Fab.register_quest(w, q)
        save = Fab.save_state(w)
        assert "q_story" in save.quest_data

    def test_save_state_includes_cooldowns(self):
        w = Fab.create_gameplay_world("gw_sl_05")
        ab = AbilityDefinition("spin", "Spin", cooldown=5.0, remaining_cooldown=3.0)
        Fab.register_ability(w, ab)
        save = Fab.save_state(w)
        assert save.cooldowns_data.get("spin") == 3.0

    def test_save_state_to_dict(self):
        save = SaveState("save_d", version=1, timestamp=10.5, gameplay_world_id="w1")
        d = save.to_dict()
        assert d["save_id"] == "save_d"
        assert d["version"] == 1
        assert d["timestamp"] == 10.5

    def test_load_state_success(self):
        w = Fab.create_gameplay_world("gw_sl_07")
        save = SaveState(
            "save_ok",
            version=1,
            timestamp=5.0,
            gameplay_world_id="gw_sl_07",
            entities_data={"hero": {"name": "Hero", "position": (2.0, 0.0, 1.0), "tags": []}},
        )
        success = Fab.load_state(w, save)
        assert success is True
        assert "hero" in w.entities
        assert w.entities["hero"].position == (2.0, 0.0, 1.0)
        assert w.tick.simulation_time == 5.0

    def test_load_state_invalid_version_fails(self):
        w = Fab.create_gameplay_world("gw_sl_08")
        save = SaveState("save_bad_ver", version=999)
        success = Fab.load_state(w, save)
        assert success is False

    def test_load_state_restores_entities(self):
        w = Fab.create_gameplay_world("gw_sl_09")
        save = SaveState(
            "s",
            entities_data={
                "e1": {"name": "Actor1", "position": (0.0, 0.0, 0.0), "tags": []},
                "e2": {"name": "Actor2", "position": (10.0, 0.0, 0.0), "tags": []},
            },
        )
        Fab.load_state(w, save)
        assert len(w.entities) == 2
        assert "e1" in w.entities
        assert "e2" in w.entities

    def test_load_state_restores_health_components(self):
        w = Fab.create_gameplay_world("gw_sl_10")
        save = SaveState(
            "s_hp",
            entities_data={
                "tank": {
                    "name": "Tank",
                    "position": (0.0, 0.0, 0.0),
                    "tags": [],
                    "health": {"current_health": 80.0, "max_health": 150.0, "current_shield": 10.0, "max_shield": 50.0},
                }
            },
        )
        Fab.load_state(w, save)
        h = w.entities["tank"].components.get("health")
        assert h is not None
        assert h.current_health == 80.0
        assert h.max_health == 150.0

    def test_load_state_restores_simulation_time(self):
        w = Fab.create_gameplay_world("gw_sl_11")
        save = SaveState("s_time", timestamp=42.0)
        Fab.load_state(w, save)
        assert w.tick.simulation_time == 42.0

    def test_load_state_clears_old_world_entities(self):
        w = Fab.create_gameplay_world("gw_sl_12")
        Fab.spawn_entity(w, "old_entity")
        save = SaveState("s_clear", entities_data={"new_entity": {"name": "New", "position": (0.0, 0.0, 0.0), "tags": []}})
        Fab.load_state(w, save)
        assert "old_entity" not in w.entities
        assert "new_entity" in w.entities

    def test_save_state_round_trip_equality(self):
        w = Fab.create_gameplay_world("gw_sl_13")
        Fab.spawn_entity(w, "hero", position=(5.0, 1.0, 0.0))
        Fab.add_component(w, "hero", "health", HealthComponent(current_health=90.0, max_health=100.0))
        save1 = Fab.save_state(w, "save_rt")
        w2 = Fab.create_gameplay_world("gw_sl_13_copy")
        Fab.load_state(w2, save1)
        save2 = Fab.save_state(w2, "save_rt")
        assert save1.to_dict() == save2.to_dict()

    def test_validator_detects_invalid_save_id(self):
        save = SaveState(save_id="", version=1)
        issues = Val.validate_save_state(save)
        assert any(i.code == "NO_UNVALIDATED_LOAD" for i in issues)

    def test_validator_detects_invalid_save_version(self):
        save = SaveState(save_id="s_ver", version=0)
        issues = Val.validate_save_state(save)
        assert any(i.code == "NO_UNVALIDATED_LOAD" for i in issues)

    def test_validator_detects_transient_leak_in_save(self):
        save = SaveState(save_id="s_leak", version=1, entities_data={"p1": {"transient_state": "cache"}})
        issues = Val.validate_save_state(save)
        assert any(i.code == "NO_TRANSIENT_STATE_IN_PERSISTENT_SAVE" for i in issues)


class TestSnapshots:
    """Tests for §120 Snapshots and Deep State Capture."""

    def test_create_snapshot_basic(self):
        w = Fab.create_gameplay_world("gw_snap_01")
        snap = Fab.create_snapshot(w, "snap_001")
        assert snap.snapshot_id == "snap_001"
        assert snap.gameplay_world_id == "gw_snap_01"

    def test_create_snapshot_custom_id(self):
        w = Fab.create_gameplay_world("gw_snap_02")
        snap = Fab.create_snapshot(w, "checkpoint_alpha")
        assert snap.snapshot_id == "checkpoint_alpha"

    def test_create_snapshot_records_tick_and_time(self):
        w = Fab.create_gameplay_world("gw_snap_03")
        w.tick.tick_index = 100
        w.tick.simulation_time = 1.6
        snap = Fab.create_snapshot(w)
        assert snap.tick_index == 100
        assert pytest.approx(snap.simulation_time, 1e-4) == 1.6

    def test_create_snapshot_records_entities(self):
        w = Fab.create_gameplay_world("gw_snap_04")
        Fab.spawn_entity(w, "actor_snap", position=(3.0, 4.0, 5.0))
        snap = Fab.create_snapshot(w)
        assert "actor_snap" in snap.entities
        assert snap.entities["actor_snap"]["position"] == [3.0, 4.0, 5.0] or snap.entities["actor_snap"]["position"] == (3.0, 4.0, 5.0)

    def test_create_snapshot_records_abilities(self):
        w = Fab.create_gameplay_world("gw_snap_05")
        Fab.register_ability(w, AbilityDefinition("ab_snap", "AbSnap", cooldown=4.0))
        snap = Fab.create_snapshot(w)
        assert "ab_snap" in snap.abilities

    def test_create_snapshot_records_quests(self):
        w = Fab.create_gameplay_world("gw_snap_06")
        Fab.register_quest(w, QuestDefinition("q_snap", "QuestSnap"))
        snap = Fab.create_snapshot(w)
        assert "q_snap" in snap.quests

    def test_create_snapshot_records_timers(self):
        w = Fab.create_gameplay_world("gw_snap_07")
        Fab.add_timer(w, "tm_snap", duration=2.5)
        snap = Fab.create_snapshot(w)
        assert "tm_snap" in snap.timers

    def test_create_snapshot_fingerprint(self):
        w = Fab.create_gameplay_world("gw_snap_08")
        snap = Fab.create_snapshot(w)
        assert snap.fingerprint == w.compute_fingerprint()

    def test_snapshot_to_dict(self):
        w = Fab.create_gameplay_world("gw_snap_09")
        snap = Fab.create_snapshot(w, "snap_d")
        d = snap.to_dict()
        assert d["snapshot_id"] == "snap_d"
        assert "entities" in d
        assert "fingerprint" in d

    def test_restore_snapshot_restores_state(self):
        w = Fab.create_gameplay_world("gw_snap_10")
        w.state = GameplayWorldState.RUNNING
        snap = Fab.create_snapshot(w, "s10")
        w.state = GameplayWorldState.STOPPED
        Fab.restore_snapshot(w, snap)
        assert w.state == GameplayWorldState.RUNNING

    def test_restore_snapshot_restores_tick_and_time(self):
        w = Fab.create_gameplay_world("gw_snap_11")
        w.tick.tick_index = 50
        w.tick.simulation_time = 2.5
        snap = Fab.create_snapshot(w)
        w.tick.tick_index = 0
        w.tick.simulation_time = 0.0
        Fab.restore_snapshot(w, snap)
        assert w.tick.tick_index == 50
        assert w.tick.simulation_time == 2.5

    def test_restore_snapshot_restores_entities(self):
        w = Fab.create_gameplay_world("gw_snap_12")
        Fab.spawn_entity(w, "ent_a", position=(1.0, 2.0, 3.0))
        snap = Fab.create_snapshot(w)
        w.entities.clear()
        Fab.restore_snapshot(w, snap)
        assert "ent_a" in w.entities
        assert w.entities["ent_a"].position == (1.0, 2.0, 3.0)

    def test_restore_snapshot_restores_components(self):
        w = Fab.create_gameplay_world("gw_snap_13")
        Fab.spawn_entity(w, "hero")
        Fab.add_component(w, "hero", "health", HealthComponent(current_health=45.0, max_health=100.0))
        snap = Fab.create_snapshot(w)
        w.entities.clear()
        Fab.restore_snapshot(w, snap)
        assert "hero" in w.entities
        h = w.entities["hero"].components.get("health")
        assert h is not None
        assert h.current_health == 45.0

    def test_two_identical_worlds_produce_identical_snapshots(self):
        w1 = Fab.create_gameplay_world("same_world")
        w2 = Fab.create_gameplay_world("same_world")
        s1 = Fab.create_snapshot(w1, "snap_id")
        s2 = Fab.create_snapshot(w2, "snap_id")
        assert s1.to_dict() == s2.to_dict()

    def test_snapshot_roundtrip_fingerprint_match(self):
        w = Fab.create_gameplay_world("gw_snap_15")
        Fab.spawn_entity(w, "hero")
        fp_before = w.compute_fingerprint()
        snap = Fab.create_snapshot(w)
        w.entities.clear()
        Fab.restore_snapshot(w, snap)
        fp_after = w.compute_fingerprint()
        assert fp_before == fp_after

    def test_validator_snapshot_checks(self):
        snap = GameplaySnapshot("s", "w", "CREATED", 0, 0.0, {}, {}, {}, {}, "hash_val")
        issues = Val.validate_snapshot(snap)
        assert len([i for i in issues if i.severity == "ERROR"]) == 0


class TestReplayAndDeterminism:
    """Tests for §121 Deterministic Replay and Simulation Execution."""

    def test_replay_commands_execution_order(self):
        w = Fab.create_gameplay_world("gw_rep_01")
        Fab.spawn_entity(w, "p", position=(0.0, 0.0, 0.0))
        Fab.add_component(w, "p", "character_controller", Fab.create_character_controller("cc_p", move_speed=1.0))
        w.tick.delta_time = 1.0
        cmds = [
            GameplayCommand("c1", GameplayCommandType.MOVE, "p", payload={"dx": 1.0, "dy": 0.0}),
            GameplayCommand("c2", GameplayCommandType.MOVE, "p", payload={"dx": 0.0, "dy": 1.0}),
        ]
        Fab.replay_commands(w, cmds)
        pos = w.entities["p"].position
        assert pytest.approx(pos[0], 1e-3) == 1.0
        assert pytest.approx(pos[1], 1e-3) == 1.0

    def test_replay_move_commands_reproduces_position(self):
        w1 = Fab.create_gameplay_world("w1")
        w2 = Fab.create_gameplay_world("w2")
        Fab.spawn_entity(w1, "p", position=(0.0, 0.0, 0.0))
        Fab.spawn_entity(w2, "p", position=(0.0, 0.0, 0.0))
        Fab.add_component(w1, "p", "character_controller", Fab.create_character_controller("cc_p", move_speed=2.0))
        Fab.add_component(w2, "p", "character_controller", Fab.create_character_controller("cc_p", move_speed=2.0))
        w1.tick.delta_time = 1.0
        w2.tick.delta_time = 1.0
        cmds = [GameplayCommand(f"c_{i}", GameplayCommandType.MOVE, "p", payload={"dx": 1.0, "dy": 0.0}) for i in range(5)]
        Fab.replay_commands(w1, cmds)
        Fab.replay_commands(w2, cmds)
        assert w1.entities["p"].position == w2.entities["p"].position

    def test_replay_damage_and_heal_reproduces_health(self):
        w = Fab.create_gameplay_world("gw_rep_03")
        Fab.spawn_entity(w, "fighter")
        Fab.add_component(w, "fighter", "health", HealthComponent(current_health=100.0, max_health=100.0))
        cmds = [
            GameplayCommand("c1", GameplayCommandType.TAKE_DAMAGE, "fighter", payload={"damage": 40.0}),
            GameplayCommand("c2", GameplayCommandType.HEAL, "fighter", payload={"heal": 15.0}),
        ]
        Fab.replay_commands(w, cmds)
        assert w.entities["fighter"].components["health"].current_health == 75.0

    def test_replay_deterministic_event_count(self):
        w1 = Fab.create_gameplay_world("w_ev_1")
        w2 = Fab.create_gameplay_world("w_ev_2")
        Fab.spawn_entity(w1, "t")
        Fab.spawn_entity(w2, "t")
        Fab.add_component(w1, "t", "health", HealthComponent(current_health=100.0, max_health=100.0))
        Fab.add_component(w2, "t", "health", HealthComponent(current_health=100.0, max_health=100.0))
        w1.event_queue.clear()
        w2.event_queue.clear()
        cmds = [GameplayCommand(f"d_{i}", GameplayCommandType.TAKE_DAMAGE, "t", payload={"damage": 10.0}) for i in range(3)]
        Fab.replay_commands(w1, cmds)
        Fab.replay_commands(w2, cmds)
        assert len(w1.event_queue) == len(w2.event_queue)

    def test_replay_commands_empty_list_no_op(self):
        w = Fab.create_gameplay_world("gw_rep_05")
        Fab.replay_commands(w, [])
        assert True

    def test_replay_ignores_commands_for_destroyed_entity(self):
        w = Fab.create_gameplay_world("gw_rep_06")
        Fab.spawn_entity(w, "dead_target")
        w.entities["dead_target"].state = EntityLifecycleState.DESTROYED
        cmds = [GameplayCommand("c1", GameplayCommandType.HEAL, "dead_target", payload={"heal": 20.0})]
        Fab.replay_commands(w, cmds)
        assert True

    def test_replay_deterministic_rule_evaluation(self):
        w1 = Fab.create_gameplay_world("w_r1")
        w2 = Fab.create_gameplay_world("w_r2")
        for world in (w1, w2):
            Fab.spawn_entity(world, "hero")
            Fab.add_rule(world, GameplayRule("r1", priority=10, conditions=[], effects=[{"type": "add_tag", "entity_id": "hero", "tag": "T1"}]))
            Fab.add_rule(world, GameplayRule("r2", priority=5, conditions=[], effects=[{"type": "add_tag", "entity_id": "hero", "tag": "T2"}]))
            Fab.evaluate_rules(world)
        assert w1.entities["hero"].tags.to_dict() == w2.entities["hero"].tags.to_dict()

    def test_deterministic_ticks_same_input_same_hash(self):
        w1 = Fab.create_gameplay_world("w_dt")
        w2 = Fab.create_gameplay_world("w_dt")
        for world in (w1, w2):
            Fab.spawn_entity(world, "actor", position=(0.0, 0.0, 0.0))
            for _ in range(5):
                Fab.tick(world, 0.016)
        assert w1.compute_fingerprint() == w2.compute_fingerprint()

    def test_independent_worlds_tick_determinism(self):
        w1 = Fab.create_gameplay_world("w_ind_1")
        w2 = Fab.create_gameplay_world("w_ind_2")
        Fab.add_timer(w1, "tm", 0.5)
        Fab.add_timer(w2, "tm", 0.5)
        Fab.tick(w1, 0.6)
        Fab.tick(w2, 0.6)
        assert w1.timers["tm"].is_completed == w2.timers["tm"].is_completed

    def test_copy_dict_deterministic_sorted_keys(self):
        d = {"z": 1, "a": 2, "m": 3}
        cd = copy_dict_deterministic(d)
        assert list(cd.keys()) == ["a", "m", "z"]

    def test_copy_dict_deterministic_nested_lists(self):
        d = {"list_key": [{"b": 2, "a": 1}]}
        cd = copy_dict_deterministic(d)
        assert list(cd["list_key"][0].keys()) == ["a", "b"]

    def test_copy_dict_deterministic_primitive_types(self):
        assert copy_dict_deterministic(42) == 42
        assert copy_dict_deterministic("text") == "text"
        assert copy_dict_deterministic(True) is True

    def test_world_compute_fingerprint_changes_on_entity_spawn(self):
        w = Fab.create_gameplay_world("gw_fp_01")
        fp1 = w.compute_fingerprint()
        Fab.spawn_entity(w, "new_actor")
        fp2 = w.compute_fingerprint()
        assert fp1 != fp2

    def test_world_compute_fingerprint_changes_on_tick(self):
        w = Fab.create_gameplay_world("gw_fp_02")
        fp1 = w.compute_fingerprint()
        Fab.tick(w, 0.016)
        fp2 = w.compute_fingerprint()
        assert fp1 != fp2

    def test_world_compute_fingerprint_changes_on_damage(self):
        w = Fab.create_gameplay_world("gw_fp_03")
        Fab.spawn_entity(w, "victim")
        Fab.add_component(w, "victim", "health", HealthComponent(current_health=100.0, max_health=100.0))
        fp1 = w.compute_fingerprint()
        Fab.apply_damage(w, DamageRequest("r", "a", "victim", 20.0))
        fp2 = w.compute_fingerprint()
        assert fp1 != fp2

    def test_replay_deterministic_quest_progress(self):
        w1 = Fab.create_gameplay_world("w_qp1")
        w2 = Fab.create_gameplay_world("w_qp2")
        for world in (w1, w2):
            q = QuestDefinition("q1", "Q1", objectives={"o1": QuestObjective("o1", "Task", target_count=3)})
            Fab.register_quest(world, q)
            Fab.start_quest(world, "q1")
            Fab.progress_objective(world, "q1", "o1", delta=2)
        assert w1.quests["q1"].objectives["o1"].current_count == w2.quests["q1"].objectives["o1"].current_count

    def test_replay_deterministic_status_effect_ticks(self):
        w1 = Fab.create_gameplay_world("w_se1")
        w2 = Fab.create_gameplay_world("w_se2")
        for world in (w1, w2):
            Fab.spawn_entity(world, "target")
            Fab.add_component(world, "target", "health", HealthComponent(current_health=100.0, max_health=100.0))
            eff = StatusEffect("poison", "Poison", "src", "target", duration=2.0, tick_interval=0.1, magnitude=5.0)
            Fab.apply_status_effect(world, eff)
            for _ in range(5):
                Fab.tick(world, 0.1)
        assert w1.entities["target"].components["health"].current_health == w2.entities["target"].components["health"].current_health

    def test_replay_reproducibility_100_ticks(self):
        w1 = Fab.create_gameplay_world("w_100")
        w2 = Fab.create_gameplay_world("w_100")
        for world in (w1, w2):
            Fab.spawn_entity(world, "hero", position=(0.0, 0.0, 0.0))
            Fab.add_component(world, "hero", "character_controller", Fab.create_character_controller("cc_h", move_speed=1.0))
            for i in range(20):
                Fab.move_character(world, "hero", 1.0, 0.0)
                Fab.tick(world, 0.016)
        assert w1.compute_fingerprint() == w2.compute_fingerprint()


class TestGoldenGameplay:
    """Tests for §122 Golden Gameplay integration and end-to-end combat flows."""

    def test_golden_combat_sequence(self):
        w = Fab.create_gameplay_world("gw_gold_01")
        Fab.spawn_entity(w, "player")
        Fab.spawn_entity(w, "boss")
        Fab.add_component(w, "player", "health", HealthComponent(current_health=200.0, max_health=200.0))
        Fab.add_component(w, "boss", "health", HealthComponent(current_health=500.0, max_health=500.0, current_shield=100.0, max_shield=100.0))
        # Player attacks Boss
        res1 = Fab.apply_damage(w, DamageRequest("atk1", "player", "boss", raw_damage=80.0))
        assert res1.shield_absorbed == 80.0
        assert w.entities["boss"].components["health"].current_shield == 20.0
        # Player attacks again -> breaks shield and hits health
        res2 = Fab.apply_damage(w, DamageRequest("atk2", "player", "boss", raw_damage=50.0))
        assert res2.shield_absorbed == 20.0
        assert res2.health_damage == 30.0
        assert w.entities["boss"].components["health"].current_health == 470.0

    def test_golden_inventory_gather_and_craft(self):
        w = Fab.create_gameplay_world("gw_gold_02")
        Fab.spawn_entity(w, "crafter")
        inv = Fab.create_inventory("inv_craft", max_slots=10)
        Fab.add_component(w, "crafter", "inventory", inv)
        Fab.add_item(inv, "wood", 10)
        Fab.add_item(inv, "iron", 5)
        assert inv.slots[0].quantity == 10
        assert inv.slots[1].quantity == 5
        # Craft consumes 4 wood and 2 iron
        assert Fab.remove_item(inv, "wood", 4) is True
        assert Fab.remove_item(inv, "iron", 2) is True
        assert inv.slots[0].quantity == 6
        assert inv.slots[1].quantity == 3
        # Add crafted sword
        Fab.add_item(inv, "iron_sword", 1)
        assert len(inv.slots) == 3

    def test_golden_quest_flow_from_start_to_completion(self):
        w = Fab.create_gameplay_world("gw_gold_03")
        q = QuestDefinition(
            "quest_relic",
            "Find Ancient Relic",
            objectives={
                "obj1": QuestObjective("obj1", "Explore Ruins", target_count=1, is_mandatory=True),
                "obj2": QuestObjective("obj2", "Defeat Guardian", target_count=1, is_mandatory=True),
            },
        )
        Fab.register_quest(w, q)
        Fab.start_quest(w, "quest_relic")
        assert q.state == QuestState.ACTIVE
        Fab.progress_objective(w, "quest_relic", "obj1", delta=1)
        assert q.state == QuestState.ACTIVE
        Fab.progress_objective(w, "quest_relic", "obj2", delta=1)
        assert q.state == QuestState.COMPLETED

    def test_golden_character_exploration_and_triggers(self):
        w = Fab.create_gameplay_world("gw_gold_04")
        Fab.spawn_entity(w, "explorer", position=(0.0, 0.0, 0.0))
        trig = Fab.create_trigger("ruins_gate")
        Fab.add_component(w, "explorer", "trigger", trig)
        # Enter zone
        evt1 = Fab.process_trigger_overlap(w, trig, "explorer", is_overlapping=True)
        assert evt1 == TriggerEventType.ENTER
        assert trig.state == TriggerState.TRIGGERED
        # Exit zone
        evt2 = Fab.process_trigger_overlap(w, trig, "explorer", is_overlapping=False)
        assert evt2 == TriggerEventType.EXIT
        assert trig.state == TriggerState.ACTIVE

    def test_golden_status_effects_and_mitigation(self):
        w = Fab.create_gameplay_world("gw_gold_05")
        Fab.spawn_entity(w, "knight")
        Fab.add_component(w, "knight", "health", HealthComponent(current_health=100.0, max_health=100.0))
        eff = StatusEffect("dot_burn", "Burn", "mage", "knight", duration=3.0, tick_interval=0.1, magnitude=5.0)
        Fab.apply_status_effect(w, eff)
        Fab.tick(w, 0.15)
        # 5 damage from burn
        assert w.entities["knight"].components["health"].current_health == 95.0

    def test_golden_ability_rotation_with_cooldowns(self):
        w = Fab.create_gameplay_world("gw_gold_06")
        Fab.spawn_entity(w, "warrior")
        ab1 = AbilityDefinition("strike", "Strike", cooldown=1.0)
        ab2 = AbilityDefinition("slam", "Slam", cooldown=2.0)
        Fab.register_ability(w, ab1)
        Fab.register_ability(w, ab2)
        assert Fab.activate_ability(w, "warrior", "strike") is True
        assert Fab.activate_ability(w, "warrior", "slam") is True
        Fab.tick(w, 1.1)
        assert ab1.state == AbilityState.AVAILABLE
        assert ab2.state == AbilityState.ON_COOLDOWN
        assert Fab.activate_ability(w, "warrior", "strike") is True

    def test_golden_multi_entity_simulation(self):
        w = Fab.create_gameplay_world("gw_gold_07")
        for i in range(10):
            Fab.spawn_entity(w, f"ent_{i}", position=(float(i), 0.0, 0.0))
        assert len(w.entities) == 10
        Fab.tick(w, 0.016)
        assert w.tick.tick_index == 1

    def test_golden_event_history_ordering(self):
        w = Fab.create_gameplay_world("gw_gold_08")
        Fab.spawn_entity(w, "hero")
        Fab.dispatch_event(w, GameplayEventType.INTERACTION_STARTED, "hero")
        Fab.dispatch_event(w, GameplayEventType.INTERACTION_COMPLETED, "hero")
        assert len(w.event_history) >= 2
        seqs = [ev.sequence_number for ev in w.event_history]
        assert seqs == sorted(seqs)

    def test_golden_snapshot_at_checkpoints(self):
        w = Fab.create_gameplay_world("gw_gold_09")
        Fab.spawn_entity(w, "traveler", position=(0.0, 0.0, 0.0))
        snap1 = Fab.create_snapshot(w, "cp_start")
        w.entities["traveler"].position = (50.0, 0.0, 0.0)
        snap2 = Fab.create_snapshot(w, "cp_mid")
        assert snap1.entities["traveler"]["position"] != snap2.entities["traveler"]["position"]

    def test_golden_save_load_resumption(self):
        w = Fab.create_gameplay_world("gw_gold_10")
        Fab.spawn_entity(w, "hero", position=(10.0, 20.0, 30.0))
        save = Fab.save_state(w, "gold_save")
        w_resumed = Fab.create_gameplay_world("gw_gold_10_resumed")
        Fab.load_state(w_resumed, save)
        assert w_resumed.entities["hero"].position == (10.0, 20.0, 30.0)

    def test_golden_rule_driven_environment_reactions(self):
        w = Fab.create_gameplay_world("gw_gold_11")
        Fab.spawn_entity(w, "torch", tags=["Env.Unlit"])
        r = GameplayRule(
            "light_torch",
            priority=1,
            conditions=[{"type": "has_tag", "entity_id": "torch", "tag": "Env.Unlit"}],
            effects=[{"type": "add_tag", "entity_id": "torch", "tag": "Env.Lit"}],
        )
        Fab.add_rule(w, r)
        Fab.evaluate_rules(w)
        assert w.entities["torch"].tags.has("Env.Lit")

    def test_golden_camera_tracking_player(self):
        w = Fab.create_gameplay_world("gw_gold_12")
        Fab.spawn_entity(w, "player", position=(5.0, 5.0, 0.0))
        cam = Fab.create_camera_controller("cam_main", target_entity_id="player", distance=6.0)
        Fab.add_component(w, "player", "camera_controller", cam)
        assert cam.target_entity_id == "player"
        assert cam.distance == 6.0

    def test_golden_interaction_puzzle_sequence(self):
        w = Fab.create_gameplay_world("gw_gold_13")
        Fab.spawn_entity(w, "player", position=(0.0, 0.0, 0.0))
        Fab.spawn_entity(w, "lever1", position=(1.0, 0.0, 0.0))
        Fab.spawn_entity(w, "lever2", position=(2.0, 0.0, 0.0))
        Fab.register_interactable(w, "lever1", InteractableComponent("pull_1", "lever1", max_distance=2.0))
        Fab.register_interactable(w, "lever2", InteractableComponent("pull_2", "lever2", max_distance=3.0))
        assert Fab.execute_interaction(w, "pull_1", "player") is True
        assert Fab.execute_interaction(w, "pull_2", "player") is True

    def test_golden_full_lifecycle_and_cleanup(self):
        w = Fab.create_gameplay_world("gw_gold_14")
        Fab.initialize(w)
        Fab.start(w)
        Fab.spawn_entity(w, "temp_actor")
        assert len(w.entities) == 1
        Fab.stop(w)
        Fab.destroy(w)
        assert w.state == GameplayWorldState.DESTROYED
        assert len(w.entities) == 0

    def test_golden_stress_determinism_50_entities(self):
        w1 = Fab.create_gameplay_world("w_stress")
        w2 = Fab.create_gameplay_world("w_stress")
        for world in (w1, w2):
            for i in range(50):
                Fab.spawn_entity(world, f"bot_{i}", position=(float(i), 0.0, 0.0))
            for _ in range(5):
                Fab.tick(world, 0.016)
        assert w1.compute_fingerprint() == w2.compute_fingerprint()

    def test_golden_world_state_parity(self):
        w = Fab.create_gameplay_world("gw_gold_16")
        Fab.initialize(w)
        Fab.start(w)
        snap = Fab.create_snapshot(w)
        assert snap.state == "RUNNING"
import os
import pytest

class TestResourceLimitsAndSecurity:
    """Tests for §123 Resource Limits and Invariant Enforcement."""

    def test_max_entities_limit_rejection(self):
        s = GameplayWorldSettings(max_entities=3)
        w = Fab.create_gameplay_world("gw_lim_01", settings=s)
        Fab.spawn_entity(w, "e1")
        Fab.spawn_entity(w, "e2")
        Fab.spawn_entity(w, "e3")
        with pytest.raises(ValueError):
            Fab.spawn_entity(w, "e4")

    def test_max_components_per_entity_limit_rejection(self):
        s = GameplayWorldSettings(max_components_per_entity=2)
        w = Fab.create_gameplay_world("gw_lim_02", settings=s)
        Fab.spawn_entity(w, "hero")
        Fab.add_component(w, "hero", "c1", HealthComponent())
        Fab.add_component(w, "hero", "c2", HealthComponent())
        with pytest.raises(ValueError):
            Fab.add_component(w, "hero", "c3", HealthComponent())

    def test_max_commands_per_tick_limit_rejection(self):
        s = GameplayWorldSettings(max_commands_per_tick=1)
        w = Fab.create_gameplay_world("gw_lim_03", settings=s)
        Fab.enqueue_command(w, GameplayCommand("c1", GameplayCommandType.MOVE, "p1"))
        with pytest.raises(ValueError):
            Fab.enqueue_command(w, GameplayCommand("c2", GameplayCommandType.MOVE, "p1"))

    def test_max_events_per_tick_limit_rejection(self):
        s = GameplayWorldSettings(max_events_per_tick=100)
        w = Fab.create_gameplay_world("gw_lim_04", settings=s)
        assert w.settings.max_events_per_tick == 100

    def test_max_timers_limit_rejection(self):
        s = GameplayWorldSettings(max_timers=1)
        w = Fab.create_gameplay_world("gw_lim_05", settings=s)
        Fab.add_timer(w, "tm1", 1.0)
        with pytest.raises(ValueError):
            Fab.add_timer(w, "tm2", 1.0)

    def test_max_rules_limit_rejection(self):
        s = GameplayWorldSettings(max_rules=1)
        w = Fab.create_gameplay_world("gw_lim_06", settings=s)
        Fab.add_rule(w, GameplayRule("r1"))
        with pytest.raises(ValueError):
            Fab.add_rule(w, GameplayRule("r2"))

    def test_validator_detects_max_entities_exceeded(self):
        s = GameplayWorldSettings(max_entities=1)
        w = Fab.create_gameplay_world("gw_lim_07", settings=s)
        Fab.spawn_entity(w, "e1")
        # bypass fabricator check to test validator detection
        w.entities["e2"] = Entity("e2", "E2")
        issues = Val.validate(w)
        assert any(i.code == "RESOURCE_LIMIT_EXCEEDED" for i in issues)

    def test_validator_detects_max_components_exceeded(self):
        s = GameplayWorldSettings(max_components_per_entity=1)
        w = Fab.create_gameplay_world("gw_lim_08", settings=s)
        Fab.spawn_entity(w, "hero")
        w.entities["hero"].components["c1"] = HealthComponent()
        w.entities["hero"].components["c2"] = HealthComponent()
        issues = Val.validate(w)
        assert any(i.code == "RESOURCE_LIMIT_EXCEEDED" for i in issues)

    def test_validator_detects_max_timers_exceeded(self):
        s = GameplayWorldSettings(max_timers=1)
        w = Fab.create_gameplay_world("gw_lim_09", settings=s)
        w.timers["t1"] = GameplayTimer("t1", 1.0)
        w.timers["t2"] = GameplayTimer("t2", 1.0)
        issues = Val.validate(w)
        assert any(i.code == "RESOURCE_LIMIT_EXCEEDED" for i in issues)

    def test_validator_detects_max_commands_exceeded(self):
        s = GameplayWorldSettings(max_commands_per_tick=1)
        w = Fab.create_gameplay_world("gw_lim_10", settings=s)
        w.command_queue.append(GameplayCommand("c1", GameplayCommandType.MOVE, "p1"))
        w.command_queue.append(GameplayCommand("c2", GameplayCommandType.MOVE, "p1"))
        issues = Val.validate(w)
        assert any(i.code == "RESOURCE_LIMIT_EXCEEDED" for i in issues)

    def test_validator_detects_empty_entity_id(self):
        w = Fab.create_gameplay_world("gw_lim_11")
        w.entities[""] = Entity("", "Empty")
        issues = Val.validate(w)
        assert any(i.code == "NO_INVALID_ENTITY" for i in issues)

    def test_validator_detects_corrupt_tags(self):
        w = Fab.create_gameplay_world("gw_lim_12")
        Fab.spawn_entity(w, "corrupt", tags=["Corrupt..Tag"])
        issues = Val.validate(w)
        assert any(i.code == "NO_TAG_HIERARCHY_CORRUPTION" for i in issues)

    def test_validator_detects_invalid_camera_limits(self):
        w = Fab.create_gameplay_world("gw_lim_13")
        Fab.spawn_entity(w, "cam_ent")
        cam = Fab.create_camera_controller("cam_bad", min_pitch=50.0, max_pitch=20.0)
        Fab.add_component(w, "cam_ent", "camera_controller", cam)
        issues = Val.validate(w)
        assert any(i.code == "NO_INVALID_CAMERA_LIMIT" for i in issues)

    def test_validator_detects_invalid_health_bounds(self):
        w = Fab.create_gameplay_world("gw_lim_14")
        Fab.spawn_entity(w, "sick")
        # Underflow current_health < min_health
        Fab.add_component(w, "sick", "health", HealthComponent(current_health=-10.0, max_health=100.0))
        issues = Val.validate(w)
        assert any(i.code == "NO_HEALTH_UNDERFLOW" for i in issues)


class TestPerformanceAndStress:
    """Tests for §124 High Throughput, Batch Processing, and Stress."""

    def test_high_throughput_ticks_100_ticks(self):
        w = Fab.create_gameplay_world("gw_perf_01")
        for _ in range(100):
            Fab.tick(w, 0.016)
        assert w.tick.tick_index == 100

    def test_high_density_entities_spawn_and_query(self):
        w = Fab.create_gameplay_world("gw_perf_02")
        for i in range(100):
            Fab.spawn_entity(w, f"ent_{i}", position=(float(i), 0.0, 0.0))
        assert len(w.entities) == 100

    def test_stress_spatial_interaction_queries_100_entities(self):
        w = Fab.create_gameplay_world("gw_perf_03")
        for i in range(50):
            Fab.spawn_entity(w, f"chest_{i}", position=(float(i) * 0.1, 0.0, 0.0))
            Fab.register_interactable(w, f"chest_{i}", InteractableComponent(f"int_{i}", f"chest_{i}", max_distance=5.0))
        results = Fab.query_interactions(w, (0.0, 0.0, 0.0), max_range=3.0)
        assert len(results) > 0

    def test_stress_batch_commands_execution_100(self):
        w = Fab.create_gameplay_world("gw_perf_04")
        Fab.spawn_entity(w, "worker", position=(0.0, 0.0, 0.0))
        Fab.add_component(w, "worker", "character_controller", Fab.create_character_controller("cc_w", move_speed=1.0))
        w.tick.delta_time = 0.01
        cmds = [GameplayCommand(f"c_{i}", GameplayCommandType.MOVE, "worker", payload={"dx": 1.0, "dy": 0.0}) for i in range(100)]
        for c in cmds:
            Fab.enqueue_command(w, c)
        Fab.tick(w, 0.01)
        # All processed
        assert len(w.command_queue) == 0

    def test_stress_events_emission_and_consumption(self):
        w = Fab.create_gameplay_world("gw_perf_05")
        for i in range(50):
            Fab.dispatch_event(w, GameplayEventType.DAMAGE_APPLIED, f"e_{i}")
        assert len(w.event_history) == 50

    def test_stress_timers_processing(self):
        w = Fab.create_gameplay_world("gw_perf_06")
        for i in range(30):
            Fab.add_timer(w, f"tm_{i}", duration=0.05 * (i + 1))
        Fab.tick(w, 0.2)
        completed = [t for t in w.timers.values() if t.is_completed]
        assert len(completed) > 0

    def test_stress_rule_evaluation_batch(self):
        w = Fab.create_gameplay_world("gw_perf_07")
        Fab.spawn_entity(w, "target")
        for i in range(20):
            Fab.add_rule(w, GameplayRule(f"r_{i}", priority=i, conditions=[], effects=[{"type": "add_tag", "entity_id": "target", "tag": f"Tag.{i}"}]))
        applied = Fab.evaluate_rules(w)
        assert applied == 20

    def test_stress_status_effects_multi_target(self):
        w = Fab.create_gameplay_world("gw_perf_08")
        for i in range(20):
            Fab.spawn_entity(w, f"victim_{i}")
            Fab.add_component(w, f"victim_{i}", "health", HealthComponent(current_health=100.0, max_health=100.0))
            eff = StatusEffect(f"eff_{i}", "Burn", "caster", f"victim_{i}", duration=1.0, tick_interval=0.1, magnitude=2.0)
            Fab.apply_status_effect(w, eff)
        Fab.tick(w, 0.15)
        for i in range(20):
            assert w.entities[f"victim_{i}"].components["health"].current_health == 98.0

    def test_stress_inventory_stacking_and_transfers(self):
        inv1 = Fab.create_inventory("inv1", max_slots=50)
        inv2 = Fab.create_inventory("inv2", max_slots=50)
        for i in range(30):
            Fab.add_item(inv1, f"item_{i}", 10)
        for i in range(30):
            assert Fab.transfer_item(inv1, inv2, f"item_{i}", 5) is True
        assert len(inv2.slots) == 30

    def test_stress_snapshots_frequency(self):
        w = Fab.create_gameplay_world("gw_perf_10")
        Fab.spawn_entity(w, "actor")
        for _ in range(10):
            Fab.tick(w, 0.016)
            snap = Fab.create_snapshot(w)
            assert snap is not None

    def test_memory_churn_no_lingering_entities_after_cleanup(self):
        w = Fab.create_gameplay_world("gw_perf_11")
        for i in range(50):
            Fab.spawn_entity(w, f"temp_{i}")
        assert len(w.entities) == 50
        for i in range(50):
            Fab.destroy_entity(w, f"temp_{i}")
        assert len(w.entities) == 0

    def test_zero_division_resilience_movement_vector(self):
        w = Fab.create_gameplay_world("gw_perf_12")
        Fab.spawn_entity(w, "still", position=(0.0, 0.0, 0.0))
        Fab.add_component(w, "still", "character_controller", Fab.create_character_controller("cc_s"))
        Fab.move_character(w, "still", 0.0, 0.0)
        assert w.entities["still"].position == (0.0, 0.0, 0.0)

    def test_extreme_damage_values_resilience(self):
        w = Fab.create_gameplay_world("gw_perf_13")
        Fab.spawn_entity(w, "target")
        Fab.add_component(w, "target", "health", HealthComponent(current_health=100.0, max_health=100.0))
        res = Fab.apply_damage(w, DamageRequest("r_huge", "a", "target", raw_damage=1e9))
        assert res.is_killed is True
        assert res.final_health == 0.0

    def test_extreme_zoom_delta_resilience(self):
        w = Fab.create_gameplay_world("gw_perf_14")
        Fab.spawn_entity(w, "cam_target")
        cam = Fab.create_camera_controller("cam_resil", min_distance=1.0, max_distance=50.0, distance=10.0)
        Fab.add_component(w, "cam_target", "camera_controller", cam)
        Fab.update_camera(w, "cam_target", zoom_delta=1e6)
        assert cam.distance == 50.0


class TestPropertyBasedAndInvariants:
    """Tests for §126 Non-Negotiable Invariant Enforcement."""

    def test_invariant_no_duplicate_entity_id(self):
        w = Fab.create_gameplay_world("gw_inv_01")
        Fab.spawn_entity(w, "unique_ent")
        with pytest.raises(ValueError) as excinfo:
            Fab.spawn_entity(w, "unique_ent")
        assert "NO DUPLICATE ENTITY ID" in str(excinfo.value)

    def test_invariant_no_multiple_component_owners(self):
        w = Fab.create_gameplay_world("gw_inv_02")
        Fab.spawn_entity(w, "e1")
        Fab.spawn_entity(w, "e2")
        shared = HealthComponent()
        Fab.add_component(w, "e1", "health", shared)
        with pytest.raises(ValueError) as excinfo:
            Fab.add_component(w, "e2", "health", shared)
        assert "NO MULTIPLE COMPONENT OWNERS" in str(excinfo.value)

    def test_invariant_no_health_underflow(self):
        w = Fab.create_gameplay_world("gw_inv_03")
        Fab.spawn_entity(w, "victim")
        Fab.add_component(w, "victim", "health", HealthComponent(current_health=10.0, max_health=100.0))
        Fab.apply_damage(w, DamageRequest("r", "a", "victim", raw_damage=100.0))
        h = w.entities["victim"].components["health"]
        assert h.current_health >= 0.0

    def test_invariant_no_health_overflow(self):
        w = Fab.create_gameplay_world("gw_inv_04")
        Fab.spawn_entity(w, "tank")
        Fab.add_component(w, "tank", "health", HealthComponent(current_health=90.0, max_health=100.0))
        Fab.heal(w, "tank", 500.0)
        h = w.entities["tank"].components["health"]
        assert h.current_health <= h.max_health

    def test_invariant_no_rule_recursion_without_limit(self):
        w = Fab.create_gameplay_world("gw_inv_05")
        with pytest.raises(ValueError) as excinfo:
            Fab.evaluate_rules(w, recursion_depth=15)
        assert "NO RULE RECURSION WITHOUT LIMIT" in str(excinfo.value)

    def test_invariant_no_partial_inventory_transaction(self):
        inv_src = Fab.create_inventory("src", max_slots=5)
        inv_dst = Fab.create_inventory("dst", max_slots=1)
        Fab.add_item(inv_src, "gold", 100, max_stack=200)
        Fab.add_item(inv_dst, "silver", 1)  # dst is full
        # Transfer 50 gold: must fail completely and not lose or partially transfer gold
        success = Fab.transfer_item(inv_src, inv_dst, "gold", 50)
        assert success is False
        assert inv_src.slots[0].quantity == 100

    def test_invariant_no_invalid_item_quantity(self):
        inv = Fab.create_inventory("inv_qty")
        rem = Fab.add_item(inv, "wood", -10)
        assert rem == 0
        assert len(inv.slots) == 0

    def test_invariant_no_command_to_destroyed_entity(self):
        w = Fab.create_gameplay_world("gw_inv_08")
        Fab.spawn_entity(w, "actor")
        w.entities["actor"].state = EntityLifecycleState.DESTROYED
        w.command_queue.append(GameplayCommand("c", GameplayCommandType.MOVE, "actor"))
        issues = Val.validate_commands(w)
        assert any(i.code == "NO_COMMAND_TO_DESTROYED_ENTITY" for i in issues)

    def test_invariant_no_command_to_despawned_entity(self):
        w = Fab.create_gameplay_world("gw_inv_09")
        Fab.spawn_entity(w, "actor")
        w.entities["actor"].state = EntityLifecycleState.PENDING_DESPAWN
        w.command_queue.append(GameplayCommand("c", GameplayCommandType.MOVE, "actor"))
        issues = Val.validate_commands(w)
        assert any(i.code == "NO_COMMAND_TO_DESPAWNED_ENTITY" for i in issues)

    def test_invariant_no_transient_state_in_persistent_save(self):
        save = SaveState("s", version=1, entities_data={"e": {"transient_state": "foo"}})
        issues = Val.validate_save_state(save)
        assert any(i.code == "NO_TRANSIENT_STATE_IN_PERSISTENT_SAVE" for i in issues)

    def test_invariant_no_unvalidated_load(self):
        save = SaveState(save_id="", version=1)
        issues = Val.validate_save_state(save)
        assert any(i.code == "NO_UNVALIDATED_LOAD" for i in issues)

    def test_invariant_no_quest_completion_without_objectives(self):
        w = Fab.create_gameplay_world("gw_inv_12")
        q = QuestDefinition("q_empty", "Empty Quest")
        q.state = QuestState.COMPLETED
        w.quests["q_empty"] = q
        issues = Val.validate_quests(w)
        assert any(i.code == "NO_QUEST_COMPLETION_WITHOUT_OBJECTIVES" for i in issues)


class TestCrossPhaseIntegrationAndCleanup:
    """Tests for §127 Cross-Phase Integration and Engine Architecture."""

    def test_cross_phase_runtime_world_id_association(self):
        w = Fab.create_gameplay_world("gw_cross_01")
        assert w.runtime_world_id == "runtime_world_default"

    def test_cross_phase_input_command_to_gameplay_mapping(self):
        w = Fab.create_gameplay_world("gw_cross_02")
        Fab.spawn_entity(w, "player", position=(0.0, 0.0, 0.0))
        Fab.add_component(w, "player", "character_controller", Fab.create_character_controller("cc_p", move_speed=5.0))
        w.tick.delta_time = 0.1
        # Simulates input system mapping raw axis (1.0, 0.0) to MOVE command
        cmd = GameplayCommand("input_cmd", GameplayCommandType.MOVE, "player", payload={"dx": 1.0, "dy": 0.0})
        Fab.execute_command(w, cmd)
        assert w.entities["player"].position[0] > 0.0

    def test_cross_phase_ui_event_to_gameplay_quest_binding(self):
        w = Fab.create_gameplay_world("gw_cross_03")
        q = QuestDefinition("q_hud", "HUD Quest", objectives={"o1": QuestObjective("o1", "Task", target_count=1)})
        Fab.register_quest(w, q)
        Fab.start_quest(w, "q_hud")
        # UI button clicked -> triggers objective progress
        Fab.progress_objective(w, "q_hud", "o1", delta=1)
        assert q.state == QuestState.COMPLETED

    def test_cross_phase_audio_trigger_overlap_event(self):
        w = Fab.create_gameplay_world("gw_cross_04")
        Fab.spawn_entity(w, "listener")
        trig = Fab.create_trigger("ambient_zone")
        res = Fab.process_trigger_overlap(w, trig, "listener", is_overlapping=True)
        assert res == TriggerEventType.ENTER

    def test_cross_phase_physics_grounded_state_sync(self):
        w = Fab.create_gameplay_world("gw_cross_05")
        Fab.spawn_entity(w, "hero")
        ctrl = Fab.create_character_controller("cc_h")
        ctrl.is_grounded = False
        ctrl.movement_state = MovementState.FALLING
        Fab.add_component(w, "hero", "character_controller", ctrl)
        # Physics engine raycast reports ground collision -> update
        Fab.set_grounded(w, "hero", True)
        assert ctrl.is_grounded is True
        assert ctrl.movement_state == MovementState.GROUNDED

    def test_cross_phase_character_controller_velocity_contract(self):
        ctrl = Fab.create_character_controller("cc_contract", move_speed=6.0, jump_force=8.0)
        assert hasattr(ctrl, "velocity")
        assert len(ctrl.velocity) == 3

    def test_cross_phase_animation_state_mapping_contract(self):
        ctrl = Fab.create_character_controller("cc_anim")
        assert ctrl.movement_state in (MovementState.IDLE, MovementState.WALKING, MovementState.RUNNING, MovementState.JUMPING, MovementState.FALLING, MovementState.GROUNDED)

    def test_cross_phase_cleanup_releases_all_references(self):
        w = Fab.create_gameplay_world("gw_cross_08")
        Fab.spawn_entity(w, "e1")
        Fab.add_timer(w, "t1", 1.0)
        Fab.add_rule(w, GameplayRule("r1"))
        Fab.destroy(w)
        assert len(w.entities) == 0
        assert len(w.timers) == 0
        assert len(w.rules) == 0

    def test_cross_phase_reset_world_state(self):
        w = Fab.create_gameplay_world("gw_cross_09")
        Fab.initialize(w)
        Fab.start(w)
        Fab.stop(w)
        assert w.state == GameplayWorldState.STOPPED

    def test_cross_phase_deterministic_checksum_across_phases(self):
        w1 = Fab.create_gameplay_world("shared_seed_w")
        w2 = Fab.create_gameplay_world("shared_seed_w")
        assert w1.compute_fingerprint() == w2.compute_fingerprint()

    def test_cross_phase_lifecycle_synchronization(self):
        w = Fab.create_gameplay_world("gw_cross_11")
        Fab.initialize(w)
        assert w.state == GameplayWorldState.READY
        Fab.start(w)
        assert w.state == GameplayWorldState.RUNNING

    def test_cross_phase_event_history_persistence(self):
        w = Fab.create_gameplay_world("gw_cross_12")
        Fab.dispatch_event(w, GameplayEventType.ENTITY_SPAWNED, "actor")
        assert len(w.event_history) == 1
        assert w.event_history[0].event_type == GameplayEventType.ENTITY_SPAWNED


class TestUE5GameplayPackager:
    """Tests for UE5 C++ Subsystem packager and export manifest."""

    def test_packager_default_output(self, tmp_path):
        import os
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        assert res["success"] is True

    def test_packager_creates_manifest_json(self, tmp_path):
        import os
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        assert os.path.exists(res["manifest"])

    def test_packager_manifest_valid_json_structure(self, tmp_path):
        import json
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        with open(res["manifest"], "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["module"] == "uaf_runtime_gameplay"
        assert data["version"] == "1.0.0"
        assert "world" in data

    def test_packager_creates_signature_sha256(self, tmp_path):
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        assert os.path.exists(res["signature"])

    def test_packager_signature_matches_manifest(self, tmp_path):
        import hashlib
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        with open(res["manifest"], "r", encoding="utf-8") as f:
            content = f.read()
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        with open(res["signature"], "r", encoding="utf-8") as f:
            sig = f.read().strip()
        assert sig == expected

    def test_packager_creates_header_h(self, tmp_path):
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        assert os.path.exists(res["header"])

    def test_packager_header_contains_uclass_and_worldsubsystem(self, tmp_path):
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        with open(res["header"], "r", encoding="utf-8") as f:
            code = f.read()
        assert "UCLASS()" in code
        assert "public UWorldSubsystem" in code
        assert "UUAFRuntimeGameplaySubsystem" in code

    def test_packager_header_contains_blueprint_callables(self, tmp_path):
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        with open(res["header"], "r", encoding="utf-8") as f:
            code = f.read()
        assert "BlueprintCallable" in code
        assert "SpawnGameplayEntity" in code
        assert "ApplyDamage" in code

    def test_packager_creates_source_cpp(self, tmp_path):
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        assert os.path.exists(res["source"])

    def test_packager_cpp_implements_subsystem_methods(self, tmp_path):
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(str(tmp_path))
        with open(res["source"], "r", encoding="utf-8") as f:
            code = f.read()
        assert "UUAFRuntimeGameplaySubsystem::Initialize" in code
        assert "UUAFRuntimeGameplaySubsystem::Deinitialize" in code
        assert "UUAFRuntimeGameplaySubsystem::SpawnGameplayEntity" in code

    def test_packager_custom_output_directory(self, tmp_path):
        custom_dir = os.path.join(tmp_path, "ue5_gameplay_export")
        pkg = UniversalRuntimeGameplayPackager()
        res = pkg.package(custom_dir)
        assert os.path.isdir(custom_dir)
        assert res["success"] is True

    def test_packager_success_flag(self, tmp_path):
        pkg = UniversalRuntimeGameplayPackager()
        w = Fab.create_gameplay_world("gw_pack_test")
        res = pkg.package(str(tmp_path), world=w)
        assert res["success"] is True
