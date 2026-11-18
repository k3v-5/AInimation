"""
UAF-81.93: Procedural Affix Generator, Elemental Synergies & Weapon Synthesizer.
Deterministic generation of prefixes, suffixes, and legendary perks,
along with elemental vulnerability calculation against armor types.
"""

from __future__ import annotations

import copy
import hashlib
import random
from typing import Dict, List, Optional, Set, Tuple

from uaf.economy.core.contracts import (
    AffixType,
    ArmorType,
    ElementalDamageType,
    ItemRarity,
    ProceduralWeapon,
    StatModifier,
    StatModifierOp,
    WeaponAffix,
    WeaponArchetype,
    WeaponBaseStats,
)
from uaf.economy.budget.power_budget import PowerBudgetCalculator


# ---------------------------------------------------------------------------
# Elemental Synergy & Vulnerability Matrix
# ---------------------------------------------------------------------------

ELEMENTAL_MULTIPLIER_MATRIX: Dict[ElementalDamageType, Dict[ArmorType, float]] = {
    ElementalDamageType.KINETIC: {
        ArmorType.UNARMORED_FLESH: 1.00,
        ArmorType.PLATED_ARMOR: 0.65,      # 35% damage reduction from ballistic armor
        ArmorType.ENERGY_SHIELD: 0.85,     # 15% deflected by energy barriers
        ArmorType.CYBERNETIC: 0.90,
    },
    ElementalDamageType.INCENDIARY: {
        ArmorType.UNARMORED_FLESH: 1.75,   # +75% bonus vs organic flesh
        ArmorType.PLATED_ARMOR: 0.75,      # Dissipated by heat-shielded armor
        ArmorType.ENERGY_SHIELD: 0.75,     # Absorbed by force shields
        ArmorType.CYBERNETIC: 1.25,        # Thermal overheating
    },
    ElementalDamageType.CRYO: {
        ArmorType.UNARMORED_FLESH: 1.20,   # Frostbite and cellular damage
        ArmorType.PLATED_ARMOR: 1.10,      # Thermal stress / embrittlement
        ArmorType.ENERGY_SHIELD: 1.00,     # Neutral
        ArmorType.CYBERNETIC: 1.35,        # Lubricant freezing and hydraulic lock
    },
    ElementalDamageType.SHOCK: {
        ArmorType.UNARMORED_FLESH: 1.00,   # Baseline
        ArmorType.PLATED_ARMOR: 0.70,      # Grounded by conductive chassis
        ArmorType.ENERGY_SHIELD: 2.20,     # +120% massive shield overload
        ArmorType.CYBERNETIC: 1.80,        # Electrical short circuit
    },
    ElementalDamageType.CORROSIVE: {
        ArmorType.UNARMORED_FLESH: 1.25,   # Chemical burns
        ArmorType.PLATED_ARMOR: 2.00,      # +100% dissolves heavy plating
        ArmorType.ENERGY_SHIELD: 0.50,     # Dispersed harmlessly by shields
        ArmorType.CYBERNETIC: 1.50,        # Joint degradation and sensor corrosion
    },
    ElementalDamageType.VOID: {
        ArmorType.UNARMORED_FLESH: 1.30,   # Universal spatial distortion
        ArmorType.PLATED_ARMOR: 1.30,      # Ignores physical armor
        ArmorType.ENERGY_SHIELD: 1.30,     # Bypasses shield frequencies
        ArmorType.CYBERNETIC: 1.30,        # Direct quantum decoupling
    },
}


def calculate_elemental_multiplier(
    damage_type: ElementalDamageType,
    armor_type: ArmorType,
) -> float:
    """Returns the damage scaling factor of an element against a target armor type."""
    return ELEMENTAL_MULTIPLIER_MATRIX[damage_type][armor_type]


# ---------------------------------------------------------------------------
# Master Affix Catalog
# ---------------------------------------------------------------------------

