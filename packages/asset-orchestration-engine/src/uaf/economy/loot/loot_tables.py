"""
UAF-81.93: Loot Tables, Weighted Drops, Luck Scaling & Bad Luck Protection.
Probabilistic item distribution, chest generation, and boss guarantees.
"""

from __future__ import annotations

import copy
import random
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.economy.core.contracts import (
    ItemRarity,
    LootTier,
    ProceduralWeapon,
    WeaponArchetype,
)
from uaf.economy.affixes.generator import ProceduralAffixGenerator


# ---------------------------------------------------------------------------
# Base Rarity Probabilities per Loot Tier
# ---------------------------------------------------------------------------

BASE_RARITY_PROBABILITIES: Dict[LootTier, Dict[ItemRarity, float]] = {
    LootTier.TIER_1_STANDARD: {
        ItemRarity.COMMON: 0.75,
        ItemRarity.UNCOMMON: 0.20,
        ItemRarity.RARE: 0.05,
        ItemRarity.EPIC: 0.00,
        ItemRarity.LEGENDARY: 0.00,
    },
    LootTier.TIER_2_ELITE: {
        ItemRarity.COMMON: 0.40,
        ItemRarity.UNCOMMON: 0.40,
        ItemRarity.RARE: 0.16,
        ItemRarity.EPIC: 0.04,
        ItemRarity.LEGENDARY: 0.00,
    },
    LootTier.TIER_3_CHEST: {
        ItemRarity.COMMON: 0.20,
        ItemRarity.UNCOMMON: 0.45,
        ItemRarity.RARE: 0.25,
        ItemRarity.EPIC: 0.09,
        ItemRarity.LEGENDARY: 0.01,
    },
    LootTier.TIER_4_BOSS: {
        ItemRarity.COMMON: 0.00,
        ItemRarity.UNCOMMON: 0.25,
        ItemRarity.RARE: 0.45,
        ItemRarity.EPIC: 0.22,
        ItemRarity.LEGENDARY: 0.08,
    },
    LootTier.TIER_5_VAULT: {
        ItemRarity.COMMON: 0.00,
        ItemRarity.UNCOMMON: 0.10,
        ItemRarity.RARE: 0.40,
        ItemRarity.EPIC: 0.35,
        ItemRarity.LEGENDARY: 0.15,
    },
}


class LootTableEntry(BaseModel):
    """An archetype candidate entry in a drop table."""
    archetype: WeaponArchetype
    weight: float = Field(gt=0)
    min_level: int = 1
    max_level: int = 100


class LootTable(BaseModel):
    """Weighted table of weapon archetypes."""
    table_id: str
    tier: LootTier
    entries: List[LootTableEntry] = Field(default_factory=list)

    def select_archetype(self, level: int, rng: random.Random) -> WeaponArchetype:
        """Selects a weighted archetype eligible for the given level."""
        eligible = [e for e in self.entries if e.min_level <= level <= e.max_level]
        if not eligible:
            # Fallback to all entries or pistol
            eligible = self.entries or [LootTableEntry(archetype=WeaponArchetype.PISTOL, weight=1.0)]

        total_weight = sum(e.weight for e in eligible)
        roll = rng.uniform(0.0, total_weight)
        cumulative = 0.0
        for entry in eligible:
            cumulative += entry.weight
            if roll <= cumulative:
                return entry.archetype
        return eligible[-1].archetype


def create_default_scifi_loot_table(tier: LootTier = LootTier.TIER_1_STANDARD) -> LootTable:
    """Creates a standard balanced loot table spanning all 8 archetypes."""
    entries = [
        LootTableEntry(archetype=WeaponArchetype.PISTOL, weight=25.0),
        LootTableEntry(archetype=WeaponArchetype.ASSAULT_RIFLE, weight=20.0),
        LootTableEntry(archetype=WeaponArchetype.ENERGY_SMG, weight=18.0),
        LootTableEntry(archetype=WeaponArchetype.SHOTGUN, weight=14.0),
        LootTableEntry(archetype=WeaponArchetype.PLASMA_BLASTER, weight=10.0),
        LootTableEntry(archetype=WeaponArchetype.SNIPER_RIFLE, weight=8.0),
        LootTableEntry(archetype=WeaponArchetype.HEAVY_CANNON, weight=5.0),
        LootTableEntry(archetype=WeaponArchetype.MELEE_BLADE, weight=5.0),
    ]
    return LootTable(table_id=f"LT_SciFi_{tier.value}", tier=tier, entries=entries)


# ---------------------------------------------------------------------------
# Loot Drop Generator with Luck & Bad Luck Protection
# ---------------------------------------------------------------------------

