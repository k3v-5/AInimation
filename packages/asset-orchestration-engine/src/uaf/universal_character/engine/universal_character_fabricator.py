"""
Universal Character Fabricator Engine.
Synthesizes Canonical Golden Presets and procedural characters, rigs, skinning, and deformers.
UAF-81.54 Sections 3-136, 169, 170, 173.
"""

from typing import Dict, Any, List, Optional, Tuple
import math

from ...core.hashing.canonical_hasher import CanonicalHasher
from ..models.definition import (
    CharacterSpecies,
    CharacterArchetype,
    BodyShape,
    ProportionNormalization,
    AnatomicalRegionType,
    SymmetryType,
    FootVariant,
    ClothingType,
    ClothingFit,
    ArmorComponentType,
    AccessoryType,
    AccessorySocket,
    HairType,
    IKType,
    ConstraintType,
    SkinningMethod,
    WeightStrategy,
    MorphType,
    FacialExpressionPreset,
    BodyProportions,
    AttachmentPoint,
    BodyComponent,
    HeadDefinition,
    EyeDefinition,
    EarDefinition,
    NoseDefinition,
    TeethDefinition,
    MouthDefinition,
    HandDefinition,
    FootDefinition,
    CreatureComponentDefinition,
    ClothingDefinition,
    ArmorDefinition,
    AccessoryDefinition,
    HairDefinition,
    BoneDefinition,
    RestPose,
    SkeletonDefinition,
    IKChain,
    ConstraintDefinition,
    RigDefinition,
    VertexWeight,
    SkinningDefinition,
    JointDeformationScore,
    CorrectiveShapeDefinition,
    DeformationProfile,
    MorphTarget,
    FacialRigDefinition,
    MorphTargetSystem,
    RetargetProfile,
    PoseDefinition,
    RagdollBody,
    RagdollConstraint,
    RagdollDefinition,
    CharacterCollisionDefinition,
    CharacterLODChain,
    CharacterNanitePolicy,
    CharacterDefinition,
    CharacterSnapshot,
    CharacterDiff,
)
from ..validation.universal_character_validator import CharacterValidator, CharacterValidationReport
from ..package.universal_character_package import ProductionReadyCharacter


