"""Standard production and stress scenario definitions for Golden Vertical Slice."""

from __future__ import annotations
from uaf.golden_slice.scenarios.scenario import ScenarioDefinition, ScenarioStep


def create_golden_main_scenario() -> ScenarioDefinition:
    """Canonical 19-step Golden Slice playthrough scenario (Section 95)."""
    steps = [
        ScenarioStep("step_01_boot", "BOOT", {"timeout_s": 10.0}),
        ScenarioStep("step_02_load_world", "LOAD_WORLD", {"biome": "temperate_forest"}),
        ScenarioStep("step_03_spawn_player", "SPAWN_PLAYER", {"spawn_id": "spawn_player_primary"}),
        ScenarioStep("step_04_move", "MOVE_TO", {"target": (40.0, 50.0, 50.0)}),
        ScenarioStep("step_05_encounter_enemy", "ENCOUNTER_ENEMY", {"archetype": "scout"}),
        ScenarioStep("step_06_ai_detection", "AI_DETECTION", {"perception": "sight"}),
        ScenarioStep("step_07_combat", "INITIATE_COMBAT", {"stance": "melee"}),
        ScenarioStep("step_08_damage", "APPLY_DAMAGE", {"action": "light_attack", "damage": 35.0}),
        ScenarioStep("step_09_vfx", "TRIGGER_VFX", {"system_id": "blood_damage"}),
        ScenarioStep("step_10_audio", "PLAY_AUDIO", {"cue_id": "impacts"}),
        ScenarioStep("step_11_enemy_death", "ENEMY_DEATH", {"enemy_id": "enemy_scout_01"}),
        ScenarioStep("step_12_loot", "PICKUP_LOOT", {"item_id": "item_health_potion"}),
        ScenarioStep("step_13_objective", "PROGRESS_OBJECTIVE", {"amount": 25}),
        ScenarioStep("step_14_streaming_transition", "STREAMING_TRANSITION", {"cell_from": "cell_0_0", "cell_to": "cell_0_1"}),
        ScenarioStep("step_15_cinematic", "PLAY_CINEMATIC", {"sequence_id": "seq_intro_cinematic"}),
        ScenarioStep("step_16_save", "SAVE_GAME", {"slot": "quicksave_01"}),
        ScenarioStep("step_17_network_replication", "SYNC_NETWORK_STATE", {"clients": 4}),
        ScenarioStep("step_18_reload", "LOAD_GAME", {"slot": "quicksave_01"}),
        ScenarioStep("step_19_validate", "VALIDATE_STATE_INTEGRITY", {}),
    ]

    return ScenarioDefinition(
        scenario_id="scenario_golden_main",
        name="Golden Slice Main Playthrough",
        description="Comprehensive 19-step end-to-end golden path verification.",
        steps=steps,
    )


def create_extended_stress_scenario() -> ScenarioDefinition:
    """Stress scenario testing high AI count, streaming, and multiplayer load (Section 96)."""
    steps = [
        ScenarioStep("stress_01_setup_server", "DEDICATED_SERVER_START", {"tick_rate": 60}),
        ScenarioStep("stress_02_connect_clients", "CONNECT_CLIENTS", {"count": 4}),
        ScenarioStep("stress_03_spawn_ai_horde", "SPAWN_AI_HORDE", {"count": 50}),
        ScenarioStep("stress_04_trigger_heavy_vfx", "SPAWN_VFX_FIELD", {"system_count": 20}),
        ScenarioStep("stress_05_stream_cells", "RAPID_STREAMING_TRAVERSAL", {"cells_count": 8}),
        ScenarioStep("stress_06_dynamic_lighting", "RAPID_DAY_NIGHT_CYCLE", {"duration_s": 5.0}),
        ScenarioStep("stress_07_verify_load_budget", "VERIFY_BUDGET_LIMITS", {}),
    ]

    return ScenarioDefinition(
        scenario_id="scenario_extended_stress",
        name="Extended Multiplayer Stress Load",
        description="Heavy stress test with 4 clients, dedicated server, 50 AI agents, and streaming load.",
        steps=steps,
    )


def create_determinism_scenario() -> ScenarioDefinition:
    """Deterministic replay verification scenario (Section 97)."""
    steps = [
        ScenarioStep("det_01_seed_init", "SET_SEED", {"seed": 1337}),
        ScenarioStep("det_02_fixed_moves", "REPLAY_INPUT_TRACE", {"frames": 100}),
        ScenarioStep("det_03_fixed_combat", "EXECUTE_DETERMINISTIC_COMBAT", {"attacks": 5}),
        ScenarioStep("det_04_capture_hash", "COMPUTE_STATE_HASH", {}),
    ]

    return ScenarioDefinition(
        scenario_id="scenario_determinism",
        name="Deterministic State Hash Equivalence",
        description="Validates reproducible identical hashes across separate runs.",
        steps=steps,
    )


def create_recovery_scenario() -> ScenarioDefinition:
    """Fault-injection and recovery verification scenario (Section 98)."""
    steps = [
        ScenarioStep("rec_01_connect", "CONNECT_BRIDGE", {}),
        ScenarioStep("rec_02_simulate_disconnect", "FORCE_DISCONNECT", {}),
        ScenarioStep("rec_03_reconnect", "ATTEMPT_RECONNECT", {}),
        ScenarioStep("rec_04_simulate_crash", "SIMULATE_UE5_CRASH", {}),
        ScenarioStep("rec_05_restart_recover", "RESTART_AND_RECOVER", {}),
        ScenarioStep("rec_06_verify_restoration", "VERIFY_RESTORED_STATE", {}),
    ]

    return ScenarioDefinition(
        scenario_id="scenario_recovery",
        name="Crash & Fault Recovery",
        description="Validates resilient reconnection, outbound freezing, and state reconstruction.",
        steps=steps,
    )
