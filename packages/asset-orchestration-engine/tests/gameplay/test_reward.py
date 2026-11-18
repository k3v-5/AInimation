"""
Tests for Reward Definition and Distribution (UAF-81.58 Sections 116-125, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    RewardDefinition,
    QuestDefinition,
    QuestObjective,
    ObjectiveType,
    QuestState,
    EntityType,
    GameplayCommand,
    GameplayCommandType,
    GameplayState,
    CurrencyType,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_reward_definition_defaults():
    reward = RewardDefinition()
    assert reward.xp == 0
    assert reward.currency == 0
    assert reward.items == []
    assert reward.reputation == {}


def test_reward_definition_custom():
    reward = RewardDefinition(
        xp=250,
        currency=100,
        items=[("POTION_HEAL", 3), ("IRON_HELMET", 1)],
        reputation={"FACTION_KNIGHTS": 15.0},
    )
    assert reward.xp == 250
    assert reward.currency == 100
    assert len(reward.items) == 2
    assert reward.reputation["FACTION_KNIGHTS"] == 15.0


def test_reward_xp_granting():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj = QuestObjective("O1", "Kill Goblin", ObjectiveType.KILL, "GOB_1", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_XP",
        title="Goblin Trouble",
        description="",
        giver="NPC",
        objectives=[obj],
        rewards=RewardDefinition(xp=60),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_kill",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert quest.state == QuestState.COMPLETED
    assert player.progression.current_xp == 60


def test_reward_currency_granting():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj = QuestObjective("O1", "Find Chest", ObjectiveType.INTERACT, "CHEST", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_GOLD",
        title="Hidden Cache",
        description="",
        giver="NPC",
        objectives=[obj],
        rewards=RewardDefinition(currency=150),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_chest",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert player.wallet.get_balance(CurrencyType.GOLD) == 150


def test_reward_items_granting():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj = QuestObjective("O1", "Talk to Guard", ObjectiveType.TALK, "GUARD", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_ITEM",
        title="Delivery",
        description="",
        giver="NPC",
        objectives=[obj],
        rewards=RewardDefinition(items=[("SWORD_IRON", 1)]),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_talk",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert len(player.inventory.items) == 1
    assert player.inventory.items[0].definition_id == "SWORD_IRON"


def test_reward_combined():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj = QuestObjective("O1", "Save Villager", ObjectiveType.INTERACT, "VILLAGER", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_ALL",
        title="Rescue Mission",
        description="",
        giver="NPC",
        objectives=[obj],
        rewards=RewardDefinition(xp=50, currency=75, items=[("HEALING_POTION", 2)]),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_rescue",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert player.progression.current_xp == 50
    assert player.wallet.get_balance(CurrencyType.GOLD) == 75
    assert any(it.definition_id == "HEALING_POTION" for it in player.inventory.items)


def test_reward_level_up_trigger():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    # XP for next level is 100
    state.entities[player.entity_id] = player

    obj = QuestObjective("O1", "Defeat Dragon", ObjectiveType.KILL, "DRAGON", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_DRAGON",
        title="Dragon Slayer",
        description="",
        giver="NPC",
        objectives=[obj],
        rewards=RewardDefinition(xp=150),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_dragon",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert player.progression.current_level == 2
    assert player.progression.current_xp == 50  # 150 - 100
    assert player.progression.skill_points == 1


def test_reward_multiple_items():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj = QuestObjective("O1", "Loot Vault", ObjectiveType.INTERACT, "VAULT", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_VAULT",
        title="Heist",
        description="",
        giver="NPC",
        objectives=[obj],
        rewards=RewardDefinition(items=[("DIAMOND", 5), ("RUBY", 3), ("EMERALD", 2)]),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_vault",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert len(player.inventory.items) == 3


def test_reward_no_grant_if_not_all_objectives_complete():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj1 = QuestObjective("O1", "Objective 1", ObjectiveType.INTERACT, "T1", target_count=1)
    obj2 = QuestObjective("O2", "Objective 2", ObjectiveType.INTERACT, "T2", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_TWO_STEP",
        title="Two Steps",
        description="",
        giver="NPC",
        objectives=[obj1, obj2],
        rewards=RewardDefinition(xp=100, currency=50),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_step1",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert quest.state == QuestState.ACTIVE
    # Rewards NOT yet granted
    assert player.progression.current_xp == 0
    assert player.wallet.get_balance(CurrencyType.GOLD) == 0


def test_reward_zero_rewards():
    state = GameplayState("SIM_REWARD")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    obj = QuestObjective("O1", "Objective", ObjectiveType.INTERACT, "T1", target_count=1)
    quest = QuestDefinition(
        quest_id="Q_ZERO",
        title="Zero Quest",
        description="",
        giver="NPC",
        objectives=[obj],
        rewards=RewardDefinition(),
        state=QuestState.ACTIVE,
    )
    state.quests[quest.quest_id] = quest

    cmd = GameplayCommand(
        command_id="cmd_zero",
        source=player.entity_id,
        target=quest.quest_id,
        command_type=GameplayCommandType.COMPLETE_OBJECTIVE,
        payload={"quest_id": quest.quest_id, "objective_id": "O1", "amount": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert quest.state == QuestState.COMPLETED
    assert player.progression.current_xp == 0