class LootDropGenerator:
    """
    Simulates item drops incorporating luck scaling and deterministic
    bad luck protection (PRD).
    """

    def __init__(self, bad_luck_protection: bool = True):
        self.bad_luck_protection = bad_luck_protection
        self.rolls_since_last_epic: int = 0
        self.rolls_since_last_legendary: int = 0

    def compute_rarity_probabilities(
        self,
        tier: LootTier,
        luck_score: float = 0.0,
    ) -> Dict[ItemRarity, float]:
        """
        Computes adjusted rarity distribution with non-linear luck scaling
        and bad luck protection boosts.
        """
        probs = copy.deepcopy(BASE_RARITY_PROBABILITIES[tier])

        # 1. Apply Luck Scaling
        clamped_luck = max(0.0, float(luck_score))
        rare_boost = 1.0 + 0.015 * clamped_luck
        epic_boost = 1.0 + 0.030 * clamped_luck
        leg_boost = 1.0 + 0.050 * clamped_luck

        probs[ItemRarity.RARE] *= rare_boost
        probs[ItemRarity.EPIC] *= epic_boost
        probs[ItemRarity.LEGENDARY] *= leg_boost

        # 2. Bad Luck Protection (Pity system)
        if self.bad_luck_protection:
            if self.rolls_since_last_epic >= 15:
                # Add +5% per roll past threshold
                pity_epic = 0.05 * (self.rolls_since_last_epic - 14)
                probs[ItemRarity.EPIC] += pity_epic

            if self.rolls_since_last_legendary >= 35:
                # Add +8% per roll past threshold
                pity_leg = 0.08 * (self.rolls_since_last_legendary - 34)
                probs[ItemRarity.LEGENDARY] += pity_leg

        # 3. Normalize probabilities to sum to 1.0
        total = sum(probs.values())
        if total <= 0.0:
            return {ItemRarity.COMMON: 1.0}

        normalized = {k: v / total for k, v in probs.items()}
        return normalized

    def roll_rarity(
        self,
        tier: LootTier,
        luck_score: float = 0.0,
        rng: Optional[random.Random] = None,
    ) -> ItemRarity:
        """Rolls an item rarity according to luck and pity counters."""
        if rng is None:
            rng = random.Random()

        probs = self.compute_rarity_probabilities(tier, luck_score)

        roll = rng.random()
        cumulative = 0.0
        chosen_rarity = ItemRarity.COMMON

        for rarity in (ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY):
            cumulative += probs.get(rarity, 0.0)
            if roll <= cumulative:
                chosen_rarity = rarity
                break

        # Update pity state
        if chosen_rarity == ItemRarity.LEGENDARY:
            self.rolls_since_last_legendary = 0
            self.rolls_since_last_epic = 0
        elif chosen_rarity == ItemRarity.EPIC:
            self.rolls_since_last_epic = 0
            self.rolls_since_last_legendary += 1
        else:
            self.rolls_since_last_epic += 1
            self.rolls_since_last_legendary += 1

        return chosen_rarity

    def generate_drop(
        self,
        tier: LootTier,
        player_level: int,
        luck_score: float = 0.0,
        seed: int = 42,
        loot_table: Optional[LootTable] = None,
    ) -> ProceduralWeapon:
        """Synthesizes a single weapon drop from the specified tier."""
        rng = random.Random(seed + player_level * 1337)
        table = loot_table or create_default_scifi_loot_table(tier)

        rarity = self.roll_rarity(tier, luck_score, rng=rng)
        archetype = table.select_archetype(player_level, rng)

        weapon = ProceduralAffixGenerator.generate_weapon(
            seed=rng.randint(1, 99999999),
            level=player_level,
            rarity=rarity,
            archetype=archetype,
        )
        return weapon

    def generate_chest_loot(
        self,
        tier: LootTier,
        player_level: int,
        item_count: int = 3,
        luck_score: float = 0.0,
        seed: int = 42,
    ) -> List[ProceduralWeapon]:
        """Generates multiple weapons for a loot container / cache."""
        items: List[ProceduralWeapon] = []
        for i in range(item_count):
            item_seed = seed + i * 10007
            item = self.generate_drop(tier, player_level, luck_score, seed=item_seed)
            items.append(item)
        return items

    def generate_boss_guaranteed_drop(
        self,
        player_level: int,
        seed: int = 42,
        min_rarity: ItemRarity = ItemRarity.EPIC,
    ) -> ProceduralWeapon:
        """Guarantees a high-tier drop from defeating a boss encounter."""
        rng = random.Random(seed + player_level * 9999)
        table = create_default_scifi_loot_table(LootTier.TIER_4_BOSS)
        archetype = table.select_archetype(player_level, rng)

        # Force rarity between min_rarity and LEGENDARY
        rarity_choices = [ItemRarity.EPIC, ItemRarity.LEGENDARY]
        if min_rarity == ItemRarity.LEGENDARY:
            rarity_choices = [ItemRarity.LEGENDARY]
        elif min_rarity == ItemRarity.RARE:
            rarity_choices = [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]

        rarity = rng.choice(rarity_choices)

        return ProceduralAffixGenerator.generate_weapon(
            seed=rng.randint(1, 99999999),
            level=player_level,
            rarity=rarity,
            archetype=archetype,
        )
