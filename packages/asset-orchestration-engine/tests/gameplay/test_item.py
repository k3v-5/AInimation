"""
Tests for Item Definitions, Modifiers, and Instances (UAF-81.58 Sections 66-85, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    ItemDefinition,
    ItemInstance,
    ItemRarity,
    ItemCategory,
    EquipmentSlot,
    StatType,
    StatModifier,
)


def test_item_definition_creation():
    item = ItemDefinition(
        item_id="sword_steel",
        name="Steel Longsword",
        description="A sturdy blade forged from refined iron.",
        category=ItemCategory.WEAPON,
        rarity=ItemRarity.UNCOMMON,
        max_stack=1,
        weight=2.5,
        value=50,
        equipment_slot=EquipmentSlot.MAIN_HAND,
        usable=False,
    )
    assert item.item_id == "sword_steel"
    assert item.name == "Steel Longsword"
    assert item.category == ItemCategory.WEAPON
    assert item.rarity == ItemRarity.UNCOMMON
    assert item.max_stack == 1
    assert item.weight == 2.5
    assert item.value == 50
    assert item.equipment_slot == EquipmentSlot.MAIN_HAND
    assert not item.usable


def test_item_rarity_enumeration():
    rarities = {r.value for r in ItemRarity}
    expected = {
        "COMMON",
        "UNCOMMON",
        "RARE",
        "EPIC",
        "LEGENDARY",
        "ARTIFACT",
        "UNIQUE",
        "CUSTOM",
    }
    assert rarities == expected


def test_item_category_enumeration():
    categories = {c.value for c in ItemCategory}
    expected = {
        "WEAPON",
        "ARMOR",
        "CONSUMABLE",
        "MATERIAL",
        "QUEST",
        "CURRENCY",
        "AMMO",
        "MISC",
        "CUSTOM",
    }
    assert categories == expected


def test_stat_modifiers_flat():
    mod = StatModifier(stat_type=StatType.DAMAGE, value=15.0, is_percentage=False)
    assert mod.stat_type == StatType.DAMAGE
    assert mod.value == 15.0
    assert not mod.is_percentage


def test_stat_modifiers_percentage():
    mod = StatModifier(stat_type=StatType.CRIT_CHANCE, value=0.05, is_percentage=True)
    assert mod.stat_type == StatType.CRIT_CHANCE
    assert mod.value == 0.05
    assert mod.is_percentage


def test_item_definition_with_multiple_modifiers():
    item = ItemDefinition(
        item_id="armor_dragonscale",
        name="Dragonscale Chestplate",
        category=ItemCategory.ARMOR,
        rarity=ItemRarity.LEGENDARY,
        equipment_slot=EquipmentSlot.CHEST,
        stat_modifiers=[
            StatModifier(StatType.ARMOR, 120.0),
            StatModifier(StatType.HEALTH, 50.0),
            StatModifier(StatType.RESISTANCE, 0.20, is_percentage=True),
        ],
    )
    assert len(item.stat_modifiers) == 3
    assert item.stat_modifiers[0].value == 120.0
    assert item.stat_modifiers[2].is_percentage is True


def test_item_instance_creation_and_fields():
    inst = ItemInstance(
        instance_id="inst_99",
        definition_id="potion_mana",
        quantity=5,
        durability=100.0,
        custom_data={"crafter": "Alchemist Bob"},
    )
    assert inst.instance_id == "inst_99"
    assert inst.definition_id == "potion_mana"
    assert inst.quantity == 5
    assert inst.durability == 100.0
    assert inst.custom_data["crafter"] == "Alchemist Bob"


def test_item_durability_and_repair():
    inst = ItemInstance(instance_id="i1", definition_id="pickaxe_iron", durability=100.0)
    inst.durability -= 35.0
    assert inst.durability == 65.0
    # Repair
    inst.durability = min(100.0, inst.durability + 30.0)
    assert inst.durability == 95.0


def test_item_stacking_limits():
    consumable = ItemDefinition(item_id="apple", name="Apple", max_stack=20)
    weapon = ItemDefinition(item_id="bow", name="Hunting Bow", max_stack=1)
    assert consumable.max_stack == 20
    assert weapon.max_stack == 1


def test_item_instance_custom_data():
    inst = ItemInstance(
        instance_id="relic_01",
        definition_id="ancient_ring",
        custom_data={"socketed_gem": "ruby_flawless", "bonus_fire_dmg": 25},
    )
    assert inst.custom_data["socketed_gem"] == "ruby_flawless"
    assert inst.custom_data["bonus_fire_dmg"] == 25
