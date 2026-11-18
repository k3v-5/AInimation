"""
End-to-End Integration and Lifecycle Tests for Universal Gameplay System (UAF-81.58 Sections 187, 206-210).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    GameplayState,
    EntityType,
    QuestDefinition,
    QuestObjective,
    ObjectiveType,
    QuestState,
    RewardDefinition,
    ItemDefinition,
    ItemInstance,
    ItemCategory,
    ItemRarity,
    EquipmentSlot,
    Inventory,
    MerchantDefinition,
    CurrencyType,
    SkillTree,
    SkillNode,
    AbilityDefinition,
    StatusEffectInstance,
    EffectType,
    WorldUnlock,
    GameplayCommand,
    GameplayCommandType,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)
from src.uaf.universal_gameplay.validation.universal_gameplay_validator import (
    UniversalGameplayValidator,
)
from src.uaf.universal_gameplay.package.universal_gameplay_package import (
    UniversalGameplayPackager,
)


def test_complete_gameplay_lifecycle_e2e():
    # 1. State Initialization
    state = GameplayState("SIM_E2E_HERO_JOURNEY", seed=4242)

    # 2. Spawn Player
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER, health=100.0, gold=50)
    player.progression.current_level = 1
    player.progression.current_xp = 0
    player.progression.xp_for_next_level = 100
    state.entities[player.entity_id] = player

    # 3. Define Items
    sword = ItemDefinition("SWORD_IRON", "Iron Sword", category=ItemCategory.WEAPON, equipment_slot=EquipmentSlot.MAIN_HAND, value=25)
    potion = ItemDefinition("POTION_HEAL", "Health Potion", category=ItemCategory.CONSUMABLE, value=10, usable=True)
    wolf_pelt = ItemDefinition("WOLF_PELT", "Wolf Pelt", category=ItemCategory.MATERIAL, value=5)
    state.items[sword.item_id] = sword
    state.items[potion.item_id] = potion
    state.items[wolf_pelt.item_id] = wolf_pelt

    # 4. Define Skill Tree
    tree = SkillTree("TREE_WARRIOR", "Warrior Discipline")
    tree.skills["SK_POWER_STRIKE"] = SkillNode("SK_POWER_STRIKE", "Power Strike", max_rank=3)
    state.skill_trees[tree.tree_id] = tree

    # 5. Define Quest
    quest = QuestDefinition(
        quest_id="Q_HUNT_WOLVES",
        title="Forest Threat",
        description="Eliminate the dire wolves harassing timber workers.",
        giver="VILLAGE_ELDER",
        objectives=[
            QuestObjective("OBJ_KILL_WOLVES", "Slay Dire Wolves", ObjectiveType.KILL, "DIRE_WOLF", target_count=3),
        ],
        rewards=RewardDefinition(
            xp=120,  # Enough to level up from lvl 1 (requires 100 XP)
            currency=40,
            items=[("SWORD_IRON", 1)],
        ),
        state=QuestState.AVAILABLE,
    )
    state.quests[quest.quest_id] = quest

    # 6. Define Merchant
    m_inv = Inventory("INV_TRADER", "TRADER_TOM")
    m_inv.items.append(ItemInstance("pot_shop", "POTION_HEAL", 10))
    trader = MerchantDefinition("TRADER_TOM", "Tom's Supplies", inventory=m_inv, buy_multiplier=1.0, sell_multiplier=0.5)
    trader.wallet.add(100, CurrencyType.GOLD)
    state.merchants[trader.merchant_id] = trader

    # 7. Step 1: Accept Quest
    cmd_accept = GameplayCommand("c1", player.entity_id, quest.quest_id, GameplayCommandType.ACCEPT_QUEST, {"quest_id": quest.quest_id})
    res_accept = UniversalGameplayFabricator.execute_command(state, cmd_accept)
    assert res_accept.success
    assert quest.state == QuestState.ACTIVE

    # 8. Step 2: Slay wolves (progress objective)
    cmd_obj = GameplayCommand(
        "c2",
        player.entity_id,
        quest.quest_id,
        GameplayCommandType.COMPLETE_OBJECTIVE,
        {"quest_id": quest.quest_id, "objective_id": "OBJ_KILL_WOLVES", "amount": 3},
    )
    res_obj = UniversalGameplayFabricator.execute_command(state, cmd_obj)
    assert res_obj.success
    assert quest.state == QuestState.COMPLETED

    # 9. Verify Quest Rewards Applied:
    # Level Up: 120 XP -> level 2, 20 XP remainder, 1 skill point
    assert player.progression.current_level == 2
    assert player.progression.current_xp == 20
    assert player.progression.skill_points == 1
    # Gold: 50 initial + 40 reward = 90
    assert player.wallet.get_balance(CurrencyType.GOLD) == 90
    # Reward item added to inventory
    assert any(it.definition_id == "SWORD_IRON" for it in player.inventory.items)

    # 10. Step 3: Spend Skill Point
    cmd_skill = GameplayCommand(
        "c3",
        player.entity_id,
        "SK_POWER_STRIKE",
        GameplayCommandType.LEARN_SKILL,
        {"tree_id": "TREE_WARRIOR", "skill_id": "SK_POWER_STRIKE"},
    )
    res_skill = UniversalGameplayFabricator.execute_command(state, cmd_skill)
    assert res_skill.success
    assert player.progression.skill_points == 0
    assert tree.skills["SK_POWER_STRIKE"].current_rank == 1

    # 11. Step 4: Equip Newly Awarded Sword
    cmd_equip = GameplayCommand(
        "c4",
        player.entity_id,
        "SWORD_IRON",
        GameplayCommandType.EQUIP_ITEM,
        {"item_id": "SWORD_IRON"},
    )
    res_equip = UniversalGameplayFabricator.execute_command(state, cmd_equip)
    assert res_equip.success
    assert player.equipment.slots[EquipmentSlot.MAIN_HAND].definition_id == "SWORD_IRON"

    # 12. Step 5: Trade with Merchant (Buy 2 potions for 20 gold)
    cmd_buy = GameplayCommand(
        "c5",
        player.entity_id,
        trader.merchant_id,
        GameplayCommandType.BUY,
        {"item_id": "POTION_HEAL", "count": 2},
    )
    res_buy = UniversalGameplayFabricator.execute_command(state, cmd_buy)
    assert res_buy.success
    # 90 gold - 20 = 70 gold
    assert player.wallet.get_balance(CurrencyType.GOLD) == 70
    assert any(it.definition_id == "POTION_HEAL" and it.quantity == 2 for it in player.inventory.items)

    # 13. Step 6: World Progression and Flag Setting
    state.world_flags["QUEST_FOREST_THREAT_COMPLETE"] = True
    unlock = WorldUnlock("UNLOCK_DEEP_WOODS", ["QUEST_FOREST_THREAT_COMPLETE"], "MAP_DEEP_WOODS")
    state.world_unlocks[unlock.unlock_id] = unlock
    if all(state.world_flags.get(f, False) for f in unlock.required_flags):
        unlock.is_unlocked = True
    assert unlock.is_unlocked is True

    # 14. Step 7: Advance simulation ticks (combat simulation)
    dot = StatusEffectInstance("bleed_1", "Poison Thorn", EffectType.DAMAGE_OVER_TIME, 5.0, 5.0, tick_interval=1.0, magnitude=5.0)
    player.active_effects.append(dot)
    UniversalGameplayFabricator.advance_simulation_tick(state, dt=1.0)
    assert player.health == 95.0

    # 15. Step 8: Validate Complete State
    val_report = UniversalGameplayValidator.validate_gameplay_state(state, export_path="/Game/Gameplay/States/Journey")
    assert val_report.is_valid
    assert val_report.quality_score >= 90.0

    # 16. Step 9: Package for Unreal Engine Production
    pkg = UniversalGameplayPackager.package_gameplay(
        state=state,
        export_path="/Game/Gameplay/Production/HeroJourney",
        author="AutomationEngine",
        version="1.0.0",
    )
    assert pkg.verify_readback()
    assert pkg.canonical_hash is not None
    assert len(pkg.canonical_hash) == 64
    assert pkg.entity_count == 1
    assert pkg.quest_count == 1
    assert pkg.transaction_count == 1  # 1 buy transaction
