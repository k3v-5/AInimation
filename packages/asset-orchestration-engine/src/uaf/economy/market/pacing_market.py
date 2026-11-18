"""
UAF-81.93: Dynamic Economy, Pacing Market Curves & Salvage / Reforge Workshop.
Real-time pricing influenced by DynamicPacingDirector tension states,
inflation curves, and circular salvage economics.
"""

from __future__ import annotations

import copy
import math
import random
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.economy.core.contracts import (
    CraftingMaterialType,
    ItemRarity,
    ProceduralWeapon,
    WeaponAffix,
    AffixType,
)
from uaf.level_design.core.contracts import PacingPhase
from uaf.economy.affixes.generator import (
    CATALOG_PREFIXES,
    CATALOG_SUFFIXES,
    ProceduralAffixGenerator,
)


# Multipliers for buying and selling based on PacingDirector state
PACING_MARKET_MULTIPLIERS: Dict[PacingPhase, Dict[str, float]] = {
    PacingPhase.CALM: {
        "buy_multiplier": 1.00,       # Standard retail price
        "sell_multiplier": 0.50,      # Merchants purchase player goods at 50%
        "supply_factor": 1.00,
    },
    PacingPhase.BUILDUP: {
        "buy_multiplier": 1.25,       # Anticipation of conflict raises costs
        "sell_multiplier": 0.55,
        "supply_factor": 0.90,
    },
    PacingPhase.PEAK: {
        "buy_multiplier": 1.85,       # Wartime emergency surge pricing
        "sell_multiplier": 0.70,      # Merchants eagerly buy combat gear
        "supply_factor": 0.50,
    },
    PacingPhase.SUSTAINED_PEAK: {
        "buy_multiplier": 2.10,       # Severe scarcity
        "sell_multiplier": 0.80,      # Maximum merchant buyback rate
        "supply_factor": 0.35,
    },
    PacingPhase.COOLDOWN: {
        "buy_multiplier": 0.80,       # Clearance discounts & restock surplus
        "sell_multiplier": 0.45,
        "supply_factor": 1.25,
    },
}


class DynamicMarketManager:
    """
    Simulates in-game merchant transactions and economic fluctuations
    directly coupled to player combat intensity from the Pacing Director.
    """

    def __init__(self, base_inflation_rate: float = 0.15):
        self.base_inflation_rate = base_inflation_rate

    def get_price_multipliers(self, phase: PacingPhase) -> Dict[str, float]:
        """Returns active buy/sell multipliers for the given pacing phase."""
        return PACING_MARKET_MULTIPLIERS.get(phase, PACING_MARKET_MULTIPLIERS[PacingPhase.CALM])

    def calculate_buy_price(self, weapon: ProceduralWeapon, phase: PacingPhase) -> int:
        """
        Calculates price for player to buy a weapon from a merchant:
        Price = BaseValue * PhaseBuyMultiplier
        """
        mult = self.get_price_multipliers(phase)["buy_multiplier"]
        return max(10, int(round(weapon.monetary_value * mult)))

    def calculate_sell_price(self, weapon: ProceduralWeapon, phase: PacingPhase) -> int:
        """
        Calculates price a merchant pays the player for a weapon:
        Price = BaseValue * PhaseSellMultiplier
        """
        mult = self.get_price_multipliers(phase)["sell_multiplier"]
        return max(5, int(round(weapon.monetary_value * mult)))


# ---------------------------------------------------------------------------
# Salvage & Reforge Workshop
# ---------------------------------------------------------------------------