class UniversalCharacterFabricator:
    """
    Core fabrication engine for Universal Characters, Rigging, Skinning, and Deformation.
    """

    @classmethod
    def build_humanoid_skeleton(cls, skeleton_id: str = "SKEL_Humanoid") -> SkeletonDefinition:
        """
        Builds standard humanoid skeleton conforming to Section 65.
        """
        bones = [
            BoneDefinition("ROOT", parent=None, rest_transform=(0.0, 0.0, 0.0), length=0.0, semantic_role="ROOT"),
            BoneDefinition("PELVIS", parent="ROOT", rest_transform=(0.0, 0.0, 95.0), length=15.0, semantic_role="PELVIS"),
            BoneDefinition("SPINE_01", parent="PELVIS", rest_transform=(0.0, 0.0, 110.0), length=12.0, semantic_role="SPINE"),
            BoneDefinition("SPINE_02", parent="SPINE_01", rest_transform=(0.0, 0.0, 122.0), length=12.0, semantic_role="SPINE"),
            BoneDefinition("SPINE_03", parent="SPINE_02", rest_transform=(0.0, 0.0, 134.0), length=14.0, semantic_role="SPINE"),
            BoneDefinition("NECK", parent="SPINE_03", rest_transform=(0.0, 0.0, 148.0), length=10.0, semantic_role="NECK"),
            BoneDefinition("HEAD", parent="NECK", rest_transform=(0.0, 0.0, 158.0), length=20.0, semantic_role="HEAD"),
            
            # Left arm
            BoneDefinition("CLAVICLE_L", parent="SPINE_03", rest_transform=(10.0, 0.0, 145.0), length=12.0, semantic_role="CLAVICLE"),
            BoneDefinition("UPPER_ARM_L", parent="CLAVICLE_L", rest_transform=(22.0, 0.0, 145.0), length=30.0, semantic_role="ARM"),
            BoneDefinition("LOWER_ARM_L", parent="UPPER_ARM_L", rest_transform=(52.0, 0.0, 145.0), length=26.0, semantic_role="FOREARM"),
            BoneDefinition("HAND_L", parent="LOWER_ARM_L", rest_transform=(78.0, 0.0, 145.0), length=18.0, semantic_role="HAND"),
            
            # Right arm
            BoneDefinition("CLAVICLE_R", parent="SPINE_03", rest_transform=(-10.0, 0.0, 145.0), length=12.0, semantic_role="CLAVICLE"),
            BoneDefinition("UPPER_ARM_R", parent="CLAVICLE_R", rest_transform=(-22.0, 0.0, 145.0), length=30.0, semantic_role="ARM"),
            BoneDefinition("LOWER_ARM_R", parent="UPPER_ARM_R", rest_transform=(-52.0, 0.0, 145.0), length=26.0, semantic_role="FOREARM"),
            BoneDefinition("HAND_R", parent="LOWER_ARM_R", rest_transform=(-78.0, 0.0, 145.0), length=18.0, semantic_role="HAND"),
            
            # Left leg
            BoneDefinition("THIGH_L", parent="PELVIS", rest_transform=(12.0, 0.0, 90.0), length=42.0, semantic_role="THIGH"),
            BoneDefinition("CALF_L", parent="THIGH_L", rest_transform=(12.0, 0.0, 48.0), length=40.0, semantic_role="CALF"),
            BoneDefinition("FOOT_L", parent="CALF_L", rest_transform=(12.0, 5.0, 8.0), length=18.0, semantic_role="FOOT"),
            BoneDefinition("TOE_L", parent="FOOT_L", rest_transform=(12.0, 18.0, 2.0), length=8.0, semantic_role="TOE"),
            
            # Right leg
            BoneDefinition("THIGH_R", parent="PELVIS", rest_transform=(-12.0, 0.0, 90.0), length=42.0, semantic_role="THIGH"),
            BoneDefinition("CALF_R", parent="THIGH_R", rest_transform=(-12.0, 0.0, 48.0), length=40.0, semantic_role="CALF"),
            BoneDefinition("FOOT_R", parent="CALF_R", rest_transform=(-12.0, 5.0, 8.0), length=18.0, semantic_role="FOOT"),
            BoneDefinition("TOE_R", parent="FOOT_R", rest_transform=(-12.0, 18.0, 2.0), length=8.0, semantic_role="TOE"),
        ]
        rest_pose = RestPose({b.name: b.rest_transform for b in bones})
        return SkeletonDefinition(skeleton_id=skeleton_id, bones=bones, rest_pose=rest_pose)

    @classmethod
    def build_quadruped_skeleton(cls, skeleton_id: str = "SKEL_Quadruped") -> SkeletonDefinition:
        """
        Builds quadruped skeleton conforming to Section 43, 66.
        """
        bones = [
            BoneDefinition("ROOT", parent=None, rest_transform=(0.0, 0.0, 0.0), length=0.0, semantic_role="ROOT"),
            BoneDefinition("PELVIS", parent="ROOT", rest_transform=(0.0, -30.0, 70.0), length=15.0, semantic_role="PELVIS"),
            BoneDefinition("SPINE_01", parent="PELVIS", rest_transform=(0.0, -15.0, 72.0), length=15.0, semantic_role="SPINE"),
            BoneDefinition("SPINE_02", parent="SPINE_01", rest_transform=(0.0, 0.0, 74.0), length=15.0, semantic_role="SPINE"),
            BoneDefinition("CHEST", parent="SPINE_02", rest_transform=(0.0, 15.0, 75.0), length=15.0, semantic_role="CHEST"),
            BoneDefinition("NECK", parent="CHEST", rest_transform=(0.0, 28.0, 85.0), length=12.0, semantic_role="NECK"),
            BoneDefinition("HEAD", parent="NECK", rest_transform=(0.0, 38.0, 95.0), length=15.0, semantic_role="HEAD"),
            
            # Front limbs (Arms/Legs)
            BoneDefinition("SHOULDER_FL", parent="CHEST", rest_transform=(15.0, 20.0, 70.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("KNEE_FL", parent="SHOULDER_FL", rest_transform=(15.0, 20.0, 45.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("PAW_FL", parent="KNEE_FL", rest_transform=(15.0, 20.0, 5.0), length=10.0, semantic_role="PAW"),
            BoneDefinition("SHOULDER_FR", parent="CHEST", rest_transform=(-15.0, 20.0, 70.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("KNEE_FR", parent="SHOULDER_FR", rest_transform=(-15.0, 20.0, 45.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("PAW_FR", parent="KNEE_FR", rest_transform=(-15.0, 20.0, 5.0), length=10.0, semantic_role="PAW"),
            
            # Back limbs
            BoneDefinition("HIP_BL", parent="PELVIS", rest_transform=(15.0, -30.0, 70.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("KNEE_BL", parent="HIP_BL", rest_transform=(15.0, -30.0, 45.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("PAW_BL", parent="KNEE_BL", rest_transform=(15.0, -30.0, 5.0), length=10.0, semantic_role="PAW"),
            BoneDefinition("HIP_BR", parent="PELVIS", rest_transform=(-15.0, -30.0, 70.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("KNEE_BR", parent="HIP_BR", rest_transform=(-15.0, -30.0, 45.0), length=25.0, semantic_role="LIMB"),
            BoneDefinition("PAW_BR", parent="KNEE_BR", rest_transform=(-15.0, -30.0, 5.0), length=10.0, semantic_role="PAW"),
            
            # Tail
            BoneDefinition("TAIL_01", parent="PELVIS", rest_transform=(0.0, -42.0, 68.0), length=12.0, semantic_role="TAIL"),
            BoneDefinition("TAIL_02", parent="TAIL_01", rest_transform=(0.0, -54.0, 62.0), length=12.0, semantic_role="TAIL"),
            BoneDefinition("TAIL_03", parent="TAIL_02", rest_transform=(0.0, -66.0, 55.0), length=12.0, semantic_role="TAIL"),
        ]
        rest_pose = RestPose({b.name: b.rest_transform for b in bones})
        return SkeletonDefinition(skeleton_id=skeleton_id, bones=bones, rest_pose=rest_pose)

    @classmethod
    def build_multi_limb_skeleton(cls, skeleton_id: str = "SKEL_MultiLimb") -> SkeletonDefinition:
        """
        Builds multi-limb skeleton with 4 arms and 2 legs (Section 43, 66).
        """
        skel = cls.build_humanoid_skeleton(skeleton_id)
        # Add secondary arms
        skel.bones.extend([
            BoneDefinition("UPPER_ARM_L2", parent="SPINE_02", rest_transform=(20.0, 0.0, 125.0), length=28.0, semantic_role="ARM_EXTRA"),
            BoneDefinition("LOWER_ARM_L2", parent="UPPER_ARM_L2", rest_transform=(48.0, 0.0, 125.0), length=24.0, semantic_role="FOREARM_EXTRA"),
            BoneDefinition("HAND_L2", parent="LOWER_ARM_L2", rest_transform=(72.0, 0.0, 125.0), length=16.0, semantic_role="HAND_EXTRA"),
            BoneDefinition("UPPER_ARM_R2", parent="SPINE_02", rest_transform=(-20.0, 0.0, 125.0), length=28.0, semantic_role="ARM_EXTRA"),
            BoneDefinition("LOWER_ARM_R2", parent="UPPER_ARM_R2", rest_transform=(-48.0, 0.0, 125.0), length=24.0, semantic_role="FOREARM_EXTRA"),
            BoneDefinition("HAND_R2", parent="LOWER_ARM_R2", rest_transform=(-72.0, 0.0, 125.0), length=16.0, semantic_role="HAND_EXTRA"),
        ])
        skel.rest_pose.bone_transforms.update({b.name: b.rest_transform for b in skel.bones})
        return skel

    @classmethod
    def build_rig(
        cls,
        skeleton: SkeletonDefinition,
        rig_id: str = "RIG_Humanoid",
        has_foot_ik: bool = True,
        has_hand_ik: bool = True
    ) -> RigDefinition:
        """
        Builds RigDefinition with IKChains and constraints (Sections 72-85).
        """
        controls = ["CTRL_Root", "CTRL_Pelvis", "CTRL_Spine", "CTRL_Head"]
        ik_chains = []
        constraints = []
        bone_names = set(skeleton.bone_names)

        # Foot IKs
        if has_foot_ik and "THIGH_L" in bone_names and "FOOT_L" in bone_names and "CALF_L" in bone_names:
            ik_chains.append(IKChain("IK_Leg_L", root="THIGH_L", effector="FOOT_L", pole="CALF_L", chain_length=2, ik_type=IKType.TWO_BONE))
            controls.append("CTRL_IK_Foot_L")
        if has_foot_ik and "THIGH_R" in bone_names and "FOOT_R" in bone_names and "CALF_R" in bone_names:
            ik_chains.append(IKChain("IK_Leg_R", root="THIGH_R", effector="FOOT_R", pole="CALF_R", chain_length=2, ik_type=IKType.TWO_BONE))
            controls.append("CTRL_IK_Foot_R")

        # Hand IKs
        if has_hand_ik and "UPPER_ARM_L" in bone_names and "HAND_L" in bone_names and "LOWER_ARM_L" in bone_names:
            ik_chains.append(IKChain("IK_Arm_L", root="UPPER_ARM_L", effector="HAND_L", pole="LOWER_ARM_L", chain_length=2, ik_type=IKType.TWO_BONE))
            controls.append("CTRL_IK_Hand_L")
        if has_hand_ik and "UPPER_ARM_R" in bone_names and "HAND_R" in bone_names and "LOWER_ARM_R" in bone_names:
            ik_chains.append(IKChain("IK_Arm_R", root="UPPER_ARM_R", effector="HAND_R", pole="LOWER_ARM_R", chain_length=2, ik_type=IKType.TWO_BONE))
            controls.append("CTRL_IK_Hand_R")

        # Basic constraints
        constraints.append(ConstraintDefinition("C_PelvisFollow", ConstraintType.COPY_TRANSFORM, "CTRL_Pelvis", "PELVIS", influence=1.0))
        constraints.append(ConstraintDefinition("C_HeadAim", ConstraintType.AIM, "CTRL_Head", "HEAD", influence=0.8))

        return RigDefinition(
            rig_id=rig_id,
            skeleton_id=skeleton.skeleton_id,
            controls=controls,
            ik_chains=ik_chains,
            constraints=constraints,
            foot_ik_enabled=has_foot_ik,
            hand_ik_enabled=has_hand_ik,
        )

    @classmethod
    def build_skinning(
        cls,
        skeleton: SkeletonDefinition,
        vertex_count: int = 1200,
        skinning_id: str = "SKIN_Standard"
    ) -> SkinningDefinition:
        """
        Builds perfectly normalized SkinningDefinition (Sections 86-94).
        """
        weights_per_vertex = {}
        bone_names = skeleton.bone_names
        primary_bone = bone_names[1] if len(bone_names) > 1 else bone_names[0]
        secondary_bone = bone_names[2] if len(bone_names) > 2 else primary_bone

        for v in range(vertex_count):
            # 2 influences: 0.7 to primary, 0.3 to secondary
            weights_per_vertex[v] = [
                VertexWeight(primary_bone, 0.7),
                VertexWeight(secondary_bone, 0.3),
            ]

        return SkinningDefinition(
            skinning_id=skinning_id,
            method=SkinningMethod.LINEAR_BLEND,
            strategy=WeightStrategy.DISTANCE,
            max_influences_per_vertex=4,
            weights_per_vertex=weights_per_vertex,
        )

    @classmethod
    def build_deformation_profile(
        cls,
        profile_id: str = "DEF_Standard",
        preserve_volume: bool = True
    ) -> DeformationProfile:
        """
        Builds DeformationProfile with corrective shapes (Sections 95-103).
        """
        correctives = [
            CorrectiveShapeDefinition("CS_Elbow_L_90", trigger_joint="LOWER_ARM_L", trigger_angle_degrees=90.0, blend_weight=1.0),
            CorrectiveShapeDefinition("CS_Knee_L_90", trigger_joint="CALF_L", trigger_angle_degrees=90.0, blend_weight=1.0),
        ]
        return DeformationProfile(
            profile_id=profile_id,
            volume_loss_percent=2.1,
            surface_stretch_percent=2.8,
            surface_compression_percent=1.9,
            joint_scores=JointDeformationScore(),
            preserve_volume=preserve_volume,
            correctives=correctives,
        )

    @classmethod
    def build_morph_system(
        cls,
        base_vertex_count: int = 1200,
        system_id: str = "MORPH_Standard",
        has_facial: bool = True
    ) -> MorphTargetSystem:
        """
        Builds MorphTargetSystem and FacialRigDefinition (Sections 104-111).
        """
        morphs = [
            MorphTarget("Morph_Body_Muscular", MorphType.BODY, base_vertex_count, delta_bounds_cm=4.5),
            MorphTarget("Morph_Body_Slim", MorphType.BODY, base_vertex_count, delta_bounds_cm=3.8),
        ]
        if has_facial:
            morphs.extend([
                MorphTarget("Morph_Face_Smile", MorphType.EXPRESSION, base_vertex_count, delta_bounds_cm=2.2),
                MorphTarget("Morph_Face_Frown", MorphType.EXPRESSION, base_vertex_count, delta_bounds_cm=2.0),
                MorphTarget("Morph_Eye_Blink_L", MorphType.FACE, base_vertex_count, delta_bounds_cm=1.5),
                MorphTarget("Morph_Eye_Blink_R", MorphType.FACE, base_vertex_count, delta_bounds_cm=1.5),
            ])

        facial_rig = FacialRigDefinition("FacialRig_01", active_preset=FacialExpressionPreset.NEUTRAL)
        return MorphTargetSystem(
            system_id=system_id,
            base_vertex_count=base_vertex_count,
            morphs=morphs,
            facial_rig=facial_rig,
        )

    @classmethod
    def build_collision(
        cls,
        skeleton: SkeletonDefinition,
        collision_id: str = "COL_Standard"
    ) -> CharacterCollisionDefinition:
        """
        Builds CharacterCollisionDefinition with Ragdoll constraints (Sections 118-121).
        """
        bodies = [
            RagdollBody("PELVIS", "CAPSULE", mass_kg=15.0),
            RagdollBody("SPINE_02", "CAPSULE", mass_kg=20.0),
            RagdollBody("HEAD", "CAPSULE", mass_kg=6.0),
            RagdollBody("UPPER_ARM_L", "CAPSULE", mass_kg=5.0),
            RagdollBody("UPPER_ARM_R", "CAPSULE", mass_kg=5.0),
            RagdollBody("THIGH_L", "CAPSULE", mass_kg=12.0),
            RagdollBody("THIGH_R", "CAPSULE", mass_kg=12.0),
        ]
        constraints = [
            RagdollConstraint("SPINE_01", angular_limits=(-30.0, 30.0)),
            RagdollConstraint("NECK", angular_limits=(-40.0, 40.0)),
            RagdollConstraint("UPPER_ARM_L", angular_limits=(-80.0, 80.0)),
            RagdollConstraint("THIGH_L", angular_limits=(-70.0, 70.0)),
        ]
        ragdoll = RagdollDefinition("Ragdoll_Main", bodies=bodies, constraints=constraints)
        return CharacterCollisionDefinition(
            collision_id=collision_id,
            capsules_count=len(bodies),
            boxes_count=2,
            ragdoll=ragdoll,
        )

    @classmethod
    def build_retarget_profile(
        cls,
        source_id: str,
        target_id: str,
        profile_id: str = "RETARGET_Humanoid"
    ) -> RetargetProfile:
        """
        Builds RetargetProfile (Sections 112-114).
        """
        mapping = {
            "ROOT": "ROOT",
            "PELVIS": "PELVIS",
            "SPINE_01": "SPINE_01",
            "HEAD": "HEAD",
            "UPPER_ARM_L": "UPPER_ARM_L",
            "HAND_L": "HAND_L",
            "UPPER_ARM_R": "UPPER_ARM_R",
            "HAND_R": "HAND_R",
            "THIGH_L": "THIGH_L",
            "FOOT_L": "FOOT_L",
            "THIGH_R": "THIGH_R",
            "FOOT_R": "FOOT_R",
        }
        return RetargetProfile(
            profile_id=profile_id,
            source_skeleton=source_id,
            target_skeleton=target_id,
            bone_mapping=mapping,
        )

    # --- THE 10 GOLDEN PRESETS (Section 170) ---

    @classmethod
    def build_golden_human_male(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_HUMAN_MALE",
            species=CharacterSpecies.HUMAN,
            archetype=CharacterArchetype.HUMAN,
            proportions=BodyProportions(height=182.0, shoulder_width=48.0, chest_depth=30.0, waist_width=33.0, hip_width=36.0),
            body_shape=BodyShape.ATHLETIC,
            gender_presentation="MALE",
            seed=101,
        )
        skel = cls.build_humanoid_skeleton("SKEL_HumanMale")
        rig = cls.build_rig(skel, "RIG_HumanMale")
        skin = cls.build_skinning(skel, 1400, "SKIN_HumanMale")
        deform = cls.build_deformation_profile("DEF_HumanMale")
        morphs = cls.build_morph_system(1400, "MORPH_HumanMale", has_facial=True)
        col = cls.build_collision(skel, "COL_HumanMale")
        cloth = [ClothingDefinition("CLOTH_MaleShirt", ClothingType.SHIRT, ClothingFit.REGULAR)]
        retarget = cls.build_retarget_profile(skel.skeleton_id, "SKEL_UE5_Manny")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, clothing=cloth, collision=col, retarget=retarget, vertex_count=1400, triangle_count=2800)

    @classmethod
    def build_golden_human_female(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_HUMAN_FEMALE",
            species=CharacterSpecies.HUMAN,
            archetype=CharacterArchetype.HUMAN,
            proportions=BodyProportions(height=168.0, shoulder_width=40.0, chest_depth=26.0, waist_width=27.0, hip_width=37.0),
            body_shape=BodyShape.SLIM,
            gender_presentation="FEMALE",
            seed=102,
        )
        skel = cls.build_humanoid_skeleton("SKEL_HumanFemale")
        rig = cls.build_rig(skel, "RIG_HumanFemale")
        skin = cls.build_skinning(skel, 1300, "SKIN_HumanFemale")
        deform = cls.build_deformation_profile("DEF_HumanFemale")
        morphs = cls.build_morph_system(1300, "MORPH_HumanFemale", has_facial=True)
        col = cls.build_collision(skel, "COL_HumanFemale")
        cloth = [ClothingDefinition("CLOTH_FemaleDress", ClothingType.DRESS, ClothingFit.REGULAR)]
        hair = HairDefinition("HAIR_FemaleLong", HairType.MESH_HAIR, scalp_coverage=0.9)
        retarget = cls.build_retarget_profile(skel.skeleton_id, "SKEL_UE5_Quinn")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, clothing=cloth, hair=hair, collision=col, retarget=retarget, vertex_count=1300, triangle_count=2600)

    @classmethod
    def build_golden_humanoid(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_HUMANOID",
            species=CharacterSpecies.HUMANOID,
            archetype=CharacterArchetype.HUMANOID,
            proportions=BodyProportions(height=195.0, shoulder_width=52.0, arm_length=85.0),
            body_shape=BodyShape.LEAN,
            seed=103,
        )
        skel = cls.build_humanoid_skeleton("SKEL_HumanoidAlien")
        rig = cls.build_rig(skel, "RIG_HumanoidAlien")
        skin = cls.build_skinning(skel, 1200, "SKIN_HumanoidAlien")
        deform = cls.build_deformation_profile("DEF_HumanoidAlien")
        morphs = cls.build_morph_system(1200, "MORPH_HumanoidAlien", has_facial=True)
        col = cls.build_collision(skel, "COL_HumanoidAlien")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, collision=col, vertex_count=1200, triangle_count=2400)

    @classmethod
    def build_golden_robot(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_ROBOT",
            species=CharacterSpecies.ROBOT,
            archetype=CharacterArchetype.ROBOT,
            proportions=BodyProportions(height=210.0, shoulder_width=55.0, chest_depth=35.0),
            body_shape=BodyShape.HEAVY,
            material_profile="METALLIC_MECHANICAL",
            seed=104,
        )
        skel = cls.build_humanoid_skeleton("SKEL_RobotMechanical")
        rig = cls.build_rig(skel, "RIG_RobotMechanical")
        skin = cls.build_skinning(skel, 1600, "SKIN_RobotMechanical")
        deform = cls.build_deformation_profile("DEF_RobotMechanical", preserve_volume=False)
        morphs = cls.build_morph_system(1600, "MORPH_RobotMechanical", has_facial=False)
        armor = [
            ArmorDefinition("ARMOR_RobotChest", ArmorComponentType.CHEST, clearance=0.8, mass_kg=12.0),
            ArmorDefinition("ARMOR_RobotHelmet", ArmorComponentType.HELMET, clearance=0.5, mass_kg=4.0),
        ]
        col = cls.build_collision(skel, "COL_RobotMechanical")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, armor=armor, collision=col, vertex_count=1600, triangle_count=3200)

    @classmethod
    def build_golden_quadruped(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_QUADRUPED",
            species=CharacterSpecies.ANIMAL,
            archetype=CharacterArchetype.QUADRUPED,
            proportions=BodyProportions(height=95.0, shoulder_width=35.0, arm_length=50.0, leg_length=50.0),
            body_shape=BodyShape.AVERAGE,
            seed=105,
        )
        skel = cls.build_quadruped_skeleton("SKEL_QuadrupedBeast")
        rig = cls.build_rig(skel, "RIG_QuadrupedBeast", has_foot_ik=False, has_hand_ik=False)
        skin = cls.build_skinning(skel, 1100, "SKIN_QuadrupedBeast")
        deform = cls.build_deformation_profile("DEF_QuadrupedBeast")
        morphs = cls.build_morph_system(1100, "MORPH_QuadrupedBeast", has_facial=False)
        col = cls.build_collision(skel, "COL_QuadrupedBeast")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, collision=col, vertex_count=1100, triangle_count=2200)

    @classmethod
    def build_golden_creature(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_CREATURE",
            species=CharacterSpecies.CREATURE,
            archetype=CharacterArchetype.BIPED_CREATURE,
            proportions=BodyProportions(height=240.0, shoulder_width=65.0, chest_depth=42.0),
            body_shape=BodyShape.MUSCULAR,
            seed=106,
        )
        skel = cls.build_humanoid_skeleton("SKEL_CreatureGargoyle")
        # Add horns & tail
        skel.bones.extend([
            BoneDefinition("HORN_L", parent="HEAD", rest_transform=(8.0, 0.0, 175.0), length=15.0, semantic_role="HORN"),
            BoneDefinition("HORN_R", parent="HEAD", rest_transform=(-8.0, 0.0, 175.0), length=15.0, semantic_role="HORN"),
            BoneDefinition("TAIL_01", parent="PELVIS", rest_transform=(0.0, -15.0, 90.0), length=20.0, semantic_role="TAIL"),
            BoneDefinition("TAIL_02", parent="TAIL_01", rest_transform=(0.0, -32.0, 80.0), length=20.0, semantic_role="TAIL"),
        ])
        skel.rest_pose.bone_transforms.update({b.name: b.rest_transform for b in skel.bones})
        rig = cls.build_rig(skel, "RIG_CreatureGargoyle")
        skin = cls.build_skinning(skel, 1800, "SKIN_CreatureGargoyle")
        deform = cls.build_deformation_profile("DEF_CreatureGargoyle")
        morphs = cls.build_morph_system(1800, "MORPH_CreatureGargoyle", has_facial=True)
        col = cls.build_collision(skel, "COL_CreatureGargoyle")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, collision=col, vertex_count=1800, triangle_count=3600)

    @classmethod
    def build_golden_multi_limb(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_MULTI_LIMB",
            species=CharacterSpecies.MUTANT,
            archetype=CharacterArchetype.MULTI_LIMB,
            proportions=BodyProportions(height=190.0, shoulder_width=50.0),
            seed=107,
        )
        skel = cls.build_multi_limb_skeleton("SKEL_MultiLimbMutant")
        rig = cls.build_rig(skel, "RIG_MultiLimbMutant")
        skin = cls.build_skinning(skel, 2000, "SKIN_MultiLimbMutant")
        deform = cls.build_deformation_profile("DEF_MultiLimbMutant")
        morphs = cls.build_morph_system(2000, "MORPH_MultiLimbMutant", has_facial=False)
        col = cls.build_collision(skel, "COL_MultiLimbMutant")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, collision=col, vertex_count=2000, triangle_count=4000)

    @classmethod
    def build_golden_armored_character(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_ARMORED_CHARACTER",
            species=CharacterSpecies.HUMAN,
            archetype=CharacterArchetype.HUMAN,
            proportions=BodyProportions(height=188.0, shoulder_width=52.0),
            body_shape=BodyShape.HEAVY,
            seed=108,
        )
        skel = cls.build_humanoid_skeleton("SKEL_ArmoredKnight")
        rig = cls.build_rig(skel, "RIG_ArmoredKnight")
        skin = cls.build_skinning(skel, 1500, "SKIN_ArmoredKnight")
        deform = cls.build_deformation_profile("DEF_ArmoredKnight")
        morphs = cls.build_morph_system(1500, "MORPH_ArmoredKnight", has_facial=False)
        armors = [
            ArmorDefinition("ARMOR_KnightChest", ArmorComponentType.CHEST, clearance=1.2, mass_kg=15.0),
            ArmorDefinition("ARMOR_KnightHelmet", ArmorComponentType.HELMET, clearance=0.8, mass_kg=4.5),
            ArmorDefinition("ARMOR_KnightShoulderL", ArmorComponentType.SHOULDER, clearance=1.0, mass_kg=3.0),
            ArmorDefinition("ARMOR_KnightShinL", ArmorComponentType.SHIN, clearance=0.6, mass_kg=2.5),
        ]
        col = cls.build_collision(skel, "COL_ArmoredKnight")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, armor=armors, collision=col, vertex_count=1500, triangle_count=3000)

    @classmethod
    def build_golden_clothed_character(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_CLOTHED_CHARACTER",
            species=CharacterSpecies.HUMAN,
            archetype=CharacterArchetype.HUMAN,
            proportions=BodyProportions(height=175.0, shoulder_width=44.0),
            body_shape=BodyShape.AVERAGE,
            seed=109,
        )
        skel = cls.build_humanoid_skeleton("SKEL_ClothedCitizen")
        rig = cls.build_rig(skel, "RIG_ClothedCitizen")
        skin = cls.build_skinning(skel, 1350, "SKIN_ClothedCitizen")
        deform = cls.build_deformation_profile("DEF_ClothedCitizen")
        morphs = cls.build_morph_system(1350, "MORPH_ClothedCitizen", has_facial=True)
        clothing = [
            ClothingDefinition("CLOTH_Jacket", ClothingType.JACKET, ClothingFit.LOOSE, minimum_clearance=0.8),
            ClothingDefinition("CLOTH_Pants", ClothingType.PANTS, ClothingFit.REGULAR, minimum_clearance=0.4),
            ClothingDefinition("CLOTH_Boots", ClothingType.BOOTS, ClothingFit.REGULAR, minimum_clearance=0.5),
        ]
        accessories = [
            AccessoryDefinition("ACC_Belt", AccessoryType.BELT, AccessorySocket.WAIST),
            AccessoryDefinition("ACC_Backpack", AccessoryType.BACKPACK, AccessorySocket.BACK),
        ]
        col = cls.build_collision(skel, "COL_ClothedCitizen")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, clothing=clothing, accessories=accessories, collision=col, vertex_count=1350, triangle_count=2700)

    @classmethod
    def build_golden_facial_character(cls) -> ProductionReadyCharacter:
        char_def = CharacterDefinition(
            character_id="GOLDEN_FACIAL_CHARACTER",
            species=CharacterSpecies.HUMAN,
            archetype=CharacterArchetype.HUMAN,
            proportions=BodyProportions(height=178.0, head_size=25.0),
            body_shape=BodyShape.AVERAGE,
            seed=110,
        )
        skel = cls.build_humanoid_skeleton("SKEL_FacialActor")
        rig = cls.build_rig(skel, "RIG_FacialActor")
        skin = cls.build_skinning(skel, 1400, "SKIN_FacialActor")
        deform = cls.build_deformation_profile("DEF_FacialActor")
        morphs = cls.build_morph_system(1400, "MORPH_FacialActor", has_facial=True)
        # Add rich expressive morphs
        morphs.morphs.extend([
            MorphTarget("Morph_Face_Surprise", MorphType.EXPRESSION, 1400, delta_bounds_cm=2.5),
            MorphTarget("Morph_Face_Angry", MorphType.EXPRESSION, 1400, delta_bounds_cm=2.1),
            MorphTarget("Morph_Face_Fear", MorphType.EXPRESSION, 1400, delta_bounds_cm=2.3),
            MorphTarget("Morph_Face_Disgust", MorphType.EXPRESSION, 1400, delta_bounds_cm=1.8),
        ])
        morphs.facial_rig.mouth_smile_l = 0.5
        morphs.facial_rig.mouth_smile_r = 0.5
        col = cls.build_collision(skel, "COL_FacialActor")

        return cls.fabricate(char_def, skel, rig, skin, deform, morphs, collision=col, vertex_count=1400, triangle_count=2800)

    # --- FABRICATE ---

    @classmethod
    def fabricate(
        cls,
        character_def: CharacterDefinition,
        skeleton: SkeletonDefinition,
        rig: RigDefinition,
        skinning: SkinningDefinition,
        deformation: DeformationProfile,
        morphs: MorphTargetSystem,
        components: Optional[List[BodyComponent]] = None,
        clothing: Optional[List[ClothingDefinition]] = None,
        armor: Optional[List[ArmorDefinition]] = None,
        accessories: Optional[List[AccessoryDefinition]] = None,
        hair: Optional[HairDefinition] = None,
        collision: Optional[CharacterCollisionDefinition] = None,
        lod_chain: Optional[CharacterLODChain] = None,
        retarget: Optional[RetargetProfile] = None,
        vertex_count: int = 1200,
        triangle_count: int = 2400,
        skeletal_mesh_path: Optional[str] = None,
        skeleton_path: Optional[str] = None,
        physics_asset_path: Optional[str] = None,
    ) -> ProductionReadyCharacter:
        """
        Synthesizes and validates a ProductionReadyCharacter.
        """
        cid = character_def.character_id
        sm_path = skeletal_mesh_path or f"/Game/Characters/SK_{cid}.uasset"
        sk_path = skeleton_path or f"/Game/Characters/SKEL_{cid}.uasset"
        phys_path = physics_asset_path or f"/Game/Characters/PHYS_{cid}.uasset"

        comp_list = components or [
            BodyComponent(f"{cid}_Torso", "TORSO", f"SM_{cid}_Torso"),
            BodyComponent(f"{cid}_Head", "HEAD", f"SM_{cid}_Head"),
            BodyComponent(f"{cid}_Limbs", "UPPER_ARM_L", f"SM_{cid}_Limbs"),
        ]
        cloth_list = clothing or []
        armor_list = armor or []
        acc_list = accessories or []
        col = collision or cls.build_collision(skeleton, f"COL_{cid}")
        lods = lod_chain or CharacterLODChain()

        report = CharacterValidator.validate_character(
            character_def=character_def,
            skeleton=skeleton,
            rig=rig,
            skinning=skinning,
            deformation=deformation,
            morphs=morphs,
            clothings=cloth_list,
            armors=armor_list,
            collision=col,
            lod_chain=lods,
            skeletal_mesh_path=sm_path,
            skeleton_path=sk_path,
            physics_asset_path=phys_path,
        )

        return ProductionReadyCharacter(
            character_def=character_def,
            skeleton=skeleton,
            rig=rig,
            skinning=skinning,
            deformation=deformation,
            morphs=morphs,
            components=comp_list,
            clothing=cloth_list,
            armor=armor_list,
            accessories=acc_list,
            hair=hair,
            collision=col,
            lod_chain=lods,
            retarget=retarget,
            validation_report=report,
            skeletal_mesh_path=sm_path,
            skeleton_path=sk_path,
            physics_asset_path=phys_path,
            vertex_count=vertex_count,
            triangle_count=triangle_count,
        )

    # --- CACHE & DIFF (Sections 134-136) ---

    @classmethod
    def generate_cache_key(cls, character: ProductionReadyCharacter) -> str:
        payload = {
            "char_def": character.character_def.to_dict(),
            "skeleton": character.skeleton.to_dict(),
            "rig": character.rig.to_dict(),
            "skinning_method": character.skinning.method.value,
        }
        return CanonicalHasher.compute_hash(payload)

    @classmethod
    def snapshot_character(cls, character: ProductionReadyCharacter, snapshot_id: str = "SNAP_01") -> CharacterSnapshot:
        return CharacterSnapshot(
            snapshot_id=snapshot_id,
            character_definition_hash=CanonicalHasher.compute_hash(character.character_def.to_dict()),
            component_hash=CanonicalHasher.compute_hash([c.to_dict() for c in character.components]),
            skeleton_hash=CanonicalHasher.compute_hash(character.skeleton.to_dict()),
            rig_hash=CanonicalHasher.compute_hash(character.rig.to_dict()),
        )

    @classmethod
    def diff_characters(cls, char_a: ProductionReadyCharacter, char_b: ProductionReadyCharacter, diff_id: str = "DIFF_01") -> CharacterDiff:
        skel_changed = (
            len(char_a.skeleton.bones) != len(char_b.skeleton.bones) or
            char_a.skeleton.bone_names != char_b.skeleton.bone_names
        )
        rig_changed = (
            char_a.rig.controls != char_b.rig.controls or
            len(char_a.rig.ik_chains) != len(char_b.rig.ik_chains)
        )
        morphs_changed = len(char_a.morphs.morphs) != len(char_b.morphs.morphs)
        lod_changed = char_a.lod_chain.lod_count != char_b.lod_chain.lod_count

        changed_components = []
        names_a = {c.component_id for c in char_a.components}
        names_b = {c.component_id for c in char_b.components}
        diff_names = names_a.symmetric_difference(names_b)
        changed_components.extend(list(diff_names))

        return CharacterDiff(
            diff_id=diff_id,
            changed_components=changed_components,
            skeleton_changed=skel_changed,
            rig_changed=rig_changed,
            morphs_changed=morphs_changed,
            lod_changed=lod_changed,
        )
