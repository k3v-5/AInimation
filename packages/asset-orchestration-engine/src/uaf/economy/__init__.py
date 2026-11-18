"""
UAF-81.93: Dynamic Economy, Weapon Affixes & Procedural Loot Fabric.
Deterministic weapon synthesis, mathematical power budgeting, affix catalogs,
elemental vulnerability matrices, pacing-coupled markets, circular salvage,
and Unreal Engine 5 Gameplay Ability System (GAS) / DataTable exporters.
"""

from uaf.economy.core import (
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
)
from uaf.economy.budget import (
    ARCHETYPE_PROFILES,
    PowerBudgetCalculator,
)
from uaf.economy.affixes import (
    ELEMENTAL_MULTIPLIER_MATRIX,
    calculate_elemental_multiplier,
    CATALOG_PREFIXES,
    CATALOG_SUFFIXES,
    CATALOG_LEGENDARY_PERKS,
    ProceduralAffixGenerator,
)
from uaf.economy.loot import (
    BASE_RARITY_PROBABILITIES,
    LootTableEntry,
    LootTable,
    create_default_scifi_loot_table,
    LootDropGenerator,
)
from uaf.economy.market import (
    PACING_MARKET_MULTIPLIERS,
    DynamicMarketManager,
    SalvageWorkshop,
)
from uaf.economy.export import (
    UE5GASDataTableManifest,
    UE5GASExporter,
)

__all__ = [
    # Core contracts
    "ItemRarity",
    "WeaponArchetype",
    "AffixType",
    "ElementalDamageType",
    "ArmorType",
    "StatModifierOp",
    "LootTier",
    "CraftingMaterialType",
    "StatModifier",
    "WeaponAffix",
    "WeaponBaseStats",
    "ProceduralWeapon",
    # Budget
    "ARCHETYPE_PROFILES",
    "PowerBudgetCalculator",
    # Affixes & Elements
    "ELEMENTAL_MULTIPLIER_MATRIX",
    "calculate_elemental_multiplier",
    "CATALOG_PREFIXES",
    "CATALOG_SUFFIXES",
    "CATALOG_LEGENDARY_PERKS",
    "ProceduralAffixGenerator",
    # Loot
    "BASE_RARITY_PROBABILITIES",
    "LootTableEntry",
    "LootTable",
    "create_default_scifi_loot_table",
    "LootDropGenerator",
    # Market & Salvage
    "PACING_MARKET_MULTIPLIERS",
    "DynamicMarketManager",
    "SalvageWorkshop",
    # Export
    "UE5GASDataTableManifest",
    "UE5GASExporter",
]