class SalvageWorkshop:
    """
    Deconstructs weapons into crafting materials and provides affix reforging.
    """

    @classmethod
    def salvage_weapon(cls, weapon: ProceduralWeapon) -> Dict[CraftingMaterialType, int]:
        """
        Deconstructs a weapon, returning its salvage yield components.
        """
        result: Dict[CraftingMaterialType, int] = {}
        for mat_key, amount in weapon.salvage_yield.items():
            if isinstance(mat_key, str):
                mat_type = CraftingMaterialType(mat_key)
            else:
                mat_type = mat_key
            result[mat_type] = amount
        return result

    @classmethod
    def get_reforge_cost(
        cls,
        weapon: ProceduralWeapon,
    ) -> Dict[CraftingMaterialType, int]:
        """Calculates material cost needed to reforge one affix on this weapon."""
        cost: Dict[CraftingMaterialType, int] = {
            CraftingMaterialType.SCRAP_METAL: int(10 + weapon.level * 3),
        }
        if weapon.rarity in (ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY):
            cost[CraftingMaterialType.REFINED_ALLOY] = int(weapon.level)
            cost[CraftingMaterialType.NANITE_CIRCUITS] = 2
        if weapon.rarity in (ItemRarity.EPIC, ItemRarity.LEGENDARY):
            cost[CraftingMaterialType.ENERGY_CELL] = 1
        return cost

    @classmethod
    def reforge_affix(
        cls,
        weapon: ProceduralWeapon,
        affix_to_replace_id: str,
        seed: int = 999,
    ) -> ProceduralWeapon:
        """
        Replaces a specified affix on the weapon with a newly rolled one,
        recalculating all derived stats, names, tags and values deterministically.
        """
        rng = random.Random(seed + hash(affix_to_replace_id) % 8888)

        new_prefixes = list(weapon.prefixes)
        new_suffixes = list(weapon.suffixes)

        replaced = False

        # 1. Check if target is in prefixes
        for idx, pfx in enumerate(new_prefixes):
            if pfx.affix_id == affix_to_replace_id:
                # Replace with different prefix
                candidate_pool = [
                    p for p in CATALOG_PREFIXES
                    if p.affix_id != affix_to_replace_id
                    and p.affix_id not in [x.affix_id for x in new_prefixes]
                ]
                if candidate_pool:
                    new_prefixes[idx] = rng.choice(candidate_pool)
                    replaced = True
                break

        # 2. Check if target is in suffixes
        if not replaced:
            for idx, sfx in enumerate(new_suffixes):
                if sfx.affix_id == affix_to_replace_id:
                    candidate_pool = [
                        s for s in CATALOG_SUFFIXES
                        if s.affix_id != affix_to_replace_id
                        and s.affix_id not in [x.affix_id for x in new_suffixes]
                    ]
                    if candidate_pool:
                        new_suffixes[idx] = rng.choice(candidate_pool)
                        replaced = True
                    break

        if not replaced:
            # Nothing matched, return unmodified copy
            return weapon

        # 3. Recalculate stats with the updated affixes
        all_mods = []
        for pfx in new_prefixes:
            all_mods.extend(pfx.stat_modifiers)
        for sfx in new_suffixes:
            all_mods.extend(sfx.stat_modifiers)
        if weapon.legendary_perk:
            all_mods.extend(weapon.legendary_perk.stat_modifiers)

        recalculated_stats = ProceduralAffixGenerator.apply_stat_modifiers(
            weapon.base_stats, all_mods
        )

        # 4. Regenerate Name
        name_parts: List[str] = []
        for pfx in new_prefixes:
            name_parts.append(pfx.name)
        archetype_clean = weapon.archetype.value.replace("_", " ").title()
        name_parts.append(archetype_clean)
        if new_suffixes:
            name_parts.append(new_suffixes[0].name)
        if weapon.legendary_perk:
            name_parts.append(f"[{weapon.legendary_perk.name}]")

        new_name = " ".join(name_parts)

        # 5. Re-aggregate tags
        tags: Set[str] = {
            f"Weapon.Archetype.{weapon.archetype.value}",
            f"Item.Rarity.{weapon.rarity.value}",
            f"Damage.Type.{weapon.elemental_type.value}",
        }
        for pfx in new_prefixes:
            tags.update(pfx.gameplay_tags)
        for sfx in new_suffixes:
            tags.update(sfx.gameplay_tags)
        if weapon.legendary_perk:
            tags.update(weapon.legendary_perk.gameplay_tags)

        return ProceduralWeapon(
            item_id=weapon.item_id,
            name=new_name,
            seed=seed,
            level=weapon.level,
            rarity=weapon.rarity,
            archetype=weapon.archetype,
            elemental_type=weapon.elemental_type,
            base_stats=weapon.base_stats,
            calculated_stats=recalculated_stats,
            prefixes=new_prefixes,
            suffixes=new_suffixes,
            legendary_perk=weapon.legendary_perk,
            monetary_value=weapon.monetary_value,
            salvage_yield=weapon.salvage_yield,
            gameplay_tags=sorted(list(tags)),
        )
