"""
Tests for World Flags, Game State Persistence, and Unlocks (UAF-81.58 Sections 186-191, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    WorldFlag,
    WorldUnlock,
    GameplayState,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_world_flag_creation():
    flag = WorldFlag(flag_id="FLAG_BRIDGE_REPAIRED")
    assert flag.flag_id == "FLAG_BRIDGE_REPAIRED"
    assert flag.value is True
    assert flag.is_set is True


def test_world_flag_boolean_and_integer_values():
    f_bool = WorldFlag("FLAG_MET_KING", value=True)
    f_count = WorldFlag("FLAG_CHESTS_OPENED", value=5)
    assert f_bool.value is True
    assert f_count.value == 5


def test_world_unlock_creation():
    unlock = WorldUnlock(
        unlock_id="UNLOCK_FAST_TRAVEL",
        required_flags=["FLAG_MET_CARTOGRAPHER", "FLAG_VISITED_CAPITAL"],
        unlocked_content="MAP_FAST_TRAVEL_NETWORK",
        is_unlocked=False,
    )
    assert unlock.unlock_id == "UNLOCK_FAST_TRAVEL"
    assert len(unlock.required_flags) == 2
    assert unlock.unlocked_content == "MAP_FAST_TRAVEL_NETWORK"
    assert unlock.is_unlocked is False


def test_world_unlock_condition_check():
    unlock = WorldUnlock(
        unlock_id="GATE_LOWER_LEVELS",
        required_flags=["KEY_COLLECTED", "BOSS_DEFEATED"],
        unlocked_content="DUNGEON_FLOOR_2",
    )
    current_flags = {"KEY_COLLECTED": True, "BOSS_DEFEATED": True}
    can_unlock = all(current_flags.get(f, False) for f in unlock.required_flags)
    assert can_unlock is True

    current_flags_incomplete = {"KEY_COLLECTED": True, "BOSS_DEFEATED": False}
    can_unlock_incomplete = all(current_flags_incomplete.get(f, False) for f in unlock.required_flags)
    assert can_unlock_incomplete is False


def test_world_flags_in_gameplay_state():
    state = GameplayState("SIM_FLAGS")
    state.world_flags["TUTORIAL_COMPLETED"] = True
    state.world_flags["DIFFICULTY"] = "HARD"
    assert state.world_flags["TUTORIAL_COMPLETED"] is True
    assert state.world_flags["DIFFICULTY"] == "HARD"


def test_world_unlock_activation():
    state = GameplayState("SIM_FLAGS")
    unlock = WorldUnlock("UNLOCK_SECRET_ARENA", ["ARENA_TOKEN"], "SECRET_ARENA")
    state.world_unlocks[unlock.unlock_id] = unlock

    assert not state.world_unlocks["UNLOCK_SECRET_ARENA"].is_unlocked
    # Player obtains token
    state.world_flags["ARENA_TOKEN"] = True
    if all(state.world_flags.get(rf, False) for rf in unlock.required_flags):
        unlock.is_unlocked = True

    assert state.world_unlocks["UNLOCK_SECRET_ARENA"].is_unlocked


def test_world_flag_serialization_in_savestate():
    state = GameplayState("SIM_FLAGS")
    state.world_flags["CHAPTER_1_DONE"] = True
    state.world_flags["FACTION_ALLIANCE"] = "ELVES"

    saved = UniversalGameplayFabricator.save_state(state)
    assert "CHAPTER_1_DONE" in saved.flags
    assert saved.flags["CHAPTER_1_DONE"] is True
    assert saved.flags["FACTION_ALLIANCE"] == "ELVES"
