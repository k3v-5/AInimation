"""
CharacterCreatureFabricationPlatform manufactures characters and creatures across all canonical archetypes.
UAF-81.21 Sections 146, 147, 167, 171.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import CharacterDefinition21, CharacterSpecies, AnatomicalLandmarks
from ..models.equipment import BodyPartType, ModularEquipmentLayer, EquipmentLayerType


class CharacterCreatureFabricationPlatform:
    """
    Synthesizes production characters across all 8 golden archetypes (Section 146)
    plus Section 147 complex multi-layer character.
    """

    @classmethod
    def _default_humanoid_parts(cls) -> List[BodyPartType]:
        return [
            BodyPartType.HEAD,
            BodyPartType.TORSO,
            BodyPartType.PELVIS,
            BodyPartType.UPPER_ARM,
            BodyPartType.LOWER_ARM,
            BodyPartType.HAND,
            BodyPartType.UPPER_LEG,
            BodyPartType.LOWER_LEG,
            BodyPartType.FOOT,
        ]

    @classmethod
    def build_human_character(cls, char_id: str = "Char_Human_Base", seed: int = 101) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """1. Human Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.HUMAN, 180.0, 75.0, "HYBRID", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Body", EquipmentLayerType.BODY, False, 0.0, "M_Skin_Human"),
            ModularEquipmentLayer("Layer_Shirt", EquipmentLayerType.SHIRT, False, 2.0, "M_Fabric_Cotton"),
            ModularEquipmentLayer("Layer_Pants", EquipmentLayerType.PANTS, False, 2.5, "M_Fabric_Denim"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Humanoid_Mannequin"

    @classmethod
    def build_robot_character(cls, char_id: str = "Char_Robot_Chassis", seed: int = 202) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """2. Robot Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.ROBOT, 195.0, 120.0, "MODULAR", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Chassis", EquipmentLayerType.BODY, True, 0.0, "M_Metal_Steel"),
            ModularEquipmentLayer("Layer_Plating", EquipmentLayerType.ARMOR_CHEST, True, 5.0, "M_Metal_Titanium"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Robot_Industrial"

    @classmethod
    def build_alien_character(cls, char_id: str = "Char_Alien_Infiltrator", seed: int = 303) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """3. Alien Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.ALIEN, 210.0, 80.0, "PARAMETRIC", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Exoskin", EquipmentLayerType.BODY, False, 0.0, "M_Skin_Reptilian"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Alien_QuadBiped"

    @classmethod
    def build_creature_character(cls, char_id: str = "Char_Beast_Quadruped", seed: int = 404) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """4. Creature Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.CREATURE, 140.0, 110.0, "HYBRID", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_FurHide", EquipmentLayerType.BODY, False, 0.0, "M_Organic_Fur"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Creature_Quadruped"

    @classmethod
    def build_heavy_armor_character(cls, char_id: str = "Char_HeavyJuggernaut", seed: int = 505) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """5. Heavy Armor Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.HUMAN, 205.0, 130.0, "HYBRID", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Body", EquipmentLayerType.BODY, False, 0.0, "M_Skin_Human"),
            ModularEquipmentLayer("Layer_UnderSuit", EquipmentLayerType.UNDERWEAR, False, 1.5, "M_Synthetic_Rubber"),
            ModularEquipmentLayer("Layer_ChestPlate", EquipmentLayerType.ARMOR_CHEST, True, 6.0, "M_Metal_Plate"),
            ModularEquipmentLayer("Layer_LimbArmor", EquipmentLayerType.ARMOR_LIMBS, True, 5.0, "M_Metal_Plate"),
            ModularEquipmentLayer("Layer_HeavyHelmet", EquipmentLayerType.HELMET, True, 7.0, "M_Metal_Plate"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Humanoid_Heavy"

    @classmethod
    def build_light_armor_character(cls, char_id: str = "Char_LightScout", seed: int = 606) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """6. Light Armor Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.HUMAN, 175.0, 68.0, "HYBRID", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Body", EquipmentLayerType.BODY, False, 0.0, "M_Skin_Human"),
            ModularEquipmentLayer("Layer_ScoutVest", EquipmentLayerType.ARMOR_CHEST, True, 3.5, "M_Composite_Kevlar"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Humanoid_Mannequin"

    @classmethod
    def build_cloth_heavy_character(cls, char_id: str = "Char_ClothHeavyMage", seed: int = 707) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """7. Cloth Heavy Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.HUMAN, 182.0, 72.0, "HYBRID", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Body", EquipmentLayerType.BODY, False, 0.0, "M_Skin_Human"),
            ModularEquipmentLayer("Layer_RobeUnder", EquipmentLayerType.SHIRT, False, 2.0, "M_Fabric_Silk"),
            ModularEquipmentLayer("Layer_RobeCloak", EquipmentLayerType.SHIRT, False, 4.0, "M_Fabric_Wool"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Humanoid_Mannequin"

    @classmethod
    def build_cloth_light_character(cls, char_id: str = "Char_ClothLightRunner", seed: int = 808) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """8. Cloth Light Golden Character."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.HUMAN, 178.0, 65.0, "HYBRID", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Body", EquipmentLayerType.BODY, False, 0.0, "M_Skin_Human"),
            ModularEquipmentLayer("Layer_TrackSuit", EquipmentLayerType.SHIRT, False, 1.5, "M_Fabric_Spandex"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Humanoid_Mannequin"

    @classmethod
    def build_complex_multilayer_character(cls, char_id: str = "Char_ComplexSoldier", seed: int = 909) -> Tuple[CharacterDefinition21, List[BodyPartType], List[ModularEquipmentLayer], str]:
        """Section 147 Complex Character Test (Multi-layer clothing, armor, backpack, weapon)."""
        char_def = CharacterDefinition21(char_id, CharacterSpecies.HUMAN, 185.0, 85.0, "HYBRID", seed=seed)
        layers = [
            ModularEquipmentLayer("Layer_Skin", EquipmentLayerType.BODY, False, 0.0, "M_Skin_Human"),
            ModularEquipmentLayer("Layer_Fatigues", EquipmentLayerType.SHIRT, False, 2.0, "M_Fabric_Camo"),
            ModularEquipmentLayer("Layer_CombatPants", EquipmentLayerType.PANTS, False, 2.5, "M_Fabric_Camo"),
            ModularEquipmentLayer("Layer_TacticalVest", EquipmentLayerType.ARMOR_CHEST, True, 4.5, "M_Kevlar_Black"),
            ModularEquipmentLayer("Layer_TacticalBackpack", EquipmentLayerType.BACKPACK, True, 6.0, "M_Nylon_Heavy"),
            ModularEquipmentLayer("Layer_AssaultRifle", EquipmentLayerType.WEAPON, True, 8.0, "M_Metal_Gunmetal"),
        ]
        return char_def, cls._default_humanoid_parts(), layers, "SKEL_Humanoid_Soldier"
