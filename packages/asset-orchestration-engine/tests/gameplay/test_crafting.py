"""
Tests for Crafting and Recipe System (UAF-81.58 Sections 96-105, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    CraftingRecipe,
    RecipeIngredient,
    ItemInstance,
    EntityType,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
    TransactionType,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_crafting_recipe_model():
    recipe = CraftingRecipe(
        recipe_id="rcp_iron_sword",
        name="Iron Sword",
        station="ANVIL",
        ingredients=[
            RecipeIngredient("IRON_INGOT", 3),
            RecipeIngredient("WOOD_STICK", 1),
        ],
        results=[RecipeIngredient("IRON_SWORD", 1)],
        craft_time=2.5,
        unlocked=True,
    )
    assert recipe.recipe_id == "rcp_iron_sword"
    assert recipe.station == "ANVIL"
    assert len(recipe.ingredients) == 2
    assert len(recipe.results) == 1
    assert recipe.craft_time == 2.5
    assert recipe.unlocked is True


def test_craft_single_ingredient_success():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.inventory.items.append(ItemInstance("i_wood", "WOOD_LOG", 4))
    state.entities[player.entity_id] = player

    recipe = CraftingRecipe(
        recipe_id="rcp_planks",
        name="Wood Planks",
        ingredients=[RecipeIngredient("WOOD_LOG", 2)],
        results=[RecipeIngredient("WOOD_PLANK", 4)],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_cr1",
        source=player.entity_id,
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success

    wood_left = sum(it.quantity for it in player.inventory.items if it.definition_id == "WOOD_LOG")
    planks_made = sum(it.quantity for it in player.inventory.items if it.definition_id == "WOOD_PLANK")
    assert wood_left == 2
    assert planks_made == 4


def test_craft_multi_ingredient_success():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.inventory.items.append(ItemInstance("i1", "IRON_INGOT", 5))
    player.inventory.items.append(ItemInstance("i2", "LEATHER_STRIP", 2))
    state.entities[player.entity_id] = player

    recipe = CraftingRecipe(
        recipe_id="rcp_dagger",
        name="Iron Dagger",
        ingredients=[
            RecipeIngredient("IRON_INGOT", 2),
            RecipeIngredient("LEATHER_STRIP", 1),
        ],
        results=[RecipeIngredient("IRON_DAGGER", 1)],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_cr2",
        source=player.entity_id,
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success

    iron = sum(it.quantity for it in player.inventory.items if it.definition_id == "IRON_INGOT")
    leather = sum(it.quantity for it in player.inventory.items if it.definition_id == "LEATHER_STRIP")
    dagger = sum(it.quantity for it in player.inventory.items if it.definition_id == "IRON_DAGGER")
    assert iron == 3
    assert leather == 1
    assert dagger == 1


def test_craft_multiple_results():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.inventory.items.append(ItemInstance("i1", "GOLD_ORE", 1))
    state.entities[player.entity_id] = player

    recipe = CraftingRecipe(
        recipe_id="rcp_smelt_gold",
        name="Refine Gold",
        ingredients=[RecipeIngredient("GOLD_ORE", 1)],
        results=[
            RecipeIngredient("GOLD_INGOT", 1),
            RecipeIngredient("SLAG", 1),
        ],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_cr3",
        source=player.entity_id,
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success

    assert any(it.definition_id == "GOLD_INGOT" for it in player.inventory.items)
    assert any(it.definition_id == "SLAG" for it in player.inventory.items)


def test_craft_missing_ingredient():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    recipe = CraftingRecipe(
        recipe_id="rcp_bow",
        name="Hunting Bow",
        ingredients=[RecipeIngredient("STRING", 3)],
        results=[RecipeIngredient("BOW", 1)],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_cr_fail",
        source=player.entity_id,
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_craft_partial_ingredient():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.inventory.items.append(ItemInstance("i1", "COPPER_ORE", 2))
    state.entities[player.entity_id] = player

    recipe = CraftingRecipe(
        recipe_id="rcp_copper_bar",
        name="Copper Bar",
        ingredients=[RecipeIngredient("COPPER_ORE", 5)],
        results=[RecipeIngredient("COPPER_BAR", 1)],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_cr_partial",
        source=player.entity_id,
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE
    # Ensure items were not consumed
    assert player.inventory.items[0].quantity == 2


def test_craft_unknown_recipe():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    cmd = GameplayCommand(
        command_id="cmd_cr_unknown",
        source=player.entity_id,
        target="rcp_ghost",
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": "rcp_ghost"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_craft_unknown_crafter():
    state = GameplayState("SIM_CRAFT")
    recipe = CraftingRecipe(
        recipe_id="rcp_simple",
        name="Simple",
        ingredients=[],
        results=[],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_cr_ghost",
        source="ghost_entity",
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_COMMAND


def test_craft_transaction_logging():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.inventory.items.append(ItemInstance("i1", "HERB", 2))
    state.entities[player.entity_id] = player

    recipe = CraftingRecipe(
        recipe_id="rcp_potion",
        name="Healing Potion",
        ingredients=[RecipeIngredient("HERB", 2)],
        results=[RecipeIngredient("POTION_HEAL", 1)],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_cr_tx",
        source=player.entity_id,
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success

    assert len(state.transactions) == 1
    tx = state.transactions[0]
    assert tx.transaction_type == TransactionType.CRAFT
    assert tx.source == player.entity_id
    assert tx.item_id == "POTION_HEAL"
    assert tx.item_count == 1


def test_craft_multiple_stacks_consumption():
    state = GameplayState("SIM_CRAFT")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    # 3 stacks of 2 wood = 6 wood total
    player.inventory.items.append(ItemInstance("stk_1", "WOOD", 2))
    player.inventory.items.append(ItemInstance("stk_2", "WOOD", 2))
    player.inventory.items.append(ItemInstance("stk_3", "WOOD", 2))
    state.entities[player.entity_id] = player

    recipe = CraftingRecipe(
        recipe_id="rcp_chair",
        name="Wooden Chair",
        ingredients=[RecipeIngredient("WOOD", 5)],
        results=[RecipeIngredient("CHAIR", 1)],
    )
    state.crafting_recipes[recipe.recipe_id] = recipe

    cmd = GameplayCommand(
        command_id="cmd_chair",
        source=player.entity_id,
        target=recipe.recipe_id,
        command_type=GameplayCommandType.CRAFT,
        payload={"recipe_id": recipe.recipe_id},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success

    # Total remaining wood should be 1
    remaining_wood = sum(it.quantity for it in player.inventory.items if it.definition_id == "WOOD")
    assert remaining_wood == 1
    assert any(it.definition_id == "CHAIR" for it in player.inventory.items)
