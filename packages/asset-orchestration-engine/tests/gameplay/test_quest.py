"""
Tests for Quest & Objective System (UAF-81.58 Sections 15-30, 187).
"""

import pytest
from uaf.universal_gameplay import (
    QuestState,
    ObjectiveType,
    ObjectiveState,
    QuestObjective,
    QuestPrerequisite,
    RewardDefinition,
    QuestDefinition,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
    EntityType,
    UniversalGameplayFabricator,
)


def test_quest_states_enum():
    states = {s.value for s in QuestState}
    expected = {
        "LOCKED",
        "AVAILABLE",
        "OFFERED",
        "ACTIVE",
        "COMPLETED",
        "FAILED",
        "ABANDONED",
        "EXPIRED",
    }
    assert states == expected


def test_objective_types_enum():
    types = {t.value for t in ObjectiveType}
    expected = {
        "KILL",
        "COLLECT",
        "INTERACT",
        "REACH_LOCATION",
        "TALK",
        "ESCORT",
        "SURVIVE",
        "CRAFT",
        "DELIVER",
        "CUSTOM",
    }
    assert types == expected


def test_objective_states_enum():
    states = {s.value for s in ObjectiveState}
    expected = {"INACTIVE", "ACTIVE", "COMPLETED", "FAILED", "OPTIONAL_SKIPPED"}
    assert states == expected


def test_quest_objective_creation_and_completion():
    obj = QuestObjective(
        objective_id="OBJ_SLIME",
        title="Defeat Slimes",
        objective_type=ObjectiveType.KILL,
        target_id="SLIME",
        target_count=5,
        current_count=0,
    )
    assert obj.is_complete() is False
    obj.current_count = 5
    assert obj.is_complete() is True


def test_quest_prerequisite_defaults():
    prereq = QuestPrerequisite(min_level=5, required_quests=["Q_TUTORIAL"])
    assert prereq.min_level == 5
    assert prereq.required_quests == ["Q_TUTORIAL"]
    assert len(prereq.required_flags) == 0


