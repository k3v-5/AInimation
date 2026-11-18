"""
CharacterFabricationPlatform produces complete character production assets across 7 canonical golden archetypes.
UAF-81.14 Sections 200, 211.
"""

from typing import Tuple, List
from ..models.profile import (
    CharacterClassification,
    CharacterQualityTier,
    CharacterStyle,
    CharacterProfile,
)
from ..models.deformation import (
    DeformationProfile,
    FaceProfile,
    CharacterLayer,
)


class CharacterFabricationPlatform:
    """
    Fabricates production-ready characters complete with anatomy, layers, deformation profiles, and morphs.
    """

    @classmethod
    def build_human_hero(cls, char_id: str = "Char_Human_Hero", seed: int = 101) -> Tuple[CharacterProfile, DeformationProfile, FaceProfile, List[CharacterLayer]]:
        """1. Human Hero (AAA quality, full face rig, layered tactical clothing)."""
        prof = CharacterProfile(
            character_id=char_id,
            classification=CharacterClassification.HERO,
            quality_tier=CharacterQualityTier.HERO,
            style=CharacterStyle.REALISTIC,
            height_cm=185.0,
            body_mass_kg=82.0,
            has_face_rig=True,
            has_hands_rig=True,
            seed=seed,
        )
        deform = DeformationProfile(bone_count=124, max_weights_per_vertex=4, has_dual_quaternion=True, deformation_quality=0.98)
        face = FaceProfile(eye_spacing=1.0, jaw_width=1.0, nose_length=1.0, morph_targets_count=52)
        layers = [
            CharacterLayer("L_Body", "BODY", f"{char_id}_Mesh_Body", "M_Hero_Skin"),
            CharacterLayer("L_Pants", "CLOTHING", f"{char_id}_Mesh_Pants", "M_Hero_TacticalPants", clipping_clearance_mm=2.5),
            CharacterLayer("L_Vest", "ARMOR", f"{char_id}_Mesh_Vest", "M_Hero_KevlarVest", clipping_clearance_mm=5.0),
        ]
        return prof, deform, face, layers

    @classmethod
    def build_human_npc(cls, char_id: str = "Char_Human_NPC", seed: int = 202) -> Tuple[CharacterProfile, DeformationProfile, FaceProfile, List[CharacterLayer]]:
        """2. Human NPC (Standard civilian quality)."""
        prof = CharacterProfile(
            character_id=char_id,
            classification=CharacterClassification.NPC,
            quality_tier=CharacterQualityTier.STANDARD,
            style=CharacterStyle.REALISTIC,
            height_cm=175.0,
            body_mass_kg=70.0,
            has_face_rig=False,
            has_hands_rig=True,
            seed=seed,
        )
        deform = DeformationProfile(bone_count=56, max_weights_per_vertex=4, has_dual_quaternion=False, deformation_quality=0.88)
        face = FaceProfile(morph_targets_count=12)
        layers = [
            CharacterLayer("L_Body", "BODY", f"{char_id}_Mesh_Body", "M_NPC_Skin"),
            CharacterLayer("L_Jacket", "CLOTHING", f"{char_id}_Mesh_Jacket", "M_NPC_Fabric"),
        ]
        return prof, deform, face, layers

    @classmethod
    def build_heavy_robot(cls, char_id: str = "Char_Heavy_Robot", seed: int = 303) -> Tuple[CharacterProfile, DeformationProfile, FaceProfile, List[CharacterLayer]]:
        """3. Heavy Robot (Armored mechanical biped, high bone rigidity)."""
        prof = CharacterProfile(
            character_id=char_id,
            classification=CharacterClassification.ELITE,
            quality_tier=CharacterQualityTier.HIGH,
            style=CharacterStyle.INDUSTRIAL,
            height_cm=240.0,
            body_mass_kg=450.0,
            has_face_rig=False,
            has_hands_rig=False,
            seed=seed,
        )
        deform = DeformationProfile(bone_count=48, max_weights_per_vertex=1, has_dual_quaternion=False, deformation_quality=1.0)
        face = FaceProfile(morph_targets_count=0)
        layers = [
            CharacterLayer("L_Endoskeleton", "BODY", f"{char_id}_Mesh_Endo", "M_Robot_Hydraulics"),
            CharacterLayer("L_Chassis", "ARMOR", f"{char_id}_Mesh_Plates", "M_Robot_PaintedPlates", clipping_clearance_mm=8.0),
        ]
        return prof, deform, face, layers

    @classmethod
    def build_light_robot(cls, char_id: str = "Char_Light_Robot", seed: int = 404) -> Tuple[CharacterProfile, DeformationProfile, FaceProfile, List[CharacterLayer]]:
        """4. Light Robot (Agile scout android, polymer shell)."""
        prof = CharacterProfile(
            character_id=char_id,
            classification=CharacterClassification.ENEMY,
            quality_tier=CharacterQualityTier.STANDARD,
            style=CharacterStyle.BIO_MECHANICAL,
            height_cm=160.0,
            body_mass_kg=55.0,
            has_face_rig=False,
            has_hands_rig=True,
            seed=seed,
        )
        deform = DeformationProfile(bone_count=62, max_weights_per_vertex=2, has_dual_quaternion=False, deformation_quality=0.92)
        face = FaceProfile(morph_targets_count=4)
        layers = [
            CharacterLayer("L_Chassis", "BODY", f"{char_id}_Mesh_Chassis", "M_Android_Polymer"),
        ]
        return prof, deform, face, layers

    @classmethod
    def build_creature(cls, char_id: str = "Char_Creature_Beast", seed: int = 505) -> Tuple[CharacterProfile, DeformationProfile, FaceProfile, List[CharacterLayer]]:
        """5. Creature (Quadruped organic beast with tail and jaws)."""
        prof = CharacterProfile(
            character_id=char_id,
            classification=CharacterClassification.CREATURE,
            quality_tier=CharacterQualityTier.HIGH,
            style=CharacterStyle.ORGANIC if hasattr(CharacterStyle, "ORGANIC") else CharacterStyle.REALISTIC,
            height_cm=140.0,
            body_mass_kg=220.0,
            has_face_rig=True,
            has_hands_rig=False,
            seed=seed,
        )
        deform = DeformationProfile(bone_count=78, max_weights_per_vertex=4, has_dual_quaternion=True, deformation_quality=0.94)
        face = FaceProfile(morph_targets_count=16)
        layers = [
            CharacterLayer("L_Hide", "BODY", f"{char_id}_Mesh_Hide", "M_Creature_Scales"),
        ]
        return prof, deform, face, layers

    @classmethod
    def build_alien(cls, char_id: str = "Char_Alien_Infiltrator", seed: int = 606) -> Tuple[CharacterProfile, DeformationProfile, FaceProfile, List[CharacterLayer]]:
        """6. Alien (Biomechanical humanoid with carapace)."""
        prof = CharacterProfile(
            character_id=char_id,
            classification=CharacterClassification.ENEMY,
            quality_tier=CharacterQualityTier.HIGH,
            style=CharacterStyle.ALIEN,
            height_cm=210.0,
            body_mass_kg=95.0,
            has_face_rig=True,
            has_hands_rig=True,
            seed=seed,
        )
        deform = DeformationProfile(bone_count=84, max_weights_per_vertex=4, has_dual_quaternion=True, deformation_quality=0.95)
        face = FaceProfile(morph_targets_count=24)
        layers = [
            CharacterLayer("L_Flesh", "BODY", f"{char_id}_Mesh_Flesh", "M_Alien_Skin"),
            CharacterLayer("L_Carapace", "ARMOR", f"{char_id}_Mesh_Carapace", "M_Alien_Chitin", clipping_clearance_mm=4.0),
        ]
        return prof, deform, face, layers

    @classmethod
    def build_boss(cls, char_id: str = "Char_Boss_Colossus", seed: int = 707) -> Tuple[CharacterProfile, DeformationProfile, FaceProfile, List[CharacterLayer]]:
        """7. Boss (Colossal armored titan with specialized gear)."""
        prof = CharacterProfile(
            character_id=char_id,
            classification=CharacterClassification.BOSS,
            quality_tier=CharacterQualityTier.CINEMATIC,
            style=CharacterStyle.BIO_MECHANICAL,
            height_cm=380.0,
            body_mass_kg=1200.0,
            has_face_rig=True,
            has_hands_rig=True,
            seed=seed,
        )
        deform = DeformationProfile(bone_count=160, max_weights_per_vertex=4, has_dual_quaternion=True, deformation_quality=0.99)
        face = FaceProfile(morph_targets_count=64)
        layers = [
            CharacterLayer("L_Body", "BODY", f"{char_id}_Mesh_Body", "M_Boss_Core"),
            CharacterLayer("L_ArmorPlates", "ARMOR", f"{char_id}_Mesh_Armor", "M_Boss_Plates", clipping_clearance_mm=10.0),
            CharacterLayer("L_Cape", "CLOTHING", f"{char_id}_Mesh_Cape", "M_Boss_Cloth", clipping_clearance_mm=15.0),
        ]
        return prof, deform, face, layers
