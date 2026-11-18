"""
UAF-81.93: Dynamic Economy, Weapon Affixes & Procedural Loot Fabric
Acceptance Test Suite.
Verifies mathematical power budgeting, archetype profiles, elemental synergy matrix,
procedural affix synthesis, weighted loot tables, luck scaling, bad luck protection,
pacing market curves, circular salvage workshop, and Unreal Engine 5 GAS / DataTable export.
"""

import csv
import io
import json
import math
import pytest
from typing import Dict

from uaf.economy import (
    ItemRarity,
    WeaponArchetype,
    AffixType,
    ElementalDamageType,
    ArmorType,
    StatModifierOp,
    LootTier,
    CraftingMaterialType,
    StatModifier,
    WeaponAffix,
    WeaponBaseStats,
    ProceduralWeapon,
    ARCHETYPE_PROFILES,
    PowerBudgetCalculator,
    ELEMENTAL_MULTIPLIER_MATRIX,
    calculate_elemental_multiplier,
    CATALOG_PREFIXES,
    CATALOG_SUFFIXES,
    CATALOG_LEGENDARY_PERKS,
    ProceduralAffixGenerator,
    BASE_RARITY_PROBABILITIES,
    LootTableEntry,
    LootTable,
    create_default_scifi_loot_table,
    LootDropGenerator,
    PACING_MARKET_MULTIPLIERS,
    DynamicMarketManager,
    SalvageWorkshop,
    UE5GASDataTableManifest,
    UE5GASExporter,
)
from uaf.level_design.core.contracts import PacingPhase


class TestPowerBudgetCalculator:
    """Validates mathematical power scaling and budget conservation."""

    def test_power_budget_formula_exact(self):
        # Budget(L, R) = BasePower * (1 + 0.12 * L) * RarityMultiplier(R)
        base_power = ARCHETYPE_PROFILES[WeaponArchetype.ASSAULT_RIFLE]["base_power"]  # 140.0
        level = 10
        rarity = ItemRarity.RARE  # 1.85 multiplier
        expected = 140.0 * (1.0 + 0.12 * 10) * 1.85  # 140 * 2.2 * 1.85 = 569.8
        calculated = PowerBudgetCalculator.calculate_power_budget(level, rarity, WeaponArchetype.ASSAULT_RIFLE)
        assert math.isclose(calculated, expected, abs_tol=1e-2)

    def test_power_budget_conservation_all_archetypes(self):
        # All archetypes should conserve power budget within +- 5% tolerance
        for archetype in WeaponArchetype:
            for rarity in ItemRarity:
                level = 15
                target_budget = PowerBudgetCalculator.calculate_power_budget(level, rarity, archetype)
                stats = PowerBudgetCalculator.generate_base_stats(level, rarity, archetype, seed=12345)
                assert PowerBudgetCalculator.validate_power_budget(stats, target_budget, tolerance=0.05), (
                    f"Archetype {archetype} rarity {rarity} DPS {stats.base_dps} deviated >5% from target {target_budget}"
                )

    def test_stat_generation_determinism(self):
        stats1 = PowerBudgetCalculator.generate_base_stats(5, ItemRarity.EPIC, WeaponArchetype.PISTOL, seed=42)
        stats2 = PowerBudgetCalculator.generate_base_stats(5, ItemRarity.EPIC, WeaponArchetype.PISTOL, seed=42)
        assert stats1.damage_per_shot == stats2.damage_per_shot
        assert stats1.rounds_per_second == stats2.rounds_per_second
        assert stats1.magazine_capacity == stats2.magazine_capacity
        assert stats1.reload_seconds == stats2.reload_seconds


