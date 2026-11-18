"""
Tests for Equipment and Loadout System (UAF-81.58 Sections 86-95, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    EquipmentLoadout,
    EquipmentSlot,
    ItemDefinition,
    ItemInstance,
    ItemCategory,
    ItemRarity,
    EntityType,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_equipment_loadout_slots():
    loadout = EquipmentLoadout()
    for slot in EquipmentSlot:
        if slot != EquipmentSlot.NONE:
            assert slot in loadout.slots
            assert loadout.slots[slot] is None


def test_equip_weapon_success():
    state = GameplayState("SIM_EQUIP")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    sword = ItemDefinition(
        item_id="SWORD_IRON",
        name="Iron Sword",
        category=ItemCategory.WEAPON,
        equipment_slot=EquipmentSlot.MAIN_HAND,
    )
    state.items[sword.item_id] = sword
    player.inventory.items.append(ItemInstance("inst_s1", "SWORD_IRON", 1))

    cmd = GameplayCommand(
        command_id="cmd_eq",
        source=player.entity_id,
        target="SWORD_IRON",
        command_type=GameplayCommandType.EQUIP_ITEM,
        payload={"item_id": "SWORD_IRON"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert player.equipment.slots[EquipmentSlot.MAIN_HAND] is not None
    assert player.equipment.slots[EquipmentSlot.MAIN_HAND].definition_id == "SWORD_IRON"
    assert len(player.inventory.items) == 0


def test_equip_armor_success():
    state = GameplayState("SIM_EQUIP")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    cuirass = ItemDefinition(
        item_id="PLATE_CHEST",
        name="Plate Armor",
        category=ItemCategory.ARMOR,
        equipment_slot=EquipmentSlot.CHEST,
    )
    state.items[cuirass.item_id] = cuirass
    player.inventory.items.append(ItemInstance("inst_c1", "PLATE_CHEST", 1))

    cmd = GameplayCommand(
        command_id="cmd_eq_armor",
        source=player.entity_id,
        target="PLATE_CHEST",
        command_type=GameplayCommandType.EQUIP_ITEM,
        payload={"item_id": "PLATE_CHEST"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert player.equipment.slots[EquipmentSlot.CHEST] is not None
    assert player.equipment.slots[EquipmentSlot.CHEST].definition_id == "PLATE_CHEST"


def test_equip_swap_existing_item():
    state = GameplayState("SIM_EQUIP")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    s1 = ItemDefinition(item_id="SWORD_1", name="Sword 1", equipment_slot=EquipmentSlot.MAIN_HAND)
    s2 = ItemDefinition(item_id="SWORD_2", name="Sword 2", equipment_slot=EquipmentSlot.MAIN_HAND)
    state.items[s1.item_id] = s1
    state.items[s2.item_id] = s2

    player.equipment.slots[EquipmentSlot.MAIN_HAND] = ItemInstance("inst_old", "SWORD_1", 1)
    player.inventory.items.append(ItemInstance("inst_new", "SWORD_2", 1))

    cmd = GameplayCommand(
        command_id="cmd_swap",
        source=player.entity_id,
        target="SWORD_2",
        command_type=GameplayCommandType.EQUIP_ITEM,
        payload={"item_id": "SWORD_2"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert player.equipment.slots[EquipmentSlot.MAIN_HAND].definition_id == "SWORD_2"
    # Old sword returned to inventory
    assert any(it.definition_id == "SWORD_1" for it in player.inventory.items)


def test_unequip_item_success():
    state = GameplayState("SIM_EQUIP")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    player.equipment.slots[EquipmentSlot.MAIN_HAND] = ItemInstance("inst_eq", "DAGGER", 1)

    cmd = GameplayCommand(
        command_id="cmd_uneq",
        source=player.entity_id,
        target="MAIN_HAND",
        command_type=GameplayCommandType.UNEQUIP_ITEM,
        payload={"slot": "MAIN_HAND"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert player.equipment.slots[EquipmentSlot.MAIN_HAND] is None
    assert any(it.definition_id == "DAGGER" for it in player.inventory.items)


def test_equip_item_not_in_inventory():
    state = GameplayState("SIM_EQUIP")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    item = ItemDefinition(item_id="HELMET", name="Iron Helmet", equipment_slot=EquipmentSlot.HEAD)
    state.items[item.item_id] = item

    cmd = GameplayCommand(
        command_id="cmd_fail_eq",
        source=player.entity_id,
        target="HELMET",
        command_type=GameplayCommandType.EQUIP_ITEM,
        payload={"item_id": "HELMET"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED


def test_equip_non_equippable_item():
    state = GameplayState("SIM_EQUIP")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    potion = ItemDefinition(item_id="POTION", name="Healing Potion", equipment_slot=EquipmentSlot.NONE)
    state.items[potion.item_id] = potion
    player.inventory.items.append(ItemInstance("i_pot", "POTION", 1))

    cmd = GameplayCommand(
        command_id="cmd_fail_none",
        source=player.entity_id,
        target="POTION",
        command_type=GameplayCommandType.EQUIP_ITEM,
        payload={"item_id": "POTION"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_unequip_empty_slot():
    state = GameplayState("SIM_EQUIP")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    cmd = GameplayCommand(
        command_id="cmd_fail_empty",
        source=player.entity_id,
        target="RING",
        command_type=GameplayCommandType.UNEQUIP_ITEM,
        payload={"slot": "RING"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED
