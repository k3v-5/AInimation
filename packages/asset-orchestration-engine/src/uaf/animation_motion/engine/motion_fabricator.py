"""
AnimationMotionFabricationPlatform manufactures skeletons, rigs, and motion sets for Section 123 character types.
UAF-81.23 Sections 123, 125, 126.
"""

from typing import Tuple, List, Dict, Any
from ..models.skeleton import CharacterRigDefinition, StandardSkeletonHierarchy, RigBoneNode, BoneRoleType
from ..models.motion import MotionClip, MotionClipType


class AnimationMotionFabricationPlatform:
    """
    Synthesizes complete skeletal rigs, control rigs, and animation sets for Section 123 character archetypes.
    """

    @classmethod
    def _create_standard_humanoid_skeleton(cls) -> StandardSkeletonHierarchy:
        skel = StandardSkeletonHierarchy()
        # Section 5 standard humanoid bones
        skel.add_bone(RigBoneNode("root", BoneRoleType.ROOT, None))
        skel.add_bone(RigBoneNode("pelvis", BoneRoleType.PELVIS, "root"))
        skel.add_bone(RigBoneNode("spine_01", BoneRoleType.SPINE, "pelvis"))
        skel.add_bone(RigBoneNode("spine_02", BoneRoleType.SPINE, "spine_01"))
        skel.add_bone(RigBoneNode("chest", BoneRoleType.CHEST, "spine_02"))
        skel.add_bone(RigBoneNode("neck", BoneRoleType.NECK, "chest"))
        skel.add_bone(RigBoneNode("head", BoneRoleType.HEAD, "neck"))

        # Left arm
        skel.add_bone(RigBoneNode("clavicle_l", BoneRoleType.CLAVICLE, "chest"))
        skel.add_bone(RigBoneNode("upperarm_l", BoneRoleType.LIMB_UPPER, "clavicle_l"))
        skel.add_bone(RigBoneNode("lowerarm_l", BoneRoleType.LIMB_LOWER, "upperarm_l"))
        skel.add_bone(RigBoneNode("hand_l", BoneRoleType.HAND, "lowerarm_l"))

        # Right arm
        skel.add_bone(RigBoneNode("clavicle_r", BoneRoleType.CLAVICLE, "chest"))
        skel.add_bone(RigBoneNode("upperarm_r", BoneRoleType.LIMB_UPPER, "clavicle_r"))
        skel.add_bone(RigBoneNode("lowerarm_r", BoneRoleType.LIMB_LOWER, "upperarm_r"))
        skel.add_bone(RigBoneNode("hand_r", BoneRoleType.HAND, "lowerarm_r"))

        # Left leg
        skel.add_bone(RigBoneNode("thigh_l", BoneRoleType.LIMB_UPPER, "pelvis"))
        skel.add_bone(RigBoneNode("calf_l", BoneRoleType.LIMB_LOWER, "thigh_l"))
        skel.add_bone(RigBoneNode("foot_l", BoneRoleType.FOOT, "calf_l"))
        skel.add_bone(RigBoneNode("ball_l", BoneRoleType.TOE, "foot_l"))

        # Right leg
        skel.add_bone(RigBoneNode("thigh_r", BoneRoleType.LIMB_UPPER, "pelvis"))
        skel.add_bone(RigBoneNode("calf_r", BoneRoleType.LIMB_LOWER, "thigh_r"))
        skel.add_bone(RigBoneNode("foot_r", BoneRoleType.FOOT, "calf_r"))
        skel.add_bone(RigBoneNode("ball_r", BoneRoleType.TOE, "foot_r"))
        return skel

    @classmethod
    def _create_standard_motion_clips(cls, prefix: str) -> List[MotionClip]:
        return [
            MotionClip(f"Anim_{prefix}_Idle", MotionClipType.LOOP, duration_seconds=2.0, is_looping=True),
            MotionClip(f"Anim_{prefix}_Walk", MotionClipType.LOOP, duration_seconds=1.2, is_looping=True, root_motion_enabled=True),
            MotionClip(f"Anim_{prefix}_Run", MotionClipType.LOOP, duration_seconds=0.8, is_looping=True, root_motion_enabled=True),
            MotionClip(f"Anim_{prefix}_Jump", MotionClipType.ONE_SHOT, duration_seconds=1.0, is_looping=False),
        ]

    @classmethod
    def build_biped_humanoid(cls, char_id: str = "Rig_Humanoid_Standard") -> Tuple[CharacterRigDefinition, List[MotionClip], str, str]:
        """1. Humanoide bípedo."""
        skel = cls._create_standard_humanoid_skeleton()
        rig_def = CharacterRigDefinition(char_id, "HUMANOID_STANDARD", skel)
        clips = cls._create_standard_motion_clips(char_id)
        return rig_def, clips, "PHYS_Humanoid_Standard", "CR_Humanoid_Mannequin"

    @classmethod
    def build_armored_character(cls, char_id: str = "Rig_Armored_Knight") -> Tuple[CharacterRigDefinition, List[MotionClip], str, str]:
        """2. Personaje con armadura."""
        skel = cls._create_standard_humanoid_skeleton()
        skel.add_bone(RigBoneNode("pauldron_l", BoneRoleType.HELPER, "clavicle_l", is_deform=False))
        skel.add_bone(RigBoneNode("pauldron_r", BoneRoleType.HELPER, "clavicle_r", is_deform=False))
        rig_def = CharacterRigDefinition(char_id, "HUMANOID_ARMORED", skel)
        clips = cls._create_standard_motion_clips(char_id)
        return rig_def, clips, "PHYS_Armored_Knight", "CR_Armored_Knight"

    @classmethod
    def build_clothed_character(cls, char_id: str = "Rig_Clothed_Mage") -> Tuple[CharacterRigDefinition, List[MotionClip], str, str]:
        """3. Personaje con ropa."""
        skel = cls._create_standard_humanoid_skeleton()
        skel.add_bone(RigBoneNode("robe_skirt_01", BoneRoleType.SECONDARY, "pelvis"))
        skel.add_bone(RigBoneNode("robe_skirt_02", BoneRoleType.SECONDARY, "robe_skirt_01"))
        rig_def = CharacterRigDefinition(char_id, "HUMANOID_CLOTH", skel)
        clips = cls._create_standard_motion_clips(char_id)
        return rig_def, clips, "PHYS_Clothed_Mage", "CR_Clothed_Mage"

    @classmethod
    def build_non_human_creature(cls, char_id: str = "Rig_Creature_Hound") -> Tuple[CharacterRigDefinition, List[MotionClip], str, str]:
        """4. Criatura no humana (Cuadrúpedo)."""
        skel = StandardSkeletonHierarchy()
        skel.add_bone(RigBoneNode("root", BoneRoleType.ROOT, None))
        skel.add_bone(RigBoneNode("pelvis", BoneRoleType.PELVIS, "root"))
        skel.add_bone(RigBoneNode("spine", BoneRoleType.SPINE, "pelvis"))
        skel.add_bone(RigBoneNode("neck", BoneRoleType.NECK, "spine"))
        skel.add_bone(RigBoneNode("head", BoneRoleType.HEAD, "neck"))
        skel.add_bone(RigBoneNode("jaw", BoneRoleType.HEAD, "head"))
        skel.add_bone(RigBoneNode("tail_01", BoneRoleType.SECONDARY, "pelvis"))
        skel.add_bone(RigBoneNode("tail_02", BoneRoleType.SECONDARY, "tail_01"))
        # 4 limbs
        skel.add_bone(RigBoneNode("foreleg_l", BoneRoleType.LIMB_UPPER, "spine"))
        skel.add_bone(RigBoneNode("foreleg_r", BoneRoleType.LIMB_UPPER, "spine"))
        skel.add_bone(RigBoneNode("hindleg_l", BoneRoleType.LIMB_UPPER, "pelvis"))
        skel.add_bone(RigBoneNode("hindleg_r", BoneRoleType.LIMB_UPPER, "pelvis"))

        rig_def = CharacterRigDefinition(char_id, "CREATURE_QUADRUPED", skel)
        clips = [
            MotionClip(f"Anim_{char_id}_Idle", MotionClipType.LOOP, 2.0, is_looping=True),
            MotionClip(f"Anim_{char_id}_Trot", MotionClipType.LOOP, 1.0, is_looping=True, root_motion_enabled=True),
            MotionClip(f"Anim_{char_id}_Bite", MotionClipType.ONE_SHOT, 0.75, is_looping=False),
        ]
        return rig_def, clips, "PHYS_Creature_Hound", "CR_Creature_Hound"

    @classmethod
    def build_weapon_armed_character(cls, char_id: str = "Rig_Armed_Soldier") -> Tuple[CharacterRigDefinition, List[MotionClip], str, str]:
        """5. Personaje con arma."""
        skel = cls._create_standard_humanoid_skeleton()
        skel.add_bone(RigBoneNode("weapon_r", BoneRoleType.WEAPON, "hand_r", is_deform=False))
        rig_def = CharacterRigDefinition(char_id, "HUMANOID_ARMED", skel)
        clips = cls._create_standard_motion_clips(char_id)
        clips.append(MotionClip(f"Anim_{char_id}_Aim", MotionClipType.ADDITIVE, 1.5, is_looping=True))
        return rig_def, clips, "PHYS_Armed_Soldier", "CR_Armed_Soldier"

    @classmethod
    def build_facial_character(cls, char_id: str = "Rig_Facial_Human") -> Tuple[CharacterRigDefinition, List[MotionClip], str, str]:
        """6. Personaje con facial básico."""
        skel = cls._create_standard_humanoid_skeleton()
        skel.add_bone(RigBoneNode("jaw", BoneRoleType.FACIAL, "head"))
        skel.add_bone(RigBoneNode("eye_l", BoneRoleType.FACIAL, "head"))
        skel.add_bone(RigBoneNode("eye_r", BoneRoleType.FACIAL, "head"))
        skel.add_bone(RigBoneNode("eyebrow_l", BoneRoleType.FACIAL, "head"))
        skel.add_bone(RigBoneNode("eyebrow_r", BoneRoleType.FACIAL, "head"))
        rig_def = CharacterRigDefinition(char_id, "HUMANOID_FACIAL", skel)
        clips = cls._create_standard_motion_clips(char_id)
        clips.append(MotionClip(f"Anim_{char_id}_Speak", MotionClipType.MONTAGE, 2.5, is_looping=False))
        return rig_def, clips, "PHYS_Facial_Human", "CR_Facial_Human"

    @classmethod
    def build_secondary_motion_character(cls, char_id: str = "Rig_Secondary_Hero") -> Tuple[CharacterRigDefinition, List[MotionClip], str, str]:
        """7. Personaje con secondary motion (Cabello/colgantes dinámicos)."""
        skel = cls._create_standard_humanoid_skeleton()
        skel.add_bone(RigBoneNode("ponytail_01", BoneRoleType.SECONDARY, "head"))
        skel.add_bone(RigBoneNode("ponytail_02", BoneRoleType.SECONDARY, "ponytail_01"))
        skel.add_bone(RigBoneNode("pouch_waist", BoneRoleType.SECONDARY, "pelvis"))
        rig_def = CharacterRigDefinition(char_id, "HUMANOID_SECONDARY", skel)
        clips = cls._create_standard_motion_clips(char_id)
        return rig_def, clips, "PHYS_Secondary_Hero", "CR_Secondary_Hero"