class TestElementalSynergies:
    """Verifies the combat damage mitigation and vulnerability matrix."""

    def test_elemental_multipliers(self):
        # Shock vs Energy Shield is +120% (2.2x)
        assert calculate_elemental_multiplier(ElementalDamageType.SHOCK, ArmorType.ENERGY_SHIELD) == 2.20
        # Corrosive vs Plated Armor is +100% (2.0x)
        assert calculate_elemental_multiplier(ElementalDamageType.CORROSIVE, ArmorType.PLATED_ARMOR) == 2.00
        # Incendiary vs Flesh is +75% (1.75x)
        assert calculate_elemental_multiplier(ElementalDamageType.INCENDIARY, ArmorType.UNARMORED_FLESH) == 1.75
        # Void penetrates all defenses at 1.30x
        for armor in ArmorType:
            assert calculate_elemental_multiplier(ElementalDamageType.VOID, armor) == 1.30
        # Kinetic has penalty vs Plated Armor (0.65x)
        assert calculate_elemental_multiplier(ElementalDamageType.KINETIC, ArmorType.PLATED_ARMOR) == 0.65


class TestAffixesAndSynthesis:
    """Tests procedural affix selection, quotas, naming and GAS tags."""

    def test_rarity_affix_quotas(self):
        # Common: 0 affixes
        c_wpn = ProceduralAffixGenerator.generate_weapon(seed=1, level=1, rarity=ItemRarity.COMMON, archetype=WeaponArchetype.PISTOL)
        assert len(c_wpn.prefixes) == 0
        assert len(c_wpn.suffixes) == 0
        assert c_wpn.legendary_perk is None
        assert c_wpn.total_affixes_count == 0

        # Uncommon: 1 prefix, 0 suffixes
        u_wpn = ProceduralAffixGenerator.generate_weapon(seed=2, level=5, rarity=ItemRarity.UNCOMMON, archetype=WeaponArchetype.SHOTGUN)
        assert len(u_wpn.prefixes) == 1
        assert len(u_wpn.suffixes) == 0
        assert u_wpn.legendary_perk is None
        assert u_wpn.total_affixes_count == 1

        # Rare: 1 prefix, 1 suffix
        r_wpn = ProceduralAffixGenerator.generate_weapon(seed=3, level=10, rarity=ItemRarity.RARE, archetype=WeaponArchetype.ENERGY_SMG)
        assert len(r_wpn.prefixes) == 1
        assert len(r_wpn.suffixes) == 1
        assert r_wpn.legendary_perk is None
        assert r_wpn.total_affixes_count == 2

        # Epic: 2 prefixes, 1 suffix
        e_wpn = ProceduralAffixGenerator.generate_weapon(seed=4, level=20, rarity=ItemRarity.EPIC, archetype=WeaponArchetype.ASSAULT_RIFLE)
        assert len(e_wpn.prefixes) == 2
        assert len(e_wpn.suffixes) == 1
        assert e_wpn.legendary_perk is None
        assert e_wpn.total_affixes_count == 3

        # Legendary: 2 prefixes, 2 suffixes, 1 Legendary Perk
        l_wpn = ProceduralAffixGenerator.generate_weapon(seed=5, level=30, rarity=ItemRarity.LEGENDARY, archetype=WeaponArchetype.HEAVY_CANNON)
        assert len(l_wpn.prefixes) == 2
        assert len(l_wpn.suffixes) == 2
        assert l_wpn.legendary_perk is not None
        assert l_wpn.total_affixes_count == 5

    def test_stat_modifier_application(self):
        base = WeaponBaseStats(
            damage_per_shot=100.0,
            rounds_per_second=5.0,
            magazine_capacity=20,
            reload_seconds=2.0,
            accuracy_spread_deg=3.0,
            recoil_pitch_deg=2.0,
            effective_range_m=50.0,
            mass_kg=4.0,
        )
        mods = [
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.25),
            StatModifier(stat_name="magazine_capacity", operation=StatModifierOp.ADD_FLAT, magnitude=10),
            StatModifier(stat_name="reload_seconds", operation=StatModifierOp.OVERRIDE, magnitude=1.5),
        ]
        calc = ProceduralAffixGenerator.apply_stat_modifiers(base, mods)
        assert math.isclose(calc.damage_per_shot, 125.0, abs_tol=1e-2)
        assert calc.magazine_capacity == 30
        assert math.isclose(calc.reload_seconds, 1.5, abs_tol=1e-2)

    def test_procedural_naming_and_tags(self):
        wpn = ProceduralAffixGenerator.generate_weapon(
            seed=777,
            level=12,
            rarity=ItemRarity.RARE,
            archetype=WeaponArchetype.PLASMA_BLASTER,
            force_element=ElementalDamageType.INCENDIARY,
        )
        assert "Plasma Blaster" in wpn.name
        assert wpn.elemental_type == ElementalDamageType.INCENDIARY
        assert any("Damage.Type.Incendiary" in tag for tag in wpn.gameplay_tags)
        assert "Item.Rarity.RARE" in wpn.gameplay_tags


