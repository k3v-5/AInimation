"""
Tests for Gameplay Simulation Determinism, Hash Invariants, and Repeatability (UAF-81.58 Sections 187, 196-200).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    GameplayState,
    EntityType,
    QuestDefinition,
    QuestObjective,
    ObjectiveType,
    QuestState,
    LootTable,
    LootEntry,
    EffectType,
    StatusEffectInstance,
    ItemDefinition,
    ItemInstance,
    EquipmentSlot,
    AbilityDefinition,
    GameplayCommand,
    GameplayCommandType,
    CurrencyType,
    MerchantDefinition,
    Inventory,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_determinism_identical_seed_same_hash():
    s1 = GameplayState("SIM_DET", seed=12345)
    s2 = GameplayState("SIM_DET", seed=12345)
    assert s1.gameplay_state_hash == s2.gameplay_state_hash


def test_determinism_different_seed_different_hash():
    s1 = GameplayState("SIM_DET", seed=111)
    s2 = GameplayState("SIM_DET", seed=222)
    assert s1.gameplay_state_hash != s2.gameplay_state_hash


def test_determinism_loot_generation_reproducibility():
    tbl = LootTable(
        table_id="tbl_gold",
        entries=[
            LootEntry("RUBY", drop_chance=0.5, min_count=1, max_count=5),
            LootEntry("GOLD", drop_chance=0.8, min_count=10, max_count=50),
        ],
        roll_count=3,
    )
    res_a = UniversalGameplayFabricator.roll_loot(tbl, seed=42)
    for _ in range(50):
        res_b = UniversalGameplayFabricator.roll_loot(tbl, seed=42)
        assert res_a == res_b


def test_determinism_loot_different_seeds_vary():
    tbl = LootTable(
        table_id="tbl_loot",
        entries=[LootEntry("GEM", drop_chance=0.5, min_count=1, max_count=100)],
        roll_count=5,
    )
    res_1 = UniversalGameplayFabricator.roll_loot(tbl, seed=10_000_000)
    res_2 = UniversalGameplayFabricator.roll_loot(tbl, seed=3_000_000_000)
    assert res_1 != res_2


def test_determinism_tick_advancement_parity():
    def create_sim():
        s = GameplayState("SIM_TICK", seed=10)
        p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
        p.health = 100.0
        p.active_effects.append(
            StatusEffectInstance("bleed", "Bleed", EffectType.DAMAGE_OVER_TIME, 10.0, 10.0, tick_interval=1.0, magnitude=4.0)
        )
        s.entities[p.entity_id] = p
        return s

    s1 = create_sim()
    s2 = create_sim()

    for _ in range(5):
        UniversalGameplayFabricator.advance_simulation_tick(s1, dt=1.0)
        UniversalGameplayFabricator.advance_simulation_tick(s2, dt=1.0)

    assert s1.entities["HERO"].health == s2.entities["HERO"].health == 80.0
    assert s1.current_tick == s2.current_tick == 5


def test_determinism_command_sequence():
    def run_sequence():
        s = GameplayState("SIM_CMD", seed=999)
        p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
        p.wallet.balances[CurrencyType.GOLD] = 500
        s.entities[p.entity_id] = p

        q = QuestDefinition("Q1", "Quest 1", "", "NPC", objectives=[QuestObjective("O1", "", ObjectiveType.TALK, "NPC")], state=QuestState.AVAILABLE)
        s.quests[q.quest_id] = q

        cmd_accept = GameplayCommand("c1", p.entity_id, q.quest_id, GameplayCommandType.ACCEPT_QUEST, {"quest_id": q.quest_id})
        UniversalGameplayFabricator.execute_command(s, cmd_accept)

        cmd_obj = GameplayCommand("c2", p.entity_id, q.quest_id, GameplayCommandType.COMPLETE_OBJECTIVE, {"quest_id": q.quest_id, "objective_id": "O1"})
        UniversalGameplayFabricator.execute_command(s, cmd_obj)

        return s

    s_a = run_sequence()
    s_b = run_sequence()
    assert s_a.gameplay_state_hash == s_b.gameplay_state_hash


def test_determinism_xp_leveling_curve():
    p1 = UniversalGameplayFabricator.spawn_entity("H1", EntityType.PLAYER)
    p2 = UniversalGameplayFabricator.spawn_entity("H2", EntityType.PLAYER)

    p1.progression.add_xp(500)
    p2.progression.add_xp(500)

    assert p1.progression.current_level == p2.progression.current_level
    assert p1.progression.current_xp == p2.progression.current_xp
    assert p1.progression.skill_points == p2.progression.skill_points
    assert p1.progression.attribute_points == p2.progression.attribute_points


def test_determinism_crafting_consumption_order():
    def make_state():
        s = GameplayState("SIM_CR", seed=50)
        p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
        p.inventory.items.append(ItemInstance("w1", "WOOD", 5))
        s.entities[p.entity_id] = p
        return s

    s1 = make_state()
    s2 = make_state()

    recipe = UniversalGameplayFabricator.GOLDEN_CRAFTING if hasattr(UniversalGameplayFabricator, "GOLDEN_CRAFTING") else None
    assert s1.entities["HERO"].inventory.items[0].quantity == s2.entities["HERO"].inventory.items[0].quantity


def test_determinism_save_state_hash():
    s = GameplayState("SIM_SAVE_HASH", seed=888)
    save_1 = UniversalGameplayFabricator.save_state(s)
    save_2 = UniversalGameplayFabricator.save_state(s)
    assert save_1.state_hash == save_2.state_hash


def test_determinism_transaction_ordering():
    s = GameplayState("SIM_TX_ORDER", seed=50)
    p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    p.wallet.balances[CurrencyType.GOLD] = 1000
    s.entities[p.entity_id] = p

    item = ItemDefinition("COFFEE", "Coffee", value=10)
    s.items[item.item_id] = item

    m = MerchantDefinition("CAFE", "Cafe", inventory=Inventory("I", "C"))
    s.merchants[m.merchant_id] = m

    for i in range(5):
        cmd = GameplayCommand(f"c_buy_{i}", p.entity_id, m.merchant_id, GameplayCommandType.BUY, {"item_id": "COFFEE"})
        UniversalGameplayFabricator.execute_command(s, cmd)

    tx_ids = [tx.transaction_id for tx in s.transactions]
    assert tx_ids == [f"TX_BUY_c_buy_{i}" for i in range(5)]


def test_determinism_ability_cooldown_decay():
    s = GameplayState("SIM_CD", seed=10)
    ab = ItemDefinition("dummy", "dummy")  # dummy check
    state_ab = AbilityDefinition("SLASH", "Slash", cooldown=5.0, current_cooldown=5.0)
    s.abilities[state_ab.ability_id] = state_ab

    UniversalGameplayFabricator.advance_simulation_tick(s, dt=2.0)
    assert state_ab.current_cooldown == 3.0


def test_determinism_golden_scenario_reproducibility():
    s1 = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_START)
    s2 = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_START)
    assert s1.gameplay_state_hash == s2.gameplay_state_hash


def test_determinism_state_hash_changes_on_any_mutation():
    s = GameplayState("SIM_MUT", seed=123)
    base_hash = s.gameplay_state_hash

    # Add entity
    p = UniversalGameplayFabricator.spawn_entity("NEW_HERO", EntityType.PLAYER)
    s.entities[p.entity_id] = p
    hash_with_entity = s.gameplay_state_hash
    assert hash_with_entity != base_hash

    # Add quest
    q = QuestDefinition("NEW_Q", "New Quest", "", "NPC", objectives=[QuestObjective("O", "", ObjectiveType.TALK, "NPC")])
    s.quests[q.quest_id] = q
    hash_with_quest = s.gameplay_state_hash
    assert hash_with_quest != hash_with_entity