CATALOG_PREFIXES: List[WeaponAffix] = [
    WeaponAffix(
        affix_id="pfx_overclocked",
        name="Overclocked",
        affix_type=AffixType.PREFIX,
        stat_modifiers=[
            StatModifier(stat_name="rounds_per_second", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.25, gameplay_tag="Weapon.Mod.FireRate"),
            StatModifier(stat_name="accuracy_spread_deg", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.15, gameplay_tag="Weapon.Mod.Spread"),
        ],
        gameplay_tags=["Weapon.Affix.Prefix.Overclocked"],
        description="+25% Fire Rate, +15% Spread",
    ),
    WeaponAffix(
        affix_id="pfx_high_caliber",
        name="High-Caliber",
        affix_type=AffixType.PREFIX,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.30, gameplay_tag="Weapon.Mod.Damage"),
            StatModifier(stat_name="rounds_per_second", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=-0.15, gameplay_tag="Weapon.Mod.FireRate"),
            StatModifier(stat_name="recoil_pitch_deg", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.20, gameplay_tag="Weapon.Mod.Recoil"),
        ],
        gameplay_tags=["Weapon.Affix.Prefix.HighCaliber"],
        description="+30% Damage, -15% Fire Rate, +20% Recoil",
    ),
    WeaponAffix(
        affix_id="pfx_extended_mag",
        name="Extended",
        affix_type=AffixType.PREFIX,
        stat_modifiers=[
            StatModifier(stat_name="magazine_capacity", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.50, gameplay_tag="Weapon.Mod.Magazine"),
            StatModifier(stat_name="reload_seconds", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.10, gameplay_tag="Weapon.Mod.Reload"),
        ],
        gameplay_tags=["Weapon.Affix.Prefix.ExtendedMag"],
        description="+50% Magazine Capacity, +10% Reload Duration",
    ),
    WeaponAffix(
        affix_id="pfx_hair_trigger",
        name="Hair-Trigger",
        affix_type=AffixType.PREFIX,
        stat_modifiers=[
            StatModifier(stat_name="reload_seconds", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=-0.25, gameplay_tag="Weapon.Mod.Reload"),
            StatModifier(stat_name="rounds_per_second", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.10, gameplay_tag="Weapon.Mod.FireRate"),
        ],
        gameplay_tags=["Weapon.Affix.Prefix.HairTrigger"],
        description="-25% Reload Time, +10% Fire Rate",
    ),
    WeaponAffix(
        affix_id="pfx_precision",
        name="Precision",
        affix_type=AffixType.PREFIX,
        stat_modifiers=[
            StatModifier(stat_name="accuracy_spread_deg", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=-0.40, gameplay_tag="Weapon.Mod.Spread"),
            StatModifier(stat_name="recoil_pitch_deg", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=-0.25, gameplay_tag="Weapon.Mod.Recoil"),
            StatModifier(stat_name="effective_range_m", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.20, gameplay_tag="Weapon.Mod.Range"),
        ],
        gameplay_tags=["Weapon.Affix.Prefix.Precision"],
        description="-40% Spread, -25% Recoil, +20% Effective Range",
    ),
    WeaponAffix(
        affix_id="pfx_lightweight",
        name="Lightweight",
        affix_type=AffixType.PREFIX,
        stat_modifiers=[
            StatModifier(stat_name="mass_kg", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=-0.30, gameplay_tag="Weapon.Mod.Mass"),
            StatModifier(stat_name="reload_seconds", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=-0.15, gameplay_tag="Weapon.Mod.Reload"),
        ],
        gameplay_tags=["Weapon.Affix.Prefix.Lightweight"],
        description="-30% Weapon Mass, -15% Reload Time",
    ),
    WeaponAffix(
        affix_id="pfx_armor_piercing",
        name="Armor-Piercing",
        affix_type=AffixType.PREFIX,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.20, gameplay_tag="Weapon.Mod.Damage"),
        ],
        gameplay_tags=["Weapon.Affix.Prefix.ArmorPiercing"],
        description="+20% Base Damage with enhanced kinetic penetration",
    ),
]

CATALOG_SUFFIXES: List[WeaponAffix] = [
    WeaponAffix(
        affix_id="sfx_inferno",
        name="of the Inferno",
        affix_type=AffixType.SUFFIX,
        elemental_type=ElementalDamageType.INCENDIARY,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.15, gameplay_tag="Damage.Type.Incendiary"),
        ],
        gameplay_tags=["Weapon.Affix.Suffix.Inferno", "Damage.Type.Incendiary"],
        description="Converts weapon damage to Incendiary, +15% Damage",
    ),
    WeaponAffix(
        affix_id="sfx_glacier",
        name="of the Glacier",
        affix_type=AffixType.SUFFIX,
        elemental_type=ElementalDamageType.CRYO,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.10, gameplay_tag="Damage.Type.Cryo"),
        ],
        gameplay_tags=["Weapon.Affix.Suffix.Glacier", "Damage.Type.Cryo", "Effect.CrowdControl.Slow"],
        description="Converts weapon damage to Cryo, applies 35% movement slow",
    ),
    WeaponAffix(
        affix_id="sfx_tempest",
        name="of the Tempest",
        affix_type=AffixType.SUFFIX,
        elemental_type=ElementalDamageType.SHOCK,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.12, gameplay_tag="Damage.Type.Shock"),
        ],
        gameplay_tags=["Weapon.Affix.Suffix.Tempest", "Damage.Type.Shock", "Effect.ShieldOverload"],
        description="Converts weapon damage to Shock, overloads energy barriers",
    ),
    WeaponAffix(
        affix_id="sfx_decay",
        name="of Decay",
        affix_type=AffixType.SUFFIX,
        elemental_type=ElementalDamageType.CORROSIVE,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.15, gameplay_tag="Damage.Type.Corrosive"),
        ],
        gameplay_tags=["Weapon.Affix.Suffix.Decay", "Damage.Type.Corrosive", "Effect.ArmorDegrade"],
        description="Converts weapon damage to Corrosive, melts heavy vehicle plating",
    ),
    WeaponAffix(
        affix_id="sfx_void",
        name="of the Void",
        affix_type=AffixType.SUFFIX,
        elemental_type=ElementalDamageType.VOID,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.20, gameplay_tag="Damage.Type.Void"),
        ],
        gameplay_tags=["Weapon.Affix.Suffix.Void", "Damage.Type.Void", "Effect.PhasePierce"],
        description="Converts weapon damage to Void, deals 30% true damage ignoring resistance",
    ),
    WeaponAffix(
        affix_id="sfx_vampire",
        name="of the Vampire",
        affix_type=AffixType.SUFFIX,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.05, gameplay_tag="Effect.LifeSteal"),
        ],
        gameplay_tags=["Weapon.Affix.Suffix.Vampire", "Effect.LifeSteal"],
        description="Restores 8% of damage dealt as shield energy",
    ),
    WeaponAffix(
        affix_id="sfx_executioner",
        name="of the Executioner",
        affix_type=AffixType.SUFFIX,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.10, gameplay_tag="Weapon.Mod.Crit"),
        ],
        gameplay_tags=["Weapon.Affix.Suffix.Executioner", "Combat.CritBonus"],
        description="+40% Critical strike damage multiplier",
    ),
]

CATALOG_LEGENDARY_PERKS: List[WeaponAffix] = [
    WeaponAffix(
        affix_id="perk_supernova",
        name="Supernova Singularity",
        affix_type=AffixType.LEGENDARY_PERK,
        elemental_type=ElementalDamageType.INCENDIARY,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.20, gameplay_tag="Perk.Supernova"),
        ],
        gameplay_tags=["Weapon.Perk.Supernova", "Ability.OnKill.Explosion"],
        description="Target kills detonate in a solar nova dealing 150% weapon damage in 5m radius",
    ),
    WeaponAffix(
        affix_id="perk_nanite_swarm",
        name="Nanite Matrix Swarm",
        affix_type=AffixType.LEGENDARY_PERK,
        elemental_type=ElementalDamageType.CORROSIVE,
        stat_modifiers=[
            StatModifier(stat_name="rounds_per_second", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.15, gameplay_tag="Perk.NaniteSwarm"),
        ],
        gameplay_tags=["Weapon.Perk.NaniteSwarm", "Ability.ContinuousHits.DroneSpawn"],
        description="Sustained fire spawns autonomous nanite drones seeking nearby enemies",
    ),
    WeaponAffix(
        affix_id="perk_chronos_shift",
        name="Chronos Dilation Core",
        affix_type=AffixType.LEGENDARY_PERK,
        elemental_type=ElementalDamageType.VOID,
        stat_modifiers=[
            StatModifier(stat_name="reload_seconds", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=-0.30, gameplay_tag="Perk.ChronosShift"),
        ],
        gameplay_tags=["Weapon.Perk.ChronosShift", "Ability.OnReload.TimeDilation"],
        description="Reloading after a kill dilates local time by 40% for 3.5 seconds",
    ),
    WeaponAffix(
        affix_id="perk_arc_cascade",
        name="Chain Lightning Conductor",
        affix_type=AffixType.LEGENDARY_PERK,
        elemental_type=ElementalDamageType.SHOCK,
        stat_modifiers=[
            StatModifier(stat_name="damage_per_shot", operation=StatModifierOp.MULTIPLY_PERCENT, magnitude=0.15, gameplay_tag="Perk.ArcCascade"),
        ],
        gameplay_tags=["Weapon.Perk.ArcCascade", "Ability.Impact.ChainLightning"],
        description="Critical hits arc high-voltage lightning to up to 3 nearby targets",
    ),
]