class TestLootTablesAndDrops:
    """Tests drop distribution, luck scaling, and bad luck protection."""

    def test_loot_table_selection(self):
        table = create_default_scifi_loot_table(LootTier.TIER_1_STANDARD)
        import random
        rng = random.Random(42)
        archetypes_sampled = {table.select_archetype(10, rng) for _ in range(50)}
        # Should sample multiple diverse archetypes
        assert len(archetypes_sampled) >= 4

    def test_luck_scaling_shifts_rarity_probabilities(self):
        gen = LootDropGenerator(bad_luck_protection=False)
        probs_no_luck = gen.compute_rarity_probabilities(LootTier.TIER_3_CHEST, luck_score=0.0)
        probs_high_luck = gen.compute_rarity_probabilities(LootTier.TIER_3_CHEST, luck_score=100.0)

        # High luck must increase Rare, Epic and Legendary share
        assert probs_high_luck[ItemRarity.LEGENDARY] > probs_no_luck[ItemRarity.LEGENDARY]
        assert probs_high_luck[ItemRarity.EPIC] > probs_no_luck[ItemRarity.EPIC]
        # Common share should decrease
        assert probs_high_luck[ItemRarity.COMMON] < probs_no_luck[ItemRarity.COMMON]

    def test_bad_luck_protection_escalation(self):
        gen = LootDropGenerator(bad_luck_protection=True)
        # Simulate 14 rolls with no epic
        gen.rolls_since_last_epic = 14
        p_base = gen.compute_rarity_probabilities(LootTier.TIER_1_STANDARD)[ItemRarity.EPIC]

        # Roll 15 without epic
        gen.rolls_since_last_epic = 15
        p_pity1 = gen.compute_rarity_probabilities(LootTier.TIER_1_STANDARD)[ItemRarity.EPIC]
        assert p_pity1 > p_base

        # Roll 20 without epic
        gen.rolls_since_last_epic = 20
        p_pity2 = gen.compute_rarity_probabilities(LootTier.TIER_1_STANDARD)[ItemRarity.EPIC]
        assert p_pity2 > p_pity1

    def test_boss_guaranteed_drop(self):
        gen = LootDropGenerator()
        boss_wpn = gen.generate_boss_guaranteed_drop(player_level=25, seed=999, min_rarity=ItemRarity.EPIC)
        assert boss_wpn.rarity in (ItemRarity.EPIC, ItemRarity.LEGENDARY)
        assert boss_wpn.level == 25


