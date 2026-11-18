"""
Tests for Negative Conditions, Hard Fails, and Error Handling (UAF-81.58 Sections 187-195).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    GameplayState,
    EntityType,
    QuestDefinition,
    QuestObjective,
    ObjectiveType,
    QuestState,
    QuestPrerequisite,
    DialogueGraph,
    DialogueNode,
    DialogueChoice,
    CurrencyType,
    TransactionRecord,
    TransactionType,
    SkillTree,
    SkillNode,
    ItemDefinition,
    ItemInstance,
    Inventory,
    MerchantDefinition,
    EquipmentSlot,
    AbilityDefinition,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    CraftingRecipe,
    RecipeIngredient,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)
from src.uaf.universal_gameplay.validation.universal_gameplay_validator import (
    UniversalGameplayValidator,
)


# --- 1-13: VALIDATOR HARD FAILS & QUALITY CHECKS ---

def test_validator_hard_fail_windows_drive_c():
    state = GameplayState("SIM_VAL")
    report = UniversalGameplayValidator.validate_gameplay_state(state, export_path="C:/Game/Gameplay/State.json")
    assert not report.is_valid
    assert report.quality_score == 0.0
    assert any("Machine-dependent path detected" in err for err in report.failed_checks)


def test_validator_hard_fail_windows_drive_d():
    state = GameplayState("SIM_VAL")
    report = UniversalGameplayValidator.validate_gameplay_state(state, export_path="D:\\Assets\\Gameplay\\State.json")
    assert not report.is_valid
    assert report.quality_score == 0.0


def test_validator_hard_fail_windows_drive_e():
    state = GameplayState("SIM_VAL")
    report = UniversalGameplayValidator.validate_gameplay_state(state, export_path="E:/Game/Exports/Pack.uasset")
    assert not report.is_valid
    assert report.quality_score == 0.0


def test_validator_hard_fail_entity_machine_id():
    state = GameplayState("SIM_VAL")
    p = UniversalGameplayFabricator.spawn_entity("C:\\Player", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert report.quality_score == 0.0
    assert any("Machine-dependent entity identifier" in err for err in report.failed_checks)


def test_validator_hard_fail_quest_without_objectives():
    state = GameplayState("SIM_VAL")
    q = QuestDefinition("Q_EMPTY", "Empty Quest", "", "NPC", objectives=[])
    state.quests[q.quest_id] = q
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert report.quality_score == 0.0
    assert any("has 0 objectives" in err for err in report.failed_checks)


def test_validator_hard_fail_dialogue_missing_root():
    state = GameplayState("SIM_VAL")
    diag = DialogueGraph("DIAG_CORRUPT", "missing_root_id", {})
    state.dialogues[diag.dialogue_id] = diag
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert any("root node 'missing_root_id' missing" in err for err in report.failed_checks)


def test_validator_hard_fail_dialogue_choice_undefined_target():
    state = GameplayState("SIM_VAL")
    n1 = DialogueNode("n1", "NPC", "Hello")
    n1.choices.append(DialogueChoice("c1", "Bye", target_node_id="phantom_node"))
    diag = DialogueGraph("DIAG_BROKEN", "n1", {"n1": n1})
    state.dialogues[diag.dialogue_id] = diag
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert any("references undefined target 'phantom_node'" in err for err in report.failed_checks)


def test_validator_hard_fail_negative_entity_balance():
    state = GameplayState("SIM_VAL")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.wallet.balances[CurrencyType.GOLD] = -50
    state.entities[p.entity_id] = p
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert any("Negative balance -50" in err for err in report.failed_checks)


def test_validator_hard_fail_negative_merchant_balance():
    state = GameplayState("SIM_VAL")
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    m.wallet.balances[CurrencyType.GOLD] = -100
    state.merchants[m.merchant_id] = m
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert any("Negative balance -100 for merchant" in err for err in report.failed_checks)


def test_validator_hard_fail_duplicate_transaction_ids():
    state = GameplayState("SIM_VAL")
    tx1 = TransactionRecord("TX_DUP", TransactionType.BUY, "P1", "SHOP", 10)
    tx2 = TransactionRecord("TX_DUP", TransactionType.BUY, "P1", "SHOP", 20)
    state.transactions.extend([tx1, tx2])
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert any("Duplicate transaction ID: TX_DUP" in err for err in report.failed_checks)


def test_validator_hard_fail_circular_skill_prerequisites():
    state = GameplayState("SIM_VAL")
    tree = SkillTree("CYCLE_TREE", "Cycle")
    tree.skills["A"] = SkillNode("A", "Node A", prerequisites=["B"])
    tree.skills["B"] = SkillNode("B", "Node B", prerequisites=["A"])
    state.skill_trees[tree.tree_id] = tree
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert not report.is_valid
    assert any("Circular skill prerequisite cycle" in err for err in report.failed_checks)


def test_validator_warning_negative_health():
    state = GameplayState("SIM_VAL")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.health = -10.0
    state.entities[p.entity_id] = p
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert report.is_valid  # Still structurally valid, but scored lower
    assert report.quality_score < 100.0
    assert any("negative health" in w for w in report.warnings)


def test_validator_warning_negative_inventory_quantity():
    state = GameplayState("SIM_VAL")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.inventory.items.append(ItemInstance("bad_item", "ORE", quantity=-5))
    state.entities[p.entity_id] = p
    report = UniversalGameplayValidator.validate_gameplay_state(state)
    assert report.is_valid
    assert report.quality_score < 100.0
    assert any("negative quantity" in w for w in report.warnings)


# --- 14-44: COMMAND FAILURE REJECTIONS ---

def test_fail_accept_quest_unknown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c1", p.entity_id, "GHOST_Q", GameplayCommandType.ACCEPT_QUEST, {"quest_id": "GHOST_Q"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_accept_quest_already_completed():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    q = QuestDefinition("Q_DONE", "Done", "", "NPC", objectives=[QuestObjective("O", "", ObjectiveType.TALK, "NPC")], state=QuestState.COMPLETED)
    state.quests[q.quest_id] = q
    cmd = GameplayCommand("c2", p.entity_id, q.quest_id, GameplayCommandType.ACCEPT_QUEST, {"quest_id": q.quest_id})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.QUEST_NOT_AVAILABLE


def test_fail_accept_quest_level_too_low():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.progression.current_level = 1
    state.entities[p.entity_id] = p
    q = QuestDefinition("Q_HI", "High Level", "", "NPC", prerequisites=QuestPrerequisite(min_level=10), objectives=[QuestObjective("O", "", ObjectiveType.TALK, "NPC")], state=QuestState.AVAILABLE)
    state.quests[q.quest_id] = q
    cmd = GameplayCommand("c3", p.entity_id, q.quest_id, GameplayCommandType.ACCEPT_QUEST, {"quest_id": q.quest_id})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED


def test_fail_complete_objective_quest_unknown():
    state = GameplayState("SIM")
    cmd = GameplayCommand("c4", "HERO", "NO_Q", GameplayCommandType.COMPLETE_OBJECTIVE, {"quest_id": "NO_Q", "objective_id": "O1"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.QUEST_NOT_ACTIVE


def test_fail_complete_objective_quest_not_active():
    state = GameplayState("SIM")
    q = QuestDefinition("Q_LOCKED", "Locked", "", "NPC", state=QuestState.LOCKED)
    state.quests[q.quest_id] = q
    cmd = GameplayCommand("c5", "HERO", q.quest_id, GameplayCommandType.COMPLETE_OBJECTIVE, {"quest_id": q.quest_id, "objective_id": "O1"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.QUEST_NOT_ACTIVE


def test_fail_complete_objective_unknown_objective():
    state = GameplayState("SIM")
    q = QuestDefinition("Q_ACT", "Active", "", "NPC", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "NPC")], state=QuestState.ACTIVE)
    state.quests[q.quest_id] = q
    cmd = GameplayCommand("c6", "HERO", q.quest_id, GameplayCommandType.COMPLETE_OBJECTIVE, {"quest_id": q.quest_id, "objective_id": "O_GHOST"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_abandon_quest_unknown():
    state = GameplayState("SIM")
    cmd = GameplayCommand("c7", "HERO", "Q_NONE", GameplayCommandType.ABANDON_QUEST, {"quest_id": "Q_NONE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.QUEST_NOT_ACTIVE


def test_fail_abandon_quest_not_active():
    state = GameplayState("SIM")
    q = QuestDefinition("Q_COMP", "Comp", "", "NPC", state=QuestState.COMPLETED)
    state.quests[q.quest_id] = q
    cmd = GameplayCommand("c8", "HERO", q.quest_id, GameplayCommandType.ABANDON_QUEST, {"quest_id": q.quest_id})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.QUEST_NOT_ACTIVE


def test_fail_buy_merchant_unknown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c9", p.entity_id, "UNKNOWN_SHOP", GameplayCommandType.BUY, {"item_id": "SWORD"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_buy_item_undefined():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    state.merchants[m.merchant_id] = m
    cmd = GameplayCommand("c10", p.entity_id, m.merchant_id, GameplayCommandType.BUY, {"item_id": "UNDEFINED_ITEM"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_buy_insufficient_gold():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.wallet.balances[CurrencyType.GOLD] = 5
    state.entities[p.entity_id] = p
    item = ItemDefinition("EXPENSIVE_ITEM", "Gold Armor", value=500)
    state.items[item.item_id] = item
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    state.merchants[m.merchant_id] = m
    cmd = GameplayCommand("c11", p.entity_id, m.merchant_id, GameplayCommandType.BUY, {"item_id": "EXPENSIVE_ITEM"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_fail_buy_inventory_full():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.inventory.max_slots = 1
    p.inventory.items.append(ItemInstance("junk", "JUNK", 1))
    p.wallet.balances[CurrencyType.GOLD] = 1000
    state.entities[p.entity_id] = p
    item = ItemDefinition("APPLE", "Apple", value=2)
    state.items[item.item_id] = item
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    state.merchants[m.merchant_id] = m
    cmd = GameplayCommand("c12", p.entity_id, m.merchant_id, GameplayCommandType.BUY, {"item_id": "APPLE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVENTORY_FULL


def test_fail_sell_seller_not_found():
    state = GameplayState("SIM")
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    state.merchants[m.merchant_id] = m
    cmd = GameplayCommand("c13", "GHOST_SELLER", m.merchant_id, GameplayCommandType.SELL, {"item_id": "ORE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_COMMAND


def test_fail_sell_merchant_unknown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c14", p.entity_id, "GHOST_MERCHANT", GameplayCommandType.SELL, {"item_id": "ORE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_sell_item_undefined():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    state.merchants[m.merchant_id] = m
    cmd = GameplayCommand("c15", p.entity_id, m.merchant_id, GameplayCommandType.SELL, {"item_id": "GHOST_ITEM"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_sell_item_not_in_inventory():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    item = ItemDefinition("ORE", "Ore", value=10)
    state.items[item.item_id] = item
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    state.merchants[m.merchant_id] = m
    cmd = GameplayCommand("c16", p.entity_id, m.merchant_id, GameplayCommandType.SELL, {"item_id": "ORE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED


def test_fail_sell_merchant_insufficient_funds():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.inventory.items.append(ItemInstance("i1", "DIAMOND", 1))
    state.entities[p.entity_id] = p
    item = ItemDefinition("DIAMOND", "Diamond", value=1000)
    state.items[item.item_id] = item
    m = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"), sell_multiplier=1.0)
    m.wallet.balances[CurrencyType.GOLD] = 10  # Can't afford 1000
    state.merchants[m.merchant_id] = m
    cmd = GameplayCommand("c17", p.entity_id, m.merchant_id, GameplayCommandType.SELL, {"item_id": "DIAMOND"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_fail_craft_recipe_unknown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c18", p.entity_id, "RECIPE_GHOST", GameplayCommandType.CRAFT, {"recipe_id": "RECIPE_GHOST"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_craft_missing_ingredients():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    recipe = CraftingRecipe("R_SWORD", "Sword", ingredients=[RecipeIngredient("IRON", 5)])
    state.crafting_recipes[recipe.recipe_id] = recipe
    cmd = GameplayCommand("c19", p.entity_id, recipe.recipe_id, GameplayCommandType.CRAFT, {"recipe_id": recipe.recipe_id})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_fail_equip_non_equippable():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.inventory.items.append(ItemInstance("i_bread", "BREAD", 1))
    state.entities[p.entity_id] = p
    item = ItemDefinition("BREAD", "Bread", equipment_slot=EquipmentSlot.NONE)
    state.items[item.item_id] = item
    cmd = GameplayCommand("c20", p.entity_id, item.item_id, GameplayCommandType.EQUIP_ITEM, {"item_id": item.item_id})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_equip_not_in_inventory():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    item = ItemDefinition("ARMOR", "Armor", equipment_slot=EquipmentSlot.CHEST)
    state.items[item.item_id] = item
    cmd = GameplayCommand("c21", p.entity_id, item.item_id, GameplayCommandType.EQUIP_ITEM, {"item_id": item.item_id})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED


def test_fail_unequip_invalid_slot():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c22", p.entity_id, "BAD_SLOT", GameplayCommandType.UNEQUIP_ITEM, {"slot": "NONSENSE_SLOT"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_unequip_empty_slot():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c23", p.entity_id, "CHEST", GameplayCommandType.UNEQUIP_ITEM, {"slot": "CHEST"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED


def test_fail_use_ability_unknown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c24", p.entity_id, "AB_GHOST", GameplayCommandType.USE_ABILITY, {"ability_id": "AB_GHOST"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_use_ability_cooldown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[p.entity_id] = p
    ab = AbilityDefinition("AB_BLAST", "Blast", cooldown=10.0, current_cooldown=5.0)
    state.abilities[ab.ability_id] = ab
    cmd = GameplayCommand("c25", p.entity_id, ab.ability_id, GameplayCommandType.USE_ABILITY, {"ability_id": ab.ability_id})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.COOLDOWN_ACTIVE


def test_fail_learn_skill_tree_unknown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.progression.skill_points = 5
    state.entities[p.entity_id] = p
    cmd = GameplayCommand("c26", p.entity_id, "SKILL", GameplayCommandType.LEARN_SKILL, {"tree_id": "TREE_NONE", "skill_id": "SKILL"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_learn_skill_skill_unknown():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.progression.skill_points = 5
    state.entities[p.entity_id] = p
    tree = SkillTree("TREE", "Tree")
    state.skill_trees[tree.tree_id] = tree
    cmd = GameplayCommand("c27", p.entity_id, "GHOST_SKILL", GameplayCommandType.LEARN_SKILL, {"tree_id": "TREE", "skill_id": "GHOST_SKILL"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_learn_skill_no_points():
    state = GameplayState("SIM")
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.progression.skill_points = 0
    state.entities[p.entity_id] = p
    tree = SkillTree("TREE", "Tree")
    tree.skills["S1"] = SkillNode("S1", "Skill 1")
    state.skill_trees[tree.tree_id] = tree
    cmd = GameplayCommand("c28", p.entity_id, "S1", GameplayCommandType.LEARN_SKILL, {"tree_id": "TREE", "skill_id": "S1"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_fail_talk_dialogue_unknown():
    state = GameplayState("SIM")
    cmd = GameplayCommand("c29", "HERO", "TARGET", GameplayCommandType.TALK, {"dialogue_id": "UNKNOWN_DIAG"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_start_mission_unknown():
    state = GameplayState("SIM")
    cmd = GameplayCommand("c30", "HERO", "MIS_NONE", GameplayCommandType.START_MISSION, {"mission_id": "MIS_NONE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_fail_complete_mission_unknown():
    state = GameplayState("SIM")
    cmd = GameplayCommand("c31", "HERO", "MIS_NONE", GameplayCommandType.COMPLETE_MISSION, {"mission_id": "MIS_NONE"})
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET
