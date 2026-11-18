"""
CharacterOrganicFabricationPlatform manufactures all 5 canonical golden characters from Section 115.
UAF-81.26 Sections 115, 116, 117, 118, 141.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    OrganicCharacterDefinition,
    CharacterArchetype26,
    CharacterProportions,
    LayeredClothingItem,
)


class CharacterOrganicFabricationPlatform:
    """
    Synthesizes complete organic and modular production characters matching Section 115.
    """

    @classmethod
    def build_golden_human(cls, char_id: str = "Char_Golden_Human") -> Tuple[OrganicCharacterDefinition, str, str, int]:
        """1. GOLDEN_HUMAN (Standard civilian/human anatomy, layered clothing, hair)."""
        prop = CharacterProportions(height_cm=175.0)
        clothing = [
            LayeredClothingItem("Cloth_Shirt", "TORSO", thickness_mm=1.5, clearance_mm=1.0),
            LayeredClothingItem("Cloth_Trousers", "LEGS", thickness_mm=2.0, clearance_mm=1.2),
            LayeredClothingItem("Cloth_Sneakers", "FEET", thickness_mm=4.0, clearance_mm=2.0),
        ]
        c_def = OrganicCharacterDefinition(
            char_id,
            CharacterArchetype26.HUMAN,
            prop,
            clothing,
            hair_style="HAIR_SHORT_CROP",
            has_facial_landmarks=True,
        )
        return c_def, f"SK_{char_id}", "SKEL_Humanoid_Master", 4

    @classmethod
    def build_golden_soldier(cls, char_id: str = "Char_Golden_Soldier") -> Tuple[OrganicCharacterDefinition, str, str, int]:
        """2. GOLDEN_SOLDIER (Tactical gear, heavy boots, ballistic vest, helmet)."""
        prop = CharacterProportions(height_cm=185.0, shoulder_ratio=0.28)
        clothing = [
            LayeredClothingItem("Gear_Fatigues", "TORSO", thickness_mm=2.0, clearance_mm=1.0),
            LayeredClothingItem("Gear_BallisticVest", "ARMOR_OUTER", thickness_mm=12.0, clearance_mm=3.0),
            LayeredClothingItem("Gear_CombatBoots", "FEET", thickness_mm=8.0, clearance_mm=2.5),
            LayeredClothingItem("Gear_Helmet", "HEAD", thickness_mm=6.0, clearance_mm=4.0),
        ]
        c_def = OrganicCharacterDefinition(
            char_id,
            CharacterArchetype26.SOLDIER,
            prop,
            clothing,
            hair_style="HAIR_BUZZCUT",
            has_facial_landmarks=True,
        )
        return c_def, f"SK_{char_id}", "SKEL_Humanoid_Master", 5

    @classmethod
    def build_golden_robot(cls, char_id: str = "Char_Golden_Robot") -> Tuple[OrganicCharacterDefinition, str, str, int]:
        """3. GOLDEN_ROBOT (Mechanical joints, plating, zero hair, zero organic clothing)."""
        prop = CharacterProportions(height_cm=190.0, head_ratio=0.12)
        c_def = OrganicCharacterDefinition(
            char_id,
            CharacterArchetype26.ROBOT,
            prop,
            clothing_layers=[],
            hair_style="NONE",
            has_facial_landmarks=False,
        )
        return c_def, f"SK_{char_id}", "SKEL_Robot_Chassis", 4

    @classmethod
    def build_golden_creature(cls, char_id: str = "Char_Golden_Creature") -> Tuple[OrganicCharacterDefinition, str, str, int]:
        """4. GOLDEN_CREATURE (Non-human beast, quadrupedal proportions, custom anatomy)."""
        prop = CharacterProportions(height_cm=140.0, leg_ratio=0.60)
        c_def = OrganicCharacterDefinition(
            char_id,
            CharacterArchetype26.CREATURE,
            prop,
            clothing_layers=[],
            hair_style="FUR_CARD_LAYER",
            has_facial_landmarks=False,
        )
        return c_def, f"SK_{char_id}", "SKEL_Creature_Beast", 4

    @classmethod
    def build_golden_boss(cls, char_id: str = "Char_Golden_Boss") -> Tuple[OrganicCharacterDefinition, str, str, int]:
        """5. GOLDEN_BOSS (Massive stature, multilayer armor, cape, weapon integration)."""
        prop = CharacterProportions(height_cm=260.0, shoulder_ratio=0.35, torso_ratio=0.40)
        clothing = [
            LayeredClothingItem("Armor_Undergarment", "TORSO", thickness_mm=3.0, clearance_mm=1.0),
            LayeredClothingItem("Armor_PlateCuirass", "ARMOR_OUTER", thickness_mm=18.0, clearance_mm=4.0),
            LayeredClothingItem("Cloth_SovereignCape", "ARMOR_OUTER", thickness_mm=2.5, clearance_mm=8.0),
        ]
        c_def = OrganicCharacterDefinition(
            char_id,
            CharacterArchetype26.BOSS,
            prop,
            clothing,
            hair_style="HAIR_LONG_MANE",
            has_facial_landmarks=True,
        )
        return c_def, f"SK_{char_id}", "SKEL_Titan_Boss", 6