# ---------------------------------------------------------------------------
# Procedural Generator & Synthesizer
# ---------------------------------------------------------------------------

class ProceduralAffixGenerator:
    """
    Synthesizes weapons deterministically by combining power budgets,
    affix catalog entries, elemental conversions, and GAS gameplay tags.
    """

    @classmethod
    def apply_stat_modifiers(
        cls,
        base_stats: WeaponBaseStats,
        modifiers: List[StatModifier],
    ) -> WeaponBaseStats:
        """
        Applies a sequence of StatModifier instances (ADD_FLAT, MULTIPLY_PERCENT, OVERRIDE)
        to produce the final calculated stats.
        """
        stat_dict = base_stats.model_dump()

        # Phase 1: ADD_FLAT and MULTIPLY_PERCENT
        multipliers: Dict[str, float] = {k: 1.0 for k in stat_dict}
        additions: Dict[str, float] = {k: 0.0 for k in stat_dict}
        overrides: Dict[str, float] = {}

        for mod in modifiers:
            s_name = mod.stat_name
            if s_name not in stat_dict:
                continue

            if mod.operation == StatModifierOp.OVERRIDE:
                overrides[s_name] = mod.magnitude
            elif mod.operation == StatModifierOp.MULTIPLY_PERCENT:
                multipliers[s_name] += mod.magnitude
            elif mod.operation == StatModifierOp.ADD_FLAT:
                additions[s_name] += mod.magnitude

        # Resolve
        result_dict: Dict[str, Any] = {}
        for k, v in stat_dict.items():
            if k in overrides:
                result_dict[k] = overrides[k]
            else:
                mult = max(0.05, multipliers[k])
                val = (v + additions[k]) * mult
                if isinstance(v, int):
                    result_dict[k] = max(1, int(round(val)))
                else:
                    result_dict[k] = max(0.01, round(val, 2))

        return WeaponBaseStats(**result_dict)

    @classmethod
    def generate_weapon(
        cls,
        seed: int,
        level: int,
        rarity: ItemRarity,
        archetype: WeaponArchetype,
        force_element: Optional[ElementalDamageType] = None,
    ) -> ProceduralWeapon:
        """
        Deterministically constructs a complete weapon instance conforming to
        power budgets, affix tier limits, and elemental alignments.
        """
        rng = random.Random(seed + level * 777 + hash(archetype) % 9999 + hash(rarity) % 5555)

        # 1. Generate base stats aligned with power budget
        base_stats = PowerBudgetCalculator.generate_base_stats(level, rarity, archetype, seed=seed)

        # 2. Select Affixes based on Rarity Quotas
        num_prefixes = rarity.max_prefixes
        num_suffixes = rarity.max_suffixes

        # Sample unique prefixes
        available_prefixes = [p for p in CATALOG_PREFIXES if not p.allowed_archetypes or archetype in p.allowed_archetypes]
        sampled_prefixes = rng.sample(available_prefixes, min(num_prefixes, len(available_prefixes)))

        # Sample unique suffixes
        available_suffixes = list(CATALOG_SUFFIXES)
        if force_element is not None:
            # Prioritize matching elemental suffix if requested
            match_sfx = [s for s in available_suffixes if s.elemental_type == force_element]
            other_sfx = [s for s in available_suffixes if s.elemental_type != force_element]
            if match_sfx and num_suffixes > 0:
                sampled_suffixes = [rng.choice(match_sfx)]
                remaining_needed = num_suffixes - 1
                if remaining_needed > 0 and other_sfx:
                    sampled_suffixes.extend(rng.sample(other_sfx, min(remaining_needed, len(other_sfx))))
            else:
                sampled_suffixes = rng.sample(available_suffixes, min(num_suffixes, len(available_suffixes)))
        else:
            sampled_suffixes = rng.sample(available_suffixes, min(num_suffixes, len(available_suffixes)))

        # Sample Legendary Perk if tier permits
        legendary_perk: Optional[WeaponAffix] = None
        if rarity.has_legendary_perk:
            legendary_perk = rng.choice(CATALOG_LEGENDARY_PERKS)

        # 3. Determine Active Elemental Affinity
        active_element = ElementalDamageType.KINETIC
        if legendary_perk and legendary_perk.elemental_type != ElementalDamageType.KINETIC:
            active_element = legendary_perk.elemental_type
        else:
            for sfx in sampled_suffixes:
                if sfx.elemental_type != ElementalDamageType.KINETIC:
                    active_element = sfx.elemental_type
                    break
        if force_element is not None:
            active_element = force_element

        # 4. Consolidate All Stat Modifiers
        all_mods: List[StatModifier] = []
        for pfx in sampled_prefixes:
            all_mods.extend(pfx.stat_modifiers)
        for sfx in sampled_suffixes:
            all_mods.extend(sfx.stat_modifiers)
        if legendary_perk:
            all_mods.extend(legendary_perk.stat_modifiers)

        calculated_stats = cls.apply_stat_modifiers(base_stats, all_mods)

        # 5. Synthesize Procedural Name
        name_parts: List[str] = []
        for pfx in sampled_prefixes:
            name_parts.append(pfx.name)

        archetype_clean = archetype.value.replace("_", " ").title()
        name_parts.append(archetype_clean)

        if sampled_suffixes:
            name_parts.append(sampled_suffixes[0].name)
        if legendary_perk:
            name_parts.append(f"[{legendary_perk.name}]")

        procedural_name = " ".join(name_parts)

        # 6. Aggregate GameplayTags
        elem_title = active_element.value.capitalize()
        gameplay_tags: Set[str] = {
            f"Weapon.Archetype.{archetype.value}",
            f"Item.Rarity.{rarity.value}",
            f"Damage.Type.{active_element.value}",
            f"Damage.Type.{elem_title}",
        }
        for pfx in sampled_prefixes:
            gameplay_tags.update(pfx.gameplay_tags)
        for sfx in sampled_suffixes:
            gameplay_tags.update(sfx.gameplay_tags)
        if legendary_perk:
            gameplay_tags.update(legendary_perk.gameplay_tags)

        # 7. Compute Monetary Value and Salvage Yield
        base_cost = 50.0
        monetary_value = int(round(base_cost * ((1.0 + 0.15 * level) ** 1.2) * rarity.multiplier))

        salvage_yield: Dict[Any, int] = {
            "SCRAP_METAL": int(5 + level * 2 * rarity.multiplier),
            "REFINED_ALLOY": int(level * rarity.multiplier) if rarity != ItemRarity.COMMON else 0,
        }
        if rarity in (ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY):
            salvage_yield["NANITE_CIRCUITS"] = int(2 + level)
        if rarity in (ItemRarity.EPIC, ItemRarity.LEGENDARY):
            salvage_yield["ENERGY_CELL"] = int(1 + level // 2)
        if rarity == ItemRarity.LEGENDARY:
            salvage_yield["QUANTUM_CORE"] = 1

        item_id = f"WPN_{archetype.value}_{rarity.value}_{seed:08x}"

        return ProceduralWeapon(
            item_id=item_id,
            name=procedural_name,
            seed=seed,
            level=level,
            rarity=rarity,
            archetype=archetype,
            elemental_type=active_element,
            base_stats=base_stats,
            calculated_stats=calculated_stats,
            prefixes=sampled_prefixes,
            suffixes=sampled_suffixes,
            legendary_perk=legendary_perk,
            monetary_value=monetary_value,
            salvage_yield=salvage_yield,
            gameplay_tags=sorted(list(gameplay_tags)),
        )
