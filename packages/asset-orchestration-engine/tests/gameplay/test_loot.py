"""
Tests for Loot Table and Drop Mechanics (UAF-81.58 Sections 106-115, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    LootEntry,
    LootTable,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_loot_entry_model():
    entry = LootEntry(
        item_id="GOLD_COIN",
        weight=2.0,
        min_count=5,
        max_count=20,
        drop_chance=0.8,
    )
    assert entry.item_id == "GOLD_COIN"
    assert entry.weight == 2.0
    assert entry.min_count == 5
    assert entry.max_count == 20
    assert entry.drop_chance == 0.8


def test_loot_table_model():
    table = LootTable(
        table_id="tbl_skeleton",
        entries=[
            LootEntry("BONE", drop_chance=1.0),
            LootEntry("ARROW", min_count=2, max_count=5, drop_chance=0.5),
        ],
        roll_count=2,
    )
    assert table.table_id == "tbl_skeleton"
    assert len(table.entries) == 2
    assert table.roll_count == 2


def test_loot_roll_guaranteed_drop():
    table = LootTable(
        table_id="tbl_chest_guaranteed",
        entries=[
            LootEntry("RUBY_GEM", min_count=1, max_count=1, drop_chance=1.0),
        ],
        roll_count=1,
    )
    loot = UniversalGameplayFabricator.roll_loot(table, seed=12345)
    assert len(loot) == 1
    assert loot[0][0] == "RUBY_GEM"
    assert loot[0][1] == 1


def test_loot_roll_zero_drop_chance():
    table = LootTable(
        table_id="tbl_impossible",
        entries=[
            LootEntry("MYTHIC_SWORD", min_count=1, max_count=1, drop_chance=0.0),
        ],
        roll_count=5,
    )
    loot = UniversalGameplayFabricator.roll_loot(table, seed=999)
    assert len(loot) == 0


def test_loot_roll_deterministic_seed():
    table = LootTable(
        table_id="tbl_dungeon_boss",
        entries=[
            LootEntry("BOSS_SOUL", drop_chance=1.0),
            LootEntry("EPIC_STAFF", drop_chance=0.5),
            LootEntry("GOLD_BAR", min_count=1, max_count=10, drop_chance=0.7),
        ],
        roll_count=3,
    )
    loot_1 = UniversalGameplayFabricator.roll_loot(table, seed=42)
    loot_2 = UniversalGameplayFabricator.roll_loot(table, seed=42)
    assert loot_1 == loot_2


def test_loot_roll_multiple_rolls():
    table = LootTable(
        table_id="tbl_multi_pull",
        entries=[
            LootEntry("COMMON_HERB", drop_chance=1.0),
        ],
        roll_count=4,
    )
    loot = UniversalGameplayFabricator.roll_loot(table, seed=101)
    # Guaranteed drop rolled 4 times
    assert len(loot) == 4
    for item_id, count in loot:
        assert item_id == "COMMON_HERB"


def test_loot_empty_table():
    table = LootTable(table_id="tbl_empty", entries=[])
    loot = UniversalGameplayFabricator.roll_loot(table, seed=555)
    assert loot == []


def test_loot_variable_quantity():
    table = LootTable(
        table_id="tbl_variable",
        entries=[
            LootEntry("ARROW", min_count=10, max_count=20, drop_chance=1.0),
        ],
        roll_count=1,
    )
    loot = UniversalGameplayFabricator.roll_loot(table, seed=77)
    assert len(loot) == 1
    assert loot[0][0] == "ARROW"
    assert 10 <= loot[0][1] <= 20
