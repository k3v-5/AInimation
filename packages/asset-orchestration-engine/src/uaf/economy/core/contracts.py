"""
UAF-81.93: Core Contracts, Enums & Models for Procedural Economy & Loot Fabric.
Strict data models, rarity multipliers, archetype specs, elemental matrices,
and GAS (Gameplay Ability System) tag integrations.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ItemRarity(str, Enum):
    """Item rarity tier with power scaling multipliers and affix quotas."""
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"

    @property
    def multiplier(self) -> float:
        """Deterministic power budget multiplier."""
        return {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.35,
            ItemRarity.RARE: 1.85,
            ItemRarity.EPIC: 2.60,
            ItemRarity.LEGENDARY: 4.0,
        }[self]

    @property
    def max_prefixes(self) -> int:
        """Maximum allowed prefixes for this tier."""
        return {
            ItemRarity.COMMON: 0,
            ItemRarity.UNCOMMON: 1,
            ItemRarity.RARE: 1,
            ItemRarity.EPIC: 2,
            ItemRarity.LEGENDARY: 2,
        }[self]

    @property
    def max_suffixes(self) -> int:
        """Maximum allowed suffixes for this tier."""
        return {
            ItemRarity.COMMON: 0,
            ItemRarity.UNCOMMON: 0,
            ItemRarity.RARE: 1,
            ItemRarity.EPIC: 1,
            ItemRarity.LEGENDARY: 2,
        }[self]

    @property
    def has_legendary_perk(self) -> bool:
        """Whether this tier is eligible for an exclusive Legendary Perk."""
        return self == ItemRarity.LEGENDARY

    @property
    def hex_color(self) -> str:
        """UI hex color for item cards and drop beacons."""
        return {
            ItemRarity.COMMON: "#A0A0A0",      # Gray
            ItemRarity.UNCOMMON: "#30D158",    # Green
            ItemRarity.RARE: "#0A84FF",        # Blue
            ItemRarity.EPIC: "#BF5AF2",        # Purple
            ItemRarity.LEGENDARY: "#FF9F0A",   # Orange / Gold
        }[self]


class WeaponArchetype(str, Enum):
    """Core weapon archetype defining base handling and tactical role."""
    PISTOL = "PISTOL"
    SHOTGUN = "SHOTGUN"
    ASSAULT_RIFLE = "ASSAULT_RIFLE"
    SNIPER_RIFLE = "SNIPER_RIFLE"
    HEAVY_CANNON = "HEAVY_CANNON"
    ENERGY_SMG = "ENERGY_SMG"
    PLASMA_BLASTER = "PLASMA_BLASTER"
    MELEE_BLADE = "MELEE_BLADE"


class AffixType(str, Enum):
    """Categorization of item affix modifiers."""
    PREFIX = "PREFIX"
    SUFFIX = "SUFFIX"
    LEGENDARY_PERK = "LEGENDARY_PERK"


class ElementalDamageType(str, Enum):
    """Elemental affinities and damage types."""
    KINETIC = "KINETIC"
    INCENDIARY = "INCENDIARY"
    CRYO = "CRYO"
    SHOCK = "SHOCK"
    CORROSIVE = "CORROSIVE"
    VOID = "VOID"


class ArmorType(str, Enum):
    """Target defense type for elemental mitigation/amplification."""
    UNARMORED_FLESH = "UNARMORED_FLESH"
    PLATED_ARMOR = "PLATED_ARMOR"
    ENERGY_SHIELD = "ENERGY_SHIELD"
    CYBERNETIC = "CYBERNETIC"


class StatModifierOp(str, Enum):
    """Operation for stat modifier application (matching GAS standards)."""
    ADD_FLAT = "ADD_FLAT"
    MULTIPLY_PERCENT = "MULTIPLY_PERCENT"
    OVERRIDE = "OVERRIDE"


class LootTier(str, Enum):
    """Loot source category for drop distribution tables."""
    TIER_1_STANDARD = "TIER_1_STANDARD"
    TIER_2_ELITE = "TIER_2_ELITE"
    TIER_3_CHEST = "TIER_3_CHEST"
    TIER_4_BOSS = "TIER_4_BOSS"
    TIER_5_VAULT = "TIER_5_VAULT"


class CraftingMaterialType(str, Enum):
    """Currencies and salvage materials for crafting and reforge."""
    SCRAP_METAL = "SCRAP_METAL"
    REFINED_ALLOY = "REFINED_ALLOY"
    NANITE_CIRCUITS = "NANITE_CIRCUITS"
    ENERGY_CELL = "ENERGY_CELL"
    QUANTUM_CORE = "QUANTUM_CORE"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class StatModifier(BaseModel):
    """A single atomic modification to a weapon attribute (GAS compatible)."""
    stat_name: str
    operation: StatModifierOp
    magnitude: float
    gameplay_tag: Optional[str] = None


class WeaponAffix(BaseModel):
    """A named prefix, suffix, or legendary perk that alters weapon properties."""
    affix_id: str
    name: str
    affix_type: AffixType
    stat_modifiers: List[StatModifier] = Field(default_factory=list)
    elemental_type: ElementalDamageType = ElementalDamageType.KINETIC
    allowed_archetypes: List[WeaponArchetype] = Field(default_factory=list)
    rarity_tier: ItemRarity = ItemRarity.COMMON
    gameplay_tags: List[str] = Field(default_factory=list)
    description: str = ""


class WeaponBaseStats(BaseModel):
    """Physical and ballistic specifications of a weapon."""
    damage_per_shot: float = Field(gt=0)
    rounds_per_second: float = Field(gt=0)
    magazine_capacity: int = Field(gt=0)
    reload_seconds: float = Field(gt=0)
    accuracy_spread_deg: float = Field(ge=0)
    recoil_pitch_deg: float = Field(ge=0)
    effective_range_m: float = Field(gt=0)
    mass_kg: float = Field(gt=0)

    @property
    def base_dps(self) -> float:
        """Raw unmitigated damage per second."""
        return self.damage_per_shot * self.rounds_per_second

    @property
    def burst_damage(self) -> float:
        """Full magazine damage output."""
        return self.damage_per_shot * self.magazine_capacity


class ProceduralWeapon(BaseModel):
    """Complete procedurally synthesized weapon item definition."""
    item_id: str
    name: str
    seed: int
    level: int = Field(ge=1)
    rarity: ItemRarity
    archetype: WeaponArchetype
    elemental_type: ElementalDamageType = ElementalDamageType.KINETIC

    base_stats: WeaponBaseStats
    calculated_stats: WeaponBaseStats

    prefixes: List[WeaponAffix] = Field(default_factory=list)
    suffixes: List[WeaponAffix] = Field(default_factory=list)
    legendary_perk: Optional[WeaponAffix] = None

    monetary_value: int = Field(ge=0)
    salvage_yield: Dict[CraftingMaterialType, int] = Field(default_factory=dict)
    gameplay_tags: List[str] = Field(default_factory=list)

    @property
    def calculated_dps(self) -> float:
        """Computed DPS including all affix and modifier influences."""
        return self.calculated_stats.damage_per_shot * self.calculated_stats.rounds_per_second

    @property
    def total_affixes_count(self) -> int:
        """Count of all active affixes."""
        count = len(self.prefixes) + len(self.suffixes)
        if self.legendary_perk is not None:
            count += 1
        return count
