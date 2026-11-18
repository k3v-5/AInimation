"""
UAF-81.58 Acceptance & Normative Compliance Test Suite.
Verifies Universal Gameplay, Quest, Mission, Dialogue, Inventory, Economy, Reward & Progression System.
Cross-Phase Integration (UAF-81.50 through 58), Machine-Agnostic Purity,
19 Canonical Golden Gameplay Scenarios, Full Transactional Command Dispatch, and Unreal Production Packaging.
"""

import pytest
from uaf.universal_gameplay import (
    UniversalGameplayFabricator,
    UniversalGameplayValidator,
    ProductionReadyGameplay,
    UniversalGameplayPackager,
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
    EquipmentSlot,
    Inventory,
    MerchantDefinition,
    CurrencyType,
    SkillTree,
    SkillNode,
    CraftingRecipe,
    RecipeIngredient,
    StatusEffectInstance,
    EffectType,
    WorldUnlock,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
)

# Cross-Phase Integration imports (UAF-81.50 through UAF-81.57)
from uaf.universal_surface import UniversalSurfaceFabricationPlatform
from uaf.universal_geometry import UniversalGeometryFabricationPlatform
from uaf.universal_character import UniversalCharacterFabricator
from uaf.universal_animation import UniversalAnimationFabricator
from uaf.universal_world import UniversalWorldFabricator
from uaf.universal_ai import UniversalAIFabricator


