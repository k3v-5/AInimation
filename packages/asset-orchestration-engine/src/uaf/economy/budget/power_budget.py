"""
UAF-81.93: Power Budget Calculator & Archetype Stat Allocation.
Mathematical models for power scaling, archetype handling profiles,
and budget conservation verification.
"""

from __future__ import annotations

import math
import random
from typing import Dict, Tuple

from uaf.economy.core.contracts import (
    ItemRarity,
    WeaponArchetype,
    WeaponBaseStats,
)


# Archetype baseline power and reference stat templates
ARCHETYPE_PROFILES: Dict[WeaponArchetype, Dict[str, float]] = {
    WeaponArchetype.PISTOL: {
        "base_power": 100.0,
        "base_damage": 25.0,
        "base_rps": 4.0,
        "magazine": 12,
        "reload_time": 1.4,
        "spread_deg": 2.0,
        "recoil_deg": 1.5,
        "range_m": 35.0,
        "mass_kg": 1.2,
    },
    WeaponArchetype.SHOTGUN: {
        "base_power": 150.0,
        "base_damage": 120.0,
        "base_rps": 1.25,
        "magazine": 6,
        "reload_time": 2.8,
        "spread_deg": 6.5,
        "recoil_deg": 4.5,
        "range_m": 18.0,
        "mass_kg": 3.8,
    },
    WeaponArchetype.ASSAULT_RIFLE: {
        "base_power": 140.0,
        "base_damage": 20.0,
        "base_rps": 7.0,
        "magazine": 30,
        "reload_time": 2.0,
        "spread_deg": 3.0,
        "recoil_deg": 2.2,
        "range_m": 50.0,
        "mass_kg": 3.5,
    },
    WeaponArchetype.SNIPER_RIFLE: {
        "base_power": 180.0,
        "base_damage": 180.0,
        "base_rps": 1.0,
        "magazine": 5,
        "reload_time": 3.2,
        "spread_deg": 0.2,
        "recoil_deg": 6.0,
        "range_m": 120.0,
        "mass_kg": 6.5,
    },
    WeaponArchetype.HEAVY_CANNON: {
        "base_power": 220.0,
        "base_damage": 275.0,
        "base_rps": 0.8,
        "magazine": 4,
        "reload_time": 4.0,
        "spread_deg": 4.0,
        "recoil_deg": 8.0,
        "range_m": 60.0,
        "mass_kg": 12.0,
    },
    WeaponArchetype.ENERGY_SMG: {
        "base_power": 130.0,
        "base_damage": 13.0,
        "base_rps": 10.0,
        "magazine": 40,
        "reload_time": 1.8,
        "spread_deg": 3.5,
        "recoil_deg": 1.8,
        "range_m": 30.0,
        "mass_kg": 2.6,
    },
    WeaponArchetype.PLASMA_BLASTER: {
        "base_power": 160.0,
        "base_damage": 40.0,
        "base_rps": 4.0,
        "magazine": 20,
        "reload_time": 2.4,
        "spread_deg": 2.5,
        "recoil_deg": 3.0,
        "range_m": 45.0,
        "mass_kg": 4.2,
    },
    WeaponArchetype.MELEE_BLADE: {
        "base_power": 170.0,
        "base_damage": 85.0,
        "base_rps": 2.0,
        "magazine": 1,
        "reload_time": 0.1,
        "spread_deg": 0.0,
        "recoil_deg": 0.0,
        "range_m": 2.5,
        "mass_kg": 1.8,
    },
}


class PowerBudgetCalculator:
    """
    Computes mathematical power budgets and deterministic stat allocations
    for weapon generation according to UAF-81.93 specifications.
    """

    LEVEL_SCALE_FACTOR: float = 0.12  # 12% power growth per level

    @classmethod
    def calculate_power_budget(
        cls,
        level: int,
        rarity: ItemRarity,
        archetype: WeaponArchetype,
    ) -> float:
        """
        Calculates expected weapon DPS power budget:
        Budget(L, R) = BasePower * (1 + 0.12 * L) * RarityMultiplier(R)
        """
        profile = ARCHETYPE_PROFILES[archetype]
        base_power = profile["base_power"]
        level_mult = 1.0 + cls.LEVEL_SCALE_FACTOR * float(level)
        rarity_mult = rarity.multiplier
        return round(base_power * level_mult * rarity_mult, 3)

    @classmethod
    def generate_base_stats(
        cls,
        level: int,
        rarity: ItemRarity,
        archetype: WeaponArchetype,
        seed: int = 42,
    ) -> WeaponBaseStats:
        """
        Synthesizes balanced base stats tailored to the archetype while
        strictly conserving the target power budget.
        """
        profile = ARCHETYPE_PROFILES[archetype]
        target_budget = cls.calculate_power_budget(level, rarity, archetype)

        rng = random.Random(seed + level * 1000 + hash(archetype) % 10000)

        # Baseline stats from profile
        base_damage = profile["base_damage"]
        base_rps = profile["base_rps"]
        profile_base_power = profile["base_power"]

        # Scale factor from baseline power to target budget
        power_ratio = target_budget / profile_base_power

        # Deterministic micro-variance (+- 4%) distributed between damage and fire rate
        var_factor = rng.uniform(0.96, 1.04)

        # Power scaling: target_budget = scaled_damage * scaled_rps
        # We scale damage by sqrt(power_ratio) * var_factor, and rps by sqrt(power_ratio) / var_factor
        sqrt_ratio = math.sqrt(power_ratio)
        scaled_damage = round(base_damage * sqrt_ratio * var_factor, 2)
        scaled_rps = round((target_budget / max(scaled_damage, 0.1)), 2)

        # Ensure bounds
        scaled_damage = max(1.0, scaled_damage)
        scaled_rps = max(0.2, scaled_rps)

        # Secondary handling stats
        mag = int(profile["magazine"])
        reload_s = round(profile["reload_time"], 2)
        spread = round(profile["spread_deg"], 2)
        recoil = round(profile["recoil_deg"], 2)
        range_m = round(profile["range_m"], 1)
        mass = round(profile["mass_kg"], 2)

        # High level/rarity slightly improves handling and reload
        rarity_bonus = 1.0 - (rarity.multiplier - 1.0) * 0.04
        reload_s = round(max(0.1, reload_s * rarity_bonus), 2)
        recoil = round(max(0.0, recoil * rarity_bonus), 2)

        return WeaponBaseStats(
            damage_per_shot=scaled_damage,
            rounds_per_second=scaled_rps,
            magazine_capacity=mag,
            reload_seconds=reload_s,
            accuracy_spread_deg=spread,
            recoil_pitch_deg=recoil,
            effective_range_m=range_m,
            mass_kg=mass,
        )

    @classmethod
    def validate_power_budget(
        cls,
        stats: WeaponBaseStats,
        expected_budget: float,
        tolerance: float = 0.05,
    ) -> bool:
        """Verifies that actual DPS is within tolerance of target budget."""
        actual_dps = stats.base_dps
        if expected_budget <= 0:
            return False
        relative_diff = abs(actual_dps - expected_budget) / expected_budget
        return relative_diff <= tolerance