def test_quest_accept_command_success():
    state = GameplayState("SIM_QUEST")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    quest = QuestDefinition(
        quest_id="Q_MAIN_01",
        title="First Steps",
        description="Begin adventure",
        giver="NPC_GUIDE",
        objectives=[QuestObjective("OBJ_1", "Talk", ObjectiveType.TALK, "NPC_GUIDE")],
        state=QuestState.AVAILABLE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand("CMD_Q", "PLAYER", "NPC_GUIDE", GameplayCommandType.ACCEPT_QUEST, {"quest_id": "Q_MAIN_01"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is True
    assert quest.state == QuestState.ACTIVE
    assert quest.objectives[0].state == ObjectiveState.ACTIVE


def test_quest_accept_level_too_low():
    state = GameplayState("SIM_QUEST")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    player.progression.current_level = 1
    state.entities[player.entity_id] = player

    quest = QuestDefinition(
        quest_id="Q_HARD",
        title="Dangerous Cavern",
        description="High level dungeon.",
        giver="CAPTAIN",
        prerequisites=QuestPrerequisite(min_level=10),
        objectives=[QuestObjective("OBJ_HARD", "Survive", ObjectiveType.SURVIVE, "DUNGEON")],
        state=QuestState.AVAILABLE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand("CMD_Q", "PLAYER", "CAPTAIN", GameplayCommandType.ACCEPT_QUEST, {"quest_id": "Q_HARD"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is False
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED
    assert quest.state == QuestState.AVAILABLE


def test_quest_accept_prerequisite_incomplete():
    state = GameplayState("SIM_QUEST")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    q1 = QuestDefinition("Q_CHAPTER_1", "Chapter 1", "", "NPC", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "NPC")], state=QuestState.ACTIVE)
    q2 = QuestDefinition("Q_CHAPTER_2", "Chapter 2", "", "NPC", prerequisites=QuestPrerequisite(required_quests=["Q_CHAPTER_1"]), objectives=[QuestObjective("O2", "", ObjectiveType.TALK, "NPC")], state=QuestState.AVAILABLE)
    state.quests[q1.quest_id] = q1
    state.quests[q2.quest_id] = q2

    cmd = GameplayCommand("CMD_Q", "PLAYER", "NPC", GameplayCommandType.ACCEPT_QUEST, {"quest_id": "Q_CHAPTER_2"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is False
    assert res.failure_code == CommandFailureCode.QUEST_NOT_AVAILABLE


def test_quest_complete_objective_progress():
    state = GameplayState("SIM_QUEST")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    quest = QuestDefinition(
        quest_id="Q_HERBS",
        title="Herb Gathering",
        description="Gather medicinal herbs.",
        giver="HERBALIST",
        objectives=[QuestObjective("OBJ_HERBS", "Collect Herbs", ObjectiveType.COLLECT, "HERB", target_count=5)],
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        "CMD_OBJ",
        "PLAYER",
        "HERBALIST",
        GameplayCommandType.COMPLETE_OBJECTIVE,
        {"quest_id": "Q_HERBS", "objective_id": "OBJ_HERBS", "amount": 2},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is True
    assert quest.objectives[0].current_count == 2
    assert quest.objectives[0].state != ObjectiveState.COMPLETED
    assert quest.state == QuestState.ACTIVE


def test_quest_completion_all_objectives():
    state = GameplayState("SIM_QUEST")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    quest = QuestDefinition(
        quest_id="Q_FINISH",
        title="Defeat Boss",
        description="Final fight.",
        giver="KING",
        objectives=[QuestObjective("OBJ_BOSS", "Defeat Boss", ObjectiveType.KILL, "DRAGON", 1)],
        rewards=RewardDefinition(xp=500, currency=200),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        "CMD_OBJ",
        "PLAYER",
        "KING",
        GameplayCommandType.COMPLETE_OBJECTIVE,
        {"quest_id": "Q_FINISH", "objective_id": "OBJ_BOSS", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is True
    assert quest.objectives[0].state == ObjectiveState.COMPLETED
    assert quest.state == QuestState.COMPLETED
    assert player.wallet.get_balance() == 200
    assert player.progression.current_xp > 0


def test_quest_optional_objective_ignored_for_completion():
    state = GameplayState("SIM_QUEST")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj_req = QuestObjective("OBJ_MANDATORY", "Mandatory task", ObjectiveType.TALK, "NPC", 1)
    obj_opt = QuestObjective("OBJ_OPTIONAL", "Optional secret", ObjectiveType.COLLECT, "SECRET", 1, is_optional=True)

    quest = QuestDefinition(
        quest_id="Q_OPT",
        title="Optional Quest",
        description="",
        giver="NPC",
        objectives=[obj_req, obj_opt],
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        "CMD_M",
        "PLAYER",
        "NPC",
        GameplayCommandType.COMPLETE_OBJECTIVE,
        {"quest_id": "Q_OPT", "objective_id": "OBJ_MANDATORY", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is True
    assert quest.state == QuestState.COMPLETED


def test_quest_rewards_items_grant():
    state = GameplayState("SIM_QUEST")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    quest = QuestDefinition(
        quest_id="Q_ITEM_REWARD",
        title="Relic Hunt",
        description="",
        giver="ARCHEOLOGIST",
        objectives=[QuestObjective("O1", "Find relic", ObjectiveType.COLLECT, "RELIC", 1)],
        rewards=RewardDefinition(items=[("RELIC_SWORD", 1)]),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        "CMD_R",
        "PLAYER",
        "ARCHEOLOGIST",
        GameplayCommandType.COMPLETE_OBJECTIVE,
        {"quest_id": "Q_ITEM_REWARD", "objective_id": "O1", "amount": 1},
    )
    UniversalGameplayFabricator.execute_command(state, cmd)

    assert quest.state == QuestState.COMPLETED
    assert len(player.inventory.items) == 1
    assert player.inventory.items[0].definition_id == "RELIC_SWORD"


def test_quest_abandon_command_success():
    state = GameplayState("SIM_QUEST")
    quest = QuestDefinition("Q_ABANDON", "Boring Quest", "", "GIVER", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "")], state=QuestState.ACTIVE)
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand("CMD_AB", "HERO", "GIVER", GameplayCommandType.ABANDON_QUEST, {"quest_id": "Q_ABANDON"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is True
    assert quest.state == QuestState.ABANDONED


def test_quest_abandon_inactive_rejected():
    state = GameplayState("SIM_QUEST")
    quest = QuestDefinition("Q_NOT_ACTIVE", "", "", "", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "")], state=QuestState.AVAILABLE)
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand("CMD_AB", "HERO", "GIVER", GameplayCommandType.ABANDON_QUEST, {"quest_id": "Q_NOT_ACTIVE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is False
    assert res.failure_code == CommandFailureCode.QUEST_NOT_ACTIVE


def test_quest_failure_transition():
    quest = QuestDefinition("Q_FAIL", "Failing Quest", "", "GIVER", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "")], state=QuestState.ACTIVE)
    assert quest.state == QuestState.ACTIVE

    quest.state = QuestState.FAILED
    assert quest.state == QuestState.FAILED


def test_quest_serialization_to_dict():
    quest = QuestDefinition(
        quest_id="Q_SERIAL",
        title="Serialization Test",
        description="Check dict output",
        giver="SYSTEM",
        objectives=[QuestObjective("O1", "Step 1", ObjectiveType.TALK, "NPC", 1, 1, ObjectiveState.COMPLETED)],
        rewards=RewardDefinition(xp=100, currency=50),
        state=QuestState.COMPLETED,
    )
    d = quest.to_dict()
    assert d["quest_id"] == "Q_SERIAL"
    assert d["title"] == "Serialization Test"
    assert d["state"] == "COMPLETED"
    assert d["reward_xp"] == 100
    assert d["reward_currency"] == 50
    assert len(d["objectives"]) == 1


def test_multiple_active_quests_tracking():
    state = GameplayState("SIM_MULTI_Q")
    q1 = QuestDefinition("Q1", "First", "", "", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "")], state=QuestState.ACTIVE)
    q2 = QuestDefinition("Q2", "Second", "", "", objectives=[QuestObjective("O2", "", ObjectiveType.TALK, "")], state=QuestState.ACTIVE)
    q3 = QuestDefinition("Q3", "Third", "", "", objectives=[QuestObjective("O3", "", ObjectiveType.TALK, "")], state=QuestState.COMPLETED)

    state.quests[q1.quest_id] = q1
    state.quests[q2.quest_id] = q2
    state.quests[q3.quest_id] = q3

    active = [q for q in state.quests.values() if q.state == QuestState.ACTIVE]
    assert len(active) == 2


def test_quest_objective_invalid_target_rejected():
    state = GameplayState("SIM_QUEST")
    quest = QuestDefinition("Q_BAD_OBJ", "", "", "", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "")], state=QuestState.ACTIVE)
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand("CMD_BAD", "HERO", "GIVER", GameplayCommandType.COMPLETE_OBJECTIVE, {"quest_id": "Q_BAD_OBJ", "objective_id": "GHOST_OBJ"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is False
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_quest_accept_unknown_quest():
    state = GameplayState("SIM_QUEST")
    cmd = GameplayCommand("CMD_UNKNOWN", "HERO", "GIVER", GameplayCommandType.ACCEPT_QUEST, {"quest_id": "NON_EXISTENT"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)

    assert res.success is False
    assert res.failure_code == CommandFailureCode.INVALID_TARGET
