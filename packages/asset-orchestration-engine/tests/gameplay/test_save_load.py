"""
Tests for Gameplay State Serialization, Save, and Load (UAF-81.58 Sections 187, 201-205).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    GameplayState,
    GameplaySaveState,
    EntityType,
    QuestDefinition,
    QuestObjective,
    ObjectiveType,
    QuestState,
    CurrencyType,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_save_state_creation():
    state = GameplayState("SIM_SAVE_1", seed=42)
    state.current_tick = 120
    save = UniversalGameplayFabricator.save_state(state)

    assert save.save_id == "SAVE_SIM_SAVE_1_120"
    assert save.state_id == "SIM_SAVE_1"
    assert save.seed == 42
    assert save.current_tick == 120
    assert save.timestamp == 120.0
    assert save.schema_version == "1.0.0"


def test_save_state_hash_calculation():
    state = GameplayState("SIM_HASH", seed=101)
    save = UniversalGameplayFabricator.save_state(state)
    assert isinstance(save.state_hash, str)
    assert len(save.state_hash) == 64  # SHA-256 hex string


def test_save_state_entity_serialization():
    state = GameplayState("SIM_ENT", seed=10)
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.health = 75.0
    p.wallet.add(250, CurrencyType.GOLD)
    p.progression.current_level = 3
    p.progression.current_xp = 40
    state.entities[p.entity_id] = p

    save = UniversalGameplayFabricator.save_state(state)
    assert len(save.serialized_entities) == 1
    e_dict = save.serialized_entities[0]
    assert e_dict["entity_id"] == "HERO"
    assert e_dict["health"] == 75.0
    assert e_dict["gold"] == 250
    assert e_dict["level"] == 3
    assert e_dict["xp"] == 40


def test_save_state_quest_serialization():
    state = GameplayState("SIM_Q", seed=20)
    q = QuestDefinition(
        quest_id="Q_MAIN",
        title="Main Quest",
        description="",
        giver="NPC",
        state=QuestState.ACTIVE,
    )
    state.quests[q.quest_id] = q

    save = UniversalGameplayFabricator.save_state(state)
    assert len(save.serialized_quests) == 1
    assert save.serialized_quests[0]["quest_id"] == "Q_MAIN"
    assert save.serialized_quests[0]["state"] == "ACTIVE"


def test_save_state_world_flags_deep_copy():
    state = GameplayState("SIM_FLAGS", seed=30)
    state.world_flags["GATE_OPEN"] = True
    save = UniversalGameplayFabricator.save_state(state)

    # Mutate original
    state.world_flags["GATE_OPEN"] = False
    state.world_flags["NEW_FLAG"] = 123

    assert save.flags["GATE_OPEN"] is True
    assert "NEW_FLAG" not in save.flags


def test_load_state_tick_restoration():
    state = GameplayState("SIM_TICK", seed=5)
    state.current_tick = 500
    save = UniversalGameplayFabricator.save_state(state)

    # Reset state tick
    state.current_tick = 0
    UniversalGameplayFabricator.load_state(state, save)
    assert state.current_tick == 500


def test_load_state_flags_restoration():
    state = GameplayState("SIM_FLAGS_RESTORE", seed=5)
    state.world_flags["PUZZLE_SOLVED"] = True
    save = UniversalGameplayFabricator.save_state(state)

    state.world_flags.clear()
    assert len(state.world_flags) == 0

    UniversalGameplayFabricator.load_state(state, save)
    assert state.world_flags["PUZZLE_SOLVED"] is True


def test_load_state_quests_restoration():
    state = GameplayState("SIM_Q_RESTORE", seed=5)
    q = QuestDefinition("Q_EPIC", "Epic", "", "NPC", state=QuestState.COMPLETED)
    state.quests[q.quest_id] = q
    save = UniversalGameplayFabricator.save_state(state)

    # Change quest state
    q.state = QuestState.FAILED
    UniversalGameplayFabricator.load_state(state, save)
    assert q.state == QuestState.COMPLETED


def test_load_state_entity_health_restoration():
    state = GameplayState("SIM_HP", seed=5)
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.health = 35.0
    state.entities[p.entity_id] = p
    save = UniversalGameplayFabricator.save_state(state)

    p.health = 100.0
    UniversalGameplayFabricator.load_state(state, save)
    assert p.health == 35.0


def test_load_state_entity_gold_restoration():
    state = GameplayState("SIM_GOLD", seed=5)
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.wallet.balances[CurrencyType.GOLD] = 888
    state.entities[p.entity_id] = p
    save = UniversalGameplayFabricator.save_state(state)

    p.wallet.balances[CurrencyType.GOLD] = 0
    UniversalGameplayFabricator.load_state(state, save)
    assert p.wallet.get_balance(CurrencyType.GOLD) == 888


def test_load_state_entity_progression_restoration():
    state = GameplayState("SIM_PROG_RESTORE", seed=5)
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.progression.current_level = 5
    p.progression.current_xp = 125
    state.entities[p.entity_id] = p
    save = UniversalGameplayFabricator.save_state(state)

    p.progression.current_level = 1
    p.progression.current_xp = 0
    UniversalGameplayFabricator.load_state(state, save)
    assert p.progression.current_level == 5
    assert p.progression.current_xp == 125


def test_save_load_roundtrip_fidelity():
    state = GameplayState("SIM_ROUNDTRIP", seed=777)
    state.current_tick = 250
    state.world_flags["BOSS_KILLED"] = True

    p = UniversalGameplayFabricator.spawn_entity("PLAYER_1", EntityType.PLAYER)
    p.health = 60.0
    p.wallet.balances[CurrencyType.GOLD] = 350
    state.entities[p.entity_id] = p

    q = QuestDefinition("Q_TOWN", "Town Rescue", "", "ELDER", state=QuestState.ACTIVE)
    state.quests[q.quest_id] = q

    save = UniversalGameplayFabricator.save_state(state)

    # Completely scramble current state
    state.current_tick = 999
    state.world_flags.clear()
    p.health = 10.0
    p.wallet.balances[CurrencyType.GOLD] = 0
    q.state = QuestState.FAILED

    UniversalGameplayFabricator.load_state(state, save)

    assert state.current_tick == 250
    assert state.world_flags["BOSS_KILLED"] is True
    assert p.health == 60.0
    assert p.wallet.get_balance(CurrencyType.GOLD) == 350
    assert q.state == QuestState.ACTIVE


def test_save_state_multiple_snapshots():
    state = GameplayState("SIM_MULTISAVE", seed=10)
    state.current_tick = 10
    save_1 = UniversalGameplayFabricator.save_state(state)

    state.current_tick = 20
    save_2 = UniversalGameplayFabricator.save_state(state)

    assert save_1.save_id != save_2.save_id
    assert save_1.current_tick == 10
    assert save_2.current_tick == 20


def test_load_state_with_missing_quest_graceful():
    state = GameplayState("SIM_GHOST_Q", seed=1)
    save = GameplaySaveState(
        save_id="SAVE_GHOST",
        state_id="SIM_GHOST_Q",
        seed=1,
        current_tick=10,
        serialized_quests=[{"quest_id": "DELETED_QUEST", "state": "COMPLETED"}],
    )
    # Should not raise exception
    UniversalGameplayFabricator.load_state(state, save)


def test_load_state_with_missing_entity_graceful():
    state = GameplayState("SIM_GHOST_E", seed=1)
    save = GameplaySaveState(
        save_id="SAVE_GHOST_E",
        state_id="SIM_GHOST_E",
        seed=1,
        current_tick=10,
        serialized_entities=[{"entity_id": "DELETED_HERO", "health": 50.0}],
    )
    # Should not raise exception
    UniversalGameplayFabricator.load_state(state, save)