class TestDynamicPacingMarketAndSalvage:
    """Tests market pricing fluctuations with PacingPhase and salvage workshop."""

    def test_market_prices_across_pacing_phases(self):
        market = DynamicMarketManager()
        wpn = ProceduralAffixGenerator.generate_weapon(seed=10, level=10, rarity=ItemRarity.RARE, archetype=WeaponArchetype.ASSAULT_RIFLE)

        calm_buy = market.calculate_buy_price(wpn, PacingPhase.CALM)
        buildup_buy = market.calculate_buy_price(wpn, PacingPhase.BUILDUP)
        peak_buy = market.calculate_buy_price(wpn, PacingPhase.PEAK)
        sustained_buy = market.calculate_buy_price(wpn, PacingPhase.SUSTAINED_PEAK)
        cooldown_buy = market.calculate_buy_price(wpn, PacingPhase.COOLDOWN)

        # Calm < Buildup < Peak < Sustained Peak
        assert calm_buy < buildup_buy < peak_buy < sustained_buy
        # Cooldown is discount phase (< Calm)
        assert cooldown_buy < calm_buy

    def test_salvage_weapon_yield(self):
        # Common weapon yields only scrap and no exotic cores
        common_wpn = ProceduralAffixGenerator.generate_weapon(seed=1, level=5, rarity=ItemRarity.COMMON, archetype=WeaponArchetype.PISTOL)
        yield_c = SalvageWorkshop.salvage_weapon(common_wpn)
        assert CraftingMaterialType.SCRAP_METAL in yield_c
        assert yield_c.get(CraftingMaterialType.QUANTUM_CORE, 0) == 0

        # Legendary weapon yields Quantum Core
        leg_wpn = ProceduralAffixGenerator.generate_weapon(seed=2, level=30, rarity=ItemRarity.LEGENDARY, archetype=WeaponArchetype.HEAVY_CANNON)
        yield_l = SalvageWorkshop.salvage_weapon(leg_wpn)
        assert yield_l[CraftingMaterialType.QUANTUM_CORE] == 1
        assert yield_l[CraftingMaterialType.ENERGY_CELL] > 0

    def test_reforge_affix_replacement(self):
        wpn = ProceduralAffixGenerator.generate_weapon(seed=50, level=15, rarity=ItemRarity.RARE, archetype=WeaponArchetype.SNIPER_RIFLE)
        assert len(wpn.prefixes) == 1
        target_pfx = wpn.prefixes[0]

        reforged = SalvageWorkshop.reforge_affix(wpn, affix_to_replace_id=target_pfx.affix_id, seed=123)
        assert reforged.prefixes[0].affix_id != target_pfx.affix_id
        # Suffix must remain identical
        assert reforged.suffixes[0].affix_id == wpn.suffixes[0].affix_id


class TestUE5GASExporter:
    """Validates CSV formatting, GAS JSON schemas, and ingestion scripts."""

    def test_export_weapons_csv(self):
        weapons = [
            ProceduralAffixGenerator.generate_weapon(seed=i, level=i + 5, rarity=ItemRarity.RARE, archetype=WeaponArchetype.PISTOL)
            for i in range(3)
        ]
        exporter = UE5GASExporter()
        csv_str = exporter.export_weapons_to_csv(weapons)

        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) == 3
        assert rows[0]["---"] == weapons[0].item_id
        assert rows[0]["Archetype"] == "PISTOL"
        assert float(rows[0]["DPS"]) > 0

    def test_export_affixes_csv(self):
        exporter = UE5GASExporter()
        csv_str = exporter.export_affixes_to_csv()
        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) >= len(CATALOG_PREFIXES) + len(CATALOG_SUFFIXES)

    def test_gas_manifest_structure(self):
        wpn = ProceduralAffixGenerator.generate_weapon(seed=100, level=10, rarity=ItemRarity.EPIC, archetype=WeaponArchetype.ASSAULT_RIFLE)
        exporter = UE5GASExporter()
        manifest = exporter.build_gas_manifest([wpn])

        assert len(manifest.weapons) == 1
        assert len(manifest.gameplay_effects) == 1
        ge = manifest.gameplay_effects[0]
        assert ge["duration_policy"] == "Infinite"
        assert any(m["attribute"] == "Attributes.Combat.WeaponDamage" for m in ge["modifiers"])
        assert "Weapon.Archetype.ASSAULT_RIFLE" in manifest.gameplay_tags

    def test_editor_ingest_script_generated(self):
        exporter = UE5GASExporter()
        script = exporter.generate_editor_ingest_script()
        assert "run_import" in script
        assert "unreal" in script
