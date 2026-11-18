"""
Tests for Canonical Golden Gameplay Scenarios (UAF-81.58 Sections 185, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import GameplayState
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)
from src.uaf.universal_gameplay.validation.universal_gameplay_validator import (
    UniversalGameplayValidator,
)


def _assert_valid_golden_scenario(state: GameplayState):
    assert isinstance(state, GameplayState)
    assert state.state_id.startswith("SIM_GOLDEN_")
    assert state.gameplay_state_hash is not None
    assert len(state.gameplay_state_hash) == 64
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert report.is_valid, f"Validation failed with: {report.failed_checks}"
    assert report.quality_score >= 90.0


def test_golden_quest_start():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_START)
    _assert_valid_golden_scenario(state)
    assert "Q_START" in state.quests


def test_golden_quest_branch():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_BRANCH)
    _assert_valid_golden_scenario(state)
    assert "Q_PEACE" in state.quests
    assert "Q_WAR" in state.quests


def test_golden_quest_complete():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_COMPLETE)
    _assert_valid_golden_scenario(state)
    assert "Q_WOLF_HUNT" in state.quests


def test_golden_quest_fail():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_FAIL)
    _assert_valid_golden_scenario(state)
    assert "Q_ESCORT" in state.quests


def test_golden_dialogue_branch():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_DIALOGUE_BRANCH)
    _assert_valid_golden_scenario(state)
    assert len(state.dialogues) >= 1


def test_golden_inventory():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_INVENTORY)
    _assert_valid_golden_scenario(state)
    hero = state.entities.get("HERO")
    assert hero is not None
    assert len(hero.inventory.items) >= 1


def test_golden_equipment():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_EQUIPMENT)
    _assert_valid_golden_scenario(state)
    hero = state.entities.get("HERO")
    assert hero is not None


def test_golden_crafting():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_CRAFTING)
    _assert_valid_golden_scenario(state)
    assert len(state.crafting_recipes) >= 1


def test_golden_loot():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_LOOT)
    _assert_valid_golden_scenario(state)
    assert len(state.loot_tables) >= 1


def test_golden_reward():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_REWARD)
    _assert_valid_golden_scenario(state)
    assert "Q_REWARD" in state.quests


def test_golden_merchant():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_MERCHANT)
    _assert_valid_golden_scenario(state)
    assert len(state.merchants) >= 1


def test_golden_faction():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_FACTION)
    _assert_valid_golden_scenario(state)
    assert len(state.factions) >= 1


def test_golden_level_up():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_LEVEL_UP)
    _assert_valid_golden_scenario(state)
    hero = state.entities.get("HERO")
    assert hero is not None


def test_golden_skill_unlock():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_SKILL_UNLOCK)
    _assert_valid_golden_scenario(state)
    assert len(state.skill_trees) >= 1


def test_golden_ability():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_ABILITY)
    _assert_valid_golden_scenario(state)
    assert len(state.abilities) >= 1


def test_golden_status_effect():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_STATUS_EFFECT)
    _assert_valid_golden_scenario(state)
    hero = state.entities.get("HERO")
    assert hero is not None
    assert len(hero.active_effects) >= 1


def test_golden_world_unlock():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_WORLD_UNLOCK)
    _assert_valid_golden_scenario(state)
    assert len(state.world_unlocks) >= 1


def test_golden_save_load():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_SAVE_LOAD)
    _assert_valid_golden_scenario(state)


def test_golden_multiplayer_reconciliation():
    state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_MULTIPLAYER_RECONCILIATION)
    _assert_valid_golden_scenario(state)
    assert "PLAYER_1" in state.entities
    assert "PLAYER_2" in state.entities
