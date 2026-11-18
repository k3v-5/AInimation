"""
Tests for Universal Inventory Management (UAF-81.58 Sections 66-75, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    Inventory,
    InventorySlot,
    ItemInstance,
    ItemDefinition,
    ItemCategory,
    ItemRarity,
    EntityType,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
    MerchantDefinition,
    CurrencyType,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_inventory_initialization():
    inv = Inventory(inventory_id="inv_1", owner_id="player_1", max_slots=20, max_weight=50.0)
    assert inv.inventory_id == "inv_1"
    assert inv.owner_id == "player_1"
    assert inv.max_slots == 20
    assert inv.max_weight == 50.0
    assert len(inv.items) == 0
    assert inv.current_weight == 0.0
    assert not inv.is_full()


def test_inventory_add_item():
    inv = Inventory(inventory_id="inv_1", owner_id="player_1")
    item = ItemInstance(instance_id="inst_1", definition_id="potion_heal", quantity=3)
    inv.items.append(item)
    assert len(inv.items) == 1
    assert inv.items[0].definition_id == "potion_heal"
    assert inv.items[0].quantity == 3


def test_inventory_remove_item():
    inv = Inventory(inventory_id="inv_1", owner_id="player_1")
    item1 = ItemInstance(instance_id="i1", definition_id="iron_ore", quantity=5)
    item2 = ItemInstance(instance_id="i2", definition_id="gold_ore", quantity=2)
    inv.items.extend([item1, item2])
    assert len(inv.items) == 2

    inv.items.remove(item1)
    assert len(inv.items) == 1
    assert inv.items[0].definition_id == "gold_ore"


def test_inventory_capacity_limit():
    inv = Inventory(inventory_id="inv_tiny", owner_id="p1", max_slots=2)
    inv.items.append(ItemInstance("i1", "item_a", 1))
    assert not inv.is_full()
    inv.items.append(ItemInstance("i2", "item_b", 1))
    assert inv.is_full()


def test_inventory_is_full_predicate():
    inv = Inventory(inventory_id="inv_1", owner_id="p1", max_slots=3)
    for i in range(3):
        inv.items.append(ItemInstance(f"inst_{i}", f"item_{i}", 1))
    assert inv.is_full()
    assert len(inv.items) == inv.max_slots


def test_inventory_weight_calculation():
    inv = Inventory(inventory_id="inv_1", owner_id="p1", max_weight=100.0)
    inv.items.append(ItemInstance("i1", "ore", quantity=10))
    inv.items.append(ItemInstance("i2", "herb", quantity=5))
    assert inv.current_weight == 15.0


def test_inventory_overburden():
    inv = Inventory(inventory_id="inv_pack", owner_id="p1", max_weight=20.0)
    inv.items.append(ItemInstance("i1", "heavy_stone", quantity=25))
    assert inv.current_weight > inv.max_weight


def test_inventory_multiple_items_of_same_type():
    inv = Inventory(inventory_id="inv_1", owner_id="p1")
    inv.items.append(ItemInstance("i1", "arrow", quantity=50))
    inv.items.append(ItemInstance("i2", "arrow", quantity=50))
    total_arrows = sum(it.quantity for it in inv.items if it.definition_id == "arrow")
    assert total_arrows == 100


def test_inventory_find_item_by_definition():
    inv = Inventory(inventory_id="inv_1", owner_id="p1")
    inv.items.append(ItemInstance("i1", "key_dungeon", quantity=1))
    inv.items.append(ItemInstance("i2", "potion_mana", quantity=4))

    found = next((it for it in inv.items if it.definition_id == "key_dungeon"), None)
    assert found is not None
    assert found.instance_id == "i1"


def test_inventory_empty_check():
    inv = Inventory(inventory_id="inv_empty", owner_id="p1")
    assert len(inv.items) == 0
    assert inv.current_weight == 0.0
    assert not inv.is_full()


def test_inventory_clear():
    inv = Inventory(inventory_id="inv_1", owner_id="p1")
    inv.items.append(ItemInstance("i1", "sword", 1))
    inv.items.append(ItemInstance("i2", "shield", 1))
    assert len(inv.items) == 2
    inv.items.clear()
    assert len(inv.items) == 0


def test_inventory_slot_assignment():
    slot0 = InventorySlot(slot_index=0, item=ItemInstance("i0", "dagger", 1))
    slot1 = InventorySlot(slot_index=1, item=None)
    assert slot0.slot_index == 0
    assert slot0.item is not None
    assert slot1.slot_index == 1
    assert slot1.item is None


def test_inventory_full_rejection_on_buy():
    state = GameplayState("SIM_INV_FULL")
    player = UniversalGameplayFabricator.spawn_entity("PLAYER", EntityType.PLAYER)
    player.inventory.max_slots = 1
    player.inventory.items.append(ItemInstance("dummy", "rock", 1))
    player.wallet.balances[CurrencyType.GOLD] = 1000
    state.entities[player.entity_id] = player

    sword_def = ItemDefinition(item_id="SWORD_EXPENSIVE", name="Gold Sword", value=100)
    state.items[sword_def.item_id] = sword_def
    m_inv = Inventory("INV_SHOP", "SHOP")
    m_inv.items.append(ItemInstance("inst_shop_1", "SWORD_EXPENSIVE", 5))
    merchant = MerchantDefinition("SHOP", "Shop", inventory=m_inv)
    state.merchants[merchant.merchant_id] = merchant

    cmd = GameplayCommand(
        command_id="cmd_buy",
        source=player.entity_id,
        target=merchant.merchant_id,
        command_type=GameplayCommandType.BUY,
        payload={"item_id": "SWORD_EXPENSIVE", "count": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVENTORY_FULL


def test_inventory_spawn_entity_default_inventory():
    entity = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    assert entity.inventory is not None
    assert entity.inventory.inventory_id == "INV_HERO"
    assert entity.inventory.owner_id == "HERO"
    assert entity.inventory.max_slots == 20
    assert len(entity.inventory.items) == 0