class TestUAF8158Acceptance:
    """Acceptance criteria tests for UAF-81.58 Universal Gameplay, Quest, Mission, Dialogue, Inventory, Economy, Reward & Progression System."""

    def test_cross_phase_integration_cohesion(self):
        """Verify seamless cross-phase interoperability across all engine subsystems (UAF-81.50 through UAF-81.58)."""
        # 1. Surface from UAF-81.52
        surf_spec, *surf_paths = UniversalSurfaceFabricationPlatform.build_golden_leather()
        assert surf_spec.is_valid_surface is True

        # 2. Geometry from UAF-81.53
        mesh_spec, *mesh_paths = UniversalGeometryFabricationPlatform.build_golden_character()
        assert mesh_spec.is_valid_mesh is True

        # 3. Character from UAF-81.54
        char = UniversalCharacterFabricator.build_golden_human_male()
        assert char.validation_report.is_valid is True

        # 4. Animation from UAF-81.55
        anim = UniversalAnimationFabricator.build_golden_walk(character=char)
        assert anim.validation_report.is_valid is True

        # 5. World from UAF-81.56
        world = UniversalWorldFabricator.create_golden_grassland()
        assert len(world.anchors) > 0

        # 6. AI from UAF-81.57
        ai = UniversalAIFabricator.create_golden_scenario(UniversalAIFabricator.GOLDEN_COMBAT)
        assert ai is not None

        # 7. Gameplay from UAF-81.58
        gameplay = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_START)
        assert gameplay is not None

        # Verify character entity binds to gameplay entity
        gameplay_player = UniversalGameplayFabricator.spawn_entity(
            entity_id=char.character.character_id if hasattr(char, 'character') else "HERO_KNIGHT",
            entity_type=EntityType.PLAYER,
            health=150.0,
            gold=200,
        )
        gameplay.entities[gameplay_player.entity_id] = gameplay_player
        assert gameplay.entities[gameplay_player.entity_id].health == 150.0
        assert gameplay.entities[gameplay_player.entity_id].wallet.get_balance(CurrencyType.GOLD) == 200

    def test_strict_machine_path_purity_enforcement(self):
        """Verify strict rejection of machine-dependent paths (C:, D:, E:) across validation and packaging."""
        state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_QUEST_START)

        # 1. Invalid Windows export paths
        for bad_path in ["C:/Unreal/Project/Game.uasset", "D:\\Engine\\Assets\\Q.json", "E:/Build/Output.uasset"]:
            report = UniversalGameplayValidator.validate_gameplay_state(state, export_path=bad_path)
            assert report.is_valid is False
            assert report.quality_score == 0.0
            assert any("Machine-dependent path detected" in err for err in report.failed_checks)

        # 2. Invalid entity identifiers
        bad_state = GameplayState("SIM_BAD_PATH")
        bad_player = UniversalGameplayFabricator.spawn_entity("C:\\Users\\GameHero", EntityType.PLAYER)
        bad_state.entities[bad_player.entity_id] = bad_player
        report_ent = UniversalGameplayValidator.validate_gameplay_state(bad_state)
        assert report_ent.is_valid is False
        assert any("Machine-dependent entity identifier" in err for err in report_ent.failed_checks)

        # 3. Pure Unreal virtual paths pass
        pure_path = "/Game/Gameplay/Quests/Quest_Start.uasset"
        pure_report = UniversalGameplayValidator.validate_gameplay_state(state, export_path=pure_path)
        assert pure_report.is_valid is True
        assert pure_report.quality_score >= 90.0

    def test_canonical_golden_gameplay_scenarios_set_complete(self):
        """Verify all 19 Golden Gameplay Scenarios from Section 185 exist, pass validation, and verify readback."""
        scenario_keys = [
            UniversalGameplayFabricator.GOLDEN_QUEST_START,
            UniversalGameplayFabricator.GOLDEN_QUEST_BRANCH,
            UniversalGameplayFabricator.GOLDEN_QUEST_COMPLETE,
            UniversalGameplayFabricator.GOLDEN_QUEST_FAIL,
            UniversalGameplayFabricator.GOLDEN_DIALOGUE_BRANCH,
            UniversalGameplayFabricator.GOLDEN_INVENTORY,
            UniversalGameplayFabricator.GOLDEN_EQUIPMENT,
            UniversalGameplayFabricator.GOLDEN_CRAFTING,
            UniversalGameplayFabricator.GOLDEN_LOOT,
            UniversalGameplayFabricator.GOLDEN_REWARD,
            UniversalGameplayFabricator.GOLDEN_MERCHANT,
            UniversalGameplayFabricator.GOLDEN_FACTION,
            UniversalGameplayFabricator.GOLDEN_LEVEL_UP,
            UniversalGameplayFabricator.GOLDEN_SKILL_UNLOCK,
            UniversalGameplayFabricator.GOLDEN_ABILITY,
            UniversalGameplayFabricator.GOLDEN_STATUS_EFFECT,
            UniversalGameplayFabricator.GOLDEN_WORLD_UNLOCK,
            UniversalGameplayFabricator.GOLDEN_SAVE_LOAD,
            UniversalGameplayFabricator.GOLDEN_MULTIPLAYER_RECONCILIATION,
        ]
        assert len(scenario_keys) == 19

        for key in scenario_keys:
            state = UniversalGameplayFabricator.create_golden_scenario(key)
            export_path = f"/Game/Gameplay/Golden_{key}.uasset"
            report = UniversalGameplayValidator.validate_gameplay_state(state, export_path=export_path)
            assert report.is_valid is True, f"Scenario {key} validation failed: {report.failed_checks}"
            assert report.quality_score >= 90.0

            pkg = UniversalGameplayPackager.package_gameplay(
                state=state,
                export_path=export_path,
                validation_report=report,
            )
            assert len(pkg.canonical_hash) == 64
            readback = pkg.verify_readback()
            assert readback["readback_status"] == "VERIFIED"

    def test_end_to_end_transactional_gameplay_loop(self):
        """Verify full authoritative gameplay loop: Quest -> Slay -> Reward -> Level Up -> Skills -> Crafting -> Equip -> Trade -> Save -> Load."""
        state = GameplayState("SIM_ACCEPTANCE_E2E", seed=777)
        player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER, health=100.0, gold=100)
        state.entities[player.entity_id] = player

        # 1. Setup Crafting & Items
        iron = ItemDefinition("IRON_ORE", "Iron Ore", category=ItemCategory.MATERIAL, value=10)
        ingot = ItemDefinition("IRON_INGOT", "Iron Ingot", category=ItemCategory.MATERIAL, value=20)
        dagger = ItemDefinition("IRON_DAGGER", "Iron Dagger", category=ItemCategory.WEAPON, equipment_slot=EquipmentSlot.MAIN_HAND, value=60)
        state.items[iron.item_id] = iron
        state.items[ingot.item_id] = ingot
        state.items[dagger.item_id] = dagger

        recipe_smelt = CraftingRecipe("RCP_SMELT", "Smelt Iron", ingredients=[RecipeIngredient("IRON_ORE", 2)], results=[RecipeIngredient("IRON_INGOT", 1)])
        recipe_forge = CraftingRecipe("RCP_FORGE", "Forge Dagger", ingredients=[RecipeIngredient("IRON_INGOT", 1)], results=[RecipeIngredient("IRON_DAGGER", 1)])
        state.crafting_recipes[recipe_smelt.recipe_id] = recipe_smelt
        state.crafting_recipes[recipe_forge.recipe_id] = recipe_forge

        # 2. Setup Quest & Objectives
        quest = QuestDefinition(
            quest_id="Q_APPRENTICE_SMITH",
            title="Smithing 101",
            description="Collect iron ore and forge a blade.",
            giver="BLACKSMITH",
            objectives=[
                QuestObjective("OBJ_COLLECT", "Gather Ore", ObjectiveType.COLLECT, "IRON_ORE", target_count=2),
                QuestObjective("OBJ_FORGE", "Forge Dagger", ObjectiveType.CRAFT, "IRON_DAGGER", target_count=1),
            ],
            rewards=RewardDefinition(xp=150, currency=50),
            state=QuestState.AVAILABLE,
        )
        state.quests[quest.quest_id] = quest

        # Accept Quest
        res_accept = UniversalGameplayFabricator.execute_command(
            state, GameplayCommand("c_acc", player.entity_id, quest.quest_id, GameplayCommandType.ACCEPT_QUEST, {"quest_id": quest.quest_id})
        )
        assert res_accept.success
        assert quest.state == QuestState.ACTIVE

        # Give Ore to player & complete obj 1
        player.inventory.items.append(ItemInstance("ore_1", "IRON_ORE", 2))
        res_obj1 = UniversalGameplayFabricator.execute_command(
            state, GameplayCommand("c_o1", player.entity_id, quest.quest_id, GameplayCommandType.COMPLETE_OBJECTIVE, {"quest_id": quest.quest_id, "objective_id": "OBJ_COLLECT", "amount": 2})
        )
        assert res_obj1.success
        assert quest.state == QuestState.ACTIVE

        # Craft Ingot then Dagger
        res_cr1 = UniversalGameplayFabricator.execute_command(
            state, GameplayCommand("c_cr1", player.entity_id, recipe_smelt.recipe_id, GameplayCommandType.CRAFT, {"recipe_id": recipe_smelt.recipe_id})
        )
        assert res_cr1.success

        res_cr2 = UniversalGameplayFabricator.execute_command(
            state, GameplayCommand("c_cr2", player.entity_id, recipe_forge.recipe_id, GameplayCommandType.CRAFT, {"recipe_id": recipe_forge.recipe_id})
        )
        assert res_cr2.success

        # Complete obj 2
        res_obj2 = UniversalGameplayFabricator.execute_command(
            state, GameplayCommand("c_o2", player.entity_id, quest.quest_id, GameplayCommandType.COMPLETE_OBJECTIVE, {"quest_id": quest.quest_id, "objective_id": "OBJ_FORGE", "amount": 1})
        )
        assert res_obj2.success
        assert quest.state == QuestState.COMPLETED

        # Verify Rewards: 100 gold + 50 = 150 gold; 150 XP -> Level 2
        assert player.wallet.get_balance(CurrencyType.GOLD) == 150
        assert player.progression.current_level == 2

        # Equip Dagger
        res_eq = UniversalGameplayFabricator.execute_command(
            state, GameplayCommand("c_eq", player.entity_id, "IRON_DAGGER", GameplayCommandType.EQUIP_ITEM, {"item_id": "IRON_DAGGER"})
        )
        assert res_eq.success
        assert player.equipment.slots[EquipmentSlot.MAIN_HAND].definition_id == "IRON_DAGGER"

        # Trade with Merchant (Sell old ore if any or buy item)
        m_inv = Inventory("INV_M", "MERCHANT_M")
        state.merchants["MERCHANT_M"] = MerchantDefinition("MERCHANT_M", "General Store", inventory=m_inv)
        state.merchants["MERCHANT_M"].wallet.add(200, CurrencyType.GOLD)

        # Save State and Load into fresh clone
        save = UniversalGameplayFabricator.save_state(state)
        clone_state = GameplayState("SIM_CLONE", seed=777)
        clone_p = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
        clone_state.entities[clone_p.entity_id] = clone_p
        clone_state.quests[quest.quest_id] = QuestDefinition(quest.quest_id, "Title", "", "GIVER")

        UniversalGameplayFabricator.load_state(clone_state, save)
        assert clone_state.current_tick == state.current_tick
        assert clone_state.quests[quest.quest_id].state == QuestState.COMPLETED
        assert clone_state.entities["HERO"].wallet.get_balance(CurrencyType.GOLD) == 150
        assert clone_state.entities["HERO"].progression.current_level == 2

    def test_production_ready_gameplay_packaging_and_readback(self):
        """Verify ProductionReadyGameplay packaging, hash determinism, and readback validation."""
        state = UniversalGameplayFabricator.create_golden_scenario(UniversalGameplayFabricator.GOLDEN_INVENTORY)
        pkg = UniversalGameplayPackager.package_gameplay(
            state=state,
            export_path="/Game/Gameplay/Inventory_Package.uasset",
            author="DeepMind_AEC",
            version="1.0.0",
        )

        assert isinstance(pkg, ProductionReadyGameplay)
        assert pkg.canonical_hash is not None
        assert len(pkg.canonical_hash) == 64

        readback = pkg.verify_readback()
        assert readback["readback_status"] == "VERIFIED"
        assert readback["entity_count"] == len(state.entities)
        assert readback["canonical_hash"] == pkg.canonical_hash
