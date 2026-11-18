"""
Tests for Core Gameplay & Entities (UAF-81.58 Sections 3-11, 187).
"""

import pytest
from uaf.universal_gameplay import (
    EntityType,
    GameplayTag,
    GameplayCommandType,
    CommandFailureCode,
    GameplayCommand,
    CommandResult,
    GameplayEntity,
    GameplayState,
    UniversalGameplayFabricator,
)


def test_entity_types_enum():
    types = {t.value for t in EntityType}
    expected = {
        "PLAYER",
        "NPC",
        "CREATURE",
        "OBJECT",
        "VEHICLE",
        "LOCATION",
        "FACTION",
        "QUEST_GIVER",
        "MERCHANT",
        "CUSTOM",
    }
    assert types == expected


def test_gameplay_tag_validity():
    t_valid1 = GameplayTag("character.player")
    t_valid2 = GameplayTag("item.weapon.sword")
    t_invalid1 = GameplayTag("player")  # No dot/namespace
    t_invalid2 = GameplayTag("")

    assert t_valid1.is_valid() is True
    assert t_valid2.is_valid() is True
    assert t_invalid1.is_valid() is False
    assert t_invalid2.is_valid() is False


def test_gameplay_command_creation():
    cmd = GameplayCommand(
        command_id="CMD_001",
        source="PLAYER_1",
        target="CHEST_01",
        command_type=GameplayCommandType.INTERACT,
        payload={"action": "OPEN"},
        timestamp=1.5,
    )
    assert cmd.command_id == "CMD_001"
    assert cmd.source == "PLAYER_1"
    assert cmd.target == "CHEST_01"
    assert cmd.command_type == GameplayCommandType.INTERACT
    assert cmd.payload["action"] == "OPEN"
    assert cmd.timestamp == 1.5


def test_command_result_success():
    res = CommandResult(success=True, message="Action performed")
    assert res.success is True
    assert res.failure_code == CommandFailureCode.NONE
    assert res.message == "Action performed"


def test_command_result_failure():
    res = CommandResult(
        success=False,
        failure_code=CommandFailureCode.OUT_OF_RANGE,
        message="Too far away",
    )
    assert res.success is False
    assert res.failure_code == CommandFailureCode.OUT_OF_RANGE
    assert res.message == "Too far away"


def test_spawn_entity_defaults():
    entity = UniversalGameplayFabricator.spawn_entity("HERO_01", EntityType.PLAYER, health=120.0, gold=50)
    assert entity.entity_id == "HERO_01"
    assert entity.entity_type == EntityType.PLAYER
    assert entity.health == 120.0
    assert entity.max_health == 120.0
    assert entity.wallet.get_balance() == 50
    assert entity.inventory.max_slots == 20
    assert entity.progression.current_level == 1


def test_entity_alive_status():
    entity = UniversalGameplayFabricator.spawn_entity("TARGET", EntityType.NPC, health=50.0)
    assert entity.is_alive() is True

    entity.health = 0.0
    assert entity.is_alive() is False

    entity.health = -10.0
    assert entity.is_alive() is False


def test_gameplay_state_creation():
    state = GameplayState("STATE_MAIN", seed=12345)
    assert state.state_id == "STATE_MAIN"
    assert state.seed == 12345
    assert len(state.entities) == 0
    assert len(state.quests) == 0
    assert state.current_tick == 0


def test_gameplay_state_hash_determinism():
    s1 = GameplayState("STATE_TEST", seed=42)
    s2 = GameplayState("STATE_TEST", seed=42)
    assert s1.gameplay_state_hash == s2.gameplay_state_hash


def test_advance_simulation_tick():
    state = GameplayState("STATE_TICK")
    assert state.current_tick == 0

    UniversalGameplayFabricator.advance_simulation_tick(state, dt=0.033)
    assert state.current_tick == 1

    UniversalGameplayFabricator.advance_simulation_tick(state, dt=0.033)
    assert state.current_tick == 2


def test_command_failure_codes_enum():
    codes = {c.value for c in CommandFailureCode}
    assert "NONE" in codes
    assert "INVALID_COMMAND" in codes
    assert "INVALID_TARGET" in codes
    assert "INVENTORY_FULL" in codes
    assert "INSUFFICIENT_RESOURCE" in codes
    assert "COOLDOWN_ACTIVE" in codes
    assert "PERMISSION_DENIED" in codes
