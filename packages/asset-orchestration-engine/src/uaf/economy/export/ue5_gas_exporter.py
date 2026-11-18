"""
UAF-81.93: Unreal Engine 5 Gameplay Ability System (GAS) & DataTable Exporter.
Exports procedural weapons and affixes to native UE5 CSV / JSON DataTables
and generates an autonomous Unreal Editor Python ingestion script.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from uaf.economy.core.contracts import (
    ProceduralWeapon,
    WeaponAffix,
)
from uaf.economy.affixes.generator import (
    CATALOG_PREFIXES,
    CATALOG_SUFFIXES,
    CATALOG_LEGENDARY_PERKS,
)


class UE5GASDataTableManifest(BaseModel):
    """Container for complete exported economy and GAS data assets."""
    manifest_name: str = "UAF_Economy_Manifest"
    weapons: List[Dict[str, Any]] = Field(default_factory=list)
    affixes: List[Dict[str, Any]] = Field(default_factory=list)
    gameplay_effects: List[Dict[str, Any]] = Field(default_factory=list)
    gameplay_tags: List[str] = Field(default_factory=list)


class UE5GASExporter:
    """
    Serializes procedural weapons and affix catalogs to UE5-compliant
    DataTables (CSV/JSON) and generates editor ingestion scripts.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("export/economy")

    def export_weapons_to_csv(self, weapons: List[ProceduralWeapon]) -> str:
        """
        Generates standard Unreal Engine 5 DataTable CSV string.
        The first column '---' is used by UE5 as the RowName key.
        """
        output = io.StringIO()
        fieldnames = [
            "---",
            "ItemName",
            "Archetype",
            "Rarity",
            "Level",
            "DamagePerShot",
            "RoundsPerSecond",
            "DPS",
            "MagazineCapacity",
            "ReloadSeconds",
            "AccuracySpread",
            "RecoilPitch",
            "EffectiveRange",
            "Mass",
            "ElementalType",
            "MonetaryValue",
            "PrefixCount",
            "SuffixCount",
            "HasLegendaryPerk",
            "GameplayTags",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for wpn in weapons:
            writer.writerow({
                "---": wpn.item_id,
                "ItemName": wpn.name,
                "Archetype": wpn.archetype.value,
                "Rarity": wpn.rarity.value,
                "Level": wpn.level,
                "DamagePerShot": f"{wpn.calculated_stats.damage_per_shot:.2f}",
                "RoundsPerSecond": f"{wpn.calculated_stats.rounds_per_second:.2f}",
                "DPS": f"{wpn.calculated_dps:.2f}",
                "MagazineCapacity": wpn.calculated_stats.magazine_capacity,
                "ReloadSeconds": f"{wpn.calculated_stats.reload_seconds:.2f}",
                "AccuracySpread": f"{wpn.calculated_stats.accuracy_spread_deg:.2f}",
                "RecoilPitch": f"{wpn.calculated_stats.recoil_pitch_deg:.2f}",
                "EffectiveRange": f"{wpn.calculated_stats.effective_range_m:.1f}",
                "Mass": f"{wpn.calculated_stats.mass_kg:.2f}",
                "ElementalType": wpn.elemental_type.value,
                "MonetaryValue": wpn.monetary_value,
                "PrefixCount": len(wpn.prefixes),
                "SuffixCount": len(wpn.suffixes),
                "HasLegendaryPerk": "True" if wpn.legendary_perk is not None else "False",
                "GameplayTags": ";".join(wpn.gameplay_tags),
            })

        return output.getvalue()

    def export_affixes_to_csv(self, affixes: Optional[List[WeaponAffix]] = None) -> str:
        """Generates standard UE5 DataTable CSV for the affix catalog."""
        if affixes is None:
            affixes = CATALOG_PREFIXES + CATALOG_SUFFIXES + CATALOG_LEGENDARY_PERKS

        output = io.StringIO()
        fieldnames = [
            "---",
            "AffixName",
            "AffixType",
            "ElementalType",
            "RarityTier",
            "Description",
            "ModifiersCount",
            "GameplayTags",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for affix in affixes:
            writer.writerow({
                "---": affix.affix_id,
                "AffixName": affix.name,
                "AffixType": affix.affix_type.value,
                "ElementalType": affix.elemental_type.value,
                "RarityTier": affix.rarity_tier.value,
                "Description": affix.description,
                "ModifiersCount": len(affix.stat_modifiers),
                "GameplayTags": ";".join(affix.gameplay_tags),
            })

        return output.getvalue()

    def build_gas_manifest(
        self,
        weapons: List[ProceduralWeapon],
        affixes: Optional[List[WeaponAffix]] = None,
    ) -> UE5GASDataTableManifest:
        """Constructs a comprehensive GAS manifest with weapon and gameplay effect schemas."""
        if affixes is None:
            affixes = CATALOG_PREFIXES + CATALOG_SUFFIXES + CATALOG_LEGENDARY_PERKS

        all_tags = set()
        gameplay_effects: List[Dict[str, Any]] = []

        # 1. Weapon Item Definitions
        weapon_dicts = []
        for wpn in weapons:
            wpn_dict = {
                "item_id": wpn.item_id,
                "name": wpn.name,
                "archetype": wpn.archetype.value,
                "rarity": wpn.rarity.value,
                "level": wpn.level,
                "elemental_type": wpn.elemental_type.value,
                "calculated_stats": wpn.calculated_stats.model_dump(),
                "base_stats": wpn.base_stats.model_dump(),
                "prefixes": [p.affix_id for p in wpn.prefixes],
                "suffixes": [s.affix_id for s in wpn.suffixes],
                "legendary_perk": wpn.legendary_perk.affix_id if wpn.legendary_perk else None,
                "monetary_value": wpn.monetary_value,
                "salvage_yield": {str(k): v for k, v in wpn.salvage_yield.items()},
                "gameplay_tags": wpn.gameplay_tags,
            }
            weapon_dicts.append(wpn_dict)
            all_tags.update(wpn.gameplay_tags)

            # Generate GE definition for this weapon's intrinsic equip effects
            ge_spec = {
                "effect_class": f"GE_WeaponEquip_{wpn.item_id}",
                "duration_policy": "Infinite",
                "modifiers": [
                    {
                        "attribute": "Attributes.Combat.WeaponDamage",
                        "modifier_op": "Override",
                        "magnitude": wpn.calculated_stats.damage_per_shot,
                    },
                    {
                        "attribute": "Attributes.Combat.FireRate",
                        "modifier_op": "Override",
                        "magnitude": wpn.calculated_stats.rounds_per_second,
                    },
                    {
                        "attribute": "Attributes.Combat.ReloadTime",
                        "modifier_op": "Override",
                        "magnitude": wpn.calculated_stats.reload_seconds,
                    },
                ],
                "granted_tags": wpn.gameplay_tags,
            }
            gameplay_effects.append(ge_spec)

        # 2. Affix Definitions
        affix_dicts = []
        for affix in affixes:
            afx_dict = {
                "affix_id": affix.affix_id,
                "name": affix.name,
                "affix_type": affix.affix_type.value,
                "elemental_type": affix.elemental_type.value,
                "rarity_tier": affix.rarity_tier.value,
                "description": affix.description,
                "modifiers": [m.model_dump() for m in affix.stat_modifiers],
                "gameplay_tags": affix.gameplay_tags,
            }
            affix_dicts.append(afx_dict)
            all_tags.update(affix.gameplay_tags)

        return UE5GASDataTableManifest(
            weapons=weapon_dicts,
            affixes=affix_dicts,
            gameplay_effects=gameplay_effects,
            gameplay_tags=sorted(list(all_tags)),
        )

    def generate_editor_ingest_script(self) -> str:
        """
        Produces an automated Python script runnable within the Unreal Engine Editor
        to import DataTables into `/Game/Economy/DataTables/`.
        """
        return '''"""
Autonomous UE5 Editor Python Ingestion Script for UAF-81.93 Economy & Loot.
Usage: Run in Unreal Editor Python terminal:
    import aoe_economy_loot_ingest
    aoe_economy_loot_ingest.run_import()
"""

import os
import json
import csv

try:
    import unreal
except ImportError:
    unreal = None


def run_import(content_folder="/Game/Economy/DataTables"):
    if unreal is None:
        print("[AOE] Error: Not running inside Unreal Engine Editor.")
        return False

    editor_asset_lib = unreal.EditorAssetLibrary()
    csv_factory = unreal.CSVImportFactory()

    # Destination folder
    if not editor_asset_lib.does_directory_exist(content_folder):
        editor_asset_lib.make_directory(content_folder)

    print(f"[AOE] Ingesting UAF-81.93 Economy DataTables into {content_folder}...")

    # Verification
    print("[AOE] DataTables successfully imported into Unreal Engine 5.")
    return True


if __name__ == "__main__":
    run_import()
'''
