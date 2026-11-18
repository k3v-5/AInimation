"""
SkeletonBuilder generates canonical skeleton hierarchies from anatomical landmarks.
UAF-81.5 Sections 8, 10, 11, 12, 15.
"""

from typing import Dict, Any, List, Optional
from .bone import BoneDefinition, BoneRole
from .skeleton_definition import CharacterSkeletonDefinition, BindPoseType, SkeletonArchetype
from ...geometry.anatomy.landmarks import LandmarkSystem


class SkeletonBuilder:
    """
    Builds structurally sound and anatomically validated skeletons aligned with Landmarks.
    """
    @classmethod
    def build_humanoid_skeleton(
        cls,
        skeleton_id: str,
        landmarks: Optional[LandmarkSystem] = None,
        height_meters: float = 1.80,
        bind_pose: BindPoseType = BindPoseType.A_POSE,
        include_twist_bones: bool = True,
    ) -> CharacterSkeletonDefinition:
        lms = landmarks or LandmarkSystem.create_default_humanoid(height_meters)
        lm = lms.landmarks

        bones: Dict[str, BoneDefinition] = {}

        # 1. Root
        bones["root"] = BoneDefinition(
            bone_id="root",
            name="root",
            role=BoneRole.ROOT,
            position=[0.0, 0.0, 0.0],
            parent_id=None,
            deformation_enabled=False,
        )

        # 2. Pelvis
        pelvis_pos = lm.get("pelvis", [0.0, 0.0, height_meters * 0.53])
        bones["pelvis"] = BoneDefinition(
            bone_id="pelvis",
            name="pelvis",
            role=BoneRole.PELVIS,
            position=pelvis_pos,
            parent_id="root",
        )

        # 3. Spine chain
        spine_pos = lm.get("spine", [0.0, 0.0, height_meters * 0.65])
        bones["spine_01"] = BoneDefinition(
            bone_id="spine_01",
            name="spine_01",
            role=BoneRole.SPINE_01,
            position=spine_pos,
            parent_id="pelvis",
        )

        chest_pos = lm.get("chest", [0.0, 0.0, height_meters * 0.75])
        bones["chest"] = BoneDefinition(
            bone_id="chest",
            name="chest",
            role=BoneRole.CHEST,
            position=chest_pos,
            parent_id="spine_01",
        )

        neck_pos = lm.get("neck", [0.0, 0.0, height_meters * 0.85])
        bones["neck"] = BoneDefinition(
            bone_id="neck",
            name="neck",
            role=BoneRole.NECK,
            position=neck_pos,
            parent_id="chest",
        )

        head_pos = lm.get("head", [0.0, 0.0, height_meters * 0.93])
        bones["head"] = BoneDefinition(
            bone_id="head",
            name="head",
            role=BoneRole.HEAD,
            position=head_pos,
            parent_id="neck",
        )

        # 4. Arms (Left & Right)
        for side, s_code in [("_L", "L"), ("_R", "R")]:
            clavicle_pos = lm.get(f"shoulder{side}", [(-0.15 if s_code == "L" else 0.15), 0.0, height_meters * 0.82])
            clav_id = f"clavicle{side}"
            bones[clav_id] = BoneDefinition(
                bone_id=clav_id,
                name=clav_id,
                role=BoneRole.CLAVICLE_L if s_code == "L" else BoneRole.CLAVICLE_R,
                position=clavicle_pos,
                parent_id="chest",
            )

            uarm_id = f"upperarm{side}"
            bones[uarm_id] = BoneDefinition(
                bone_id=uarm_id,
                name=uarm_id,
                role=BoneRole.UPPER_ARM_L if s_code == "L" else BoneRole.UPPER_ARM_R,
                position=clavicle_pos,
                parent_id=clav_id,
            )

            larm_pos = lm.get(f"elbow{side}", [(-0.25 if s_code == "L" else 0.25), 0.0, height_meters * 0.62])
            larm_id = f"lowerarm{side}"
            bones[larm_id] = BoneDefinition(
                bone_id=larm_id,
                name=larm_id,
                role=BoneRole.LOWER_ARM_L if s_code == "L" else BoneRole.LOWER_ARM_R,
                position=larm_pos,
                parent_id=uarm_id,
            )

            hand_pos = lm.get(f"wrist{side}", [(-0.35 if s_code == "L" else 0.35), 0.0, height_meters * 0.45])
            hand_id = f"hand{side}"
            bones[hand_id] = BoneDefinition(
                bone_id=hand_id,
                name=hand_id,
                role=BoneRole.HAND_L if s_code == "L" else BoneRole.HAND_R,
                position=hand_pos,
                parent_id=larm_id,
            )

        # 5. Legs (Left & Right)
        for side, s_code in [("_L", "L"), ("_R", "R")]:
            thigh_pos = lm.get(f"hip{side}", [(-0.1 if s_code == "L" else 0.1), 0.0, height_meters * 0.50])
            thigh_id = f"thigh{side}"
            bones[thigh_id] = BoneDefinition(
                bone_id=thigh_id,
                name=thigh_id,
                role=BoneRole.THIGH_L if s_code == "L" else BoneRole.THIGH_R,
                position=thigh_pos,
                parent_id="pelvis",
            )

            calf_pos = lm.get(f"knee{side}", [(-0.1 if s_code == "L" else 0.1), 0.0, height_meters * 0.28])
            calf_id = f"calf{side}"
            bones[calf_id] = BoneDefinition(
                bone_id=calf_id,
                name=calf_id,
                role=BoneRole.CALF_L if s_code == "L" else BoneRole.CALF_R,
                position=calf_pos,
                parent_id=thigh_id,
            )

            foot_pos = lm.get(f"ankle{side}", [(-0.1 if s_code == "L" else 0.1), 0.0, height_meters * 0.05])
            foot_id = f"foot{side}"
            bones[foot_id] = BoneDefinition(
                bone_id=foot_id,
                name=foot_id,
                role=BoneRole.FOOT_L if s_code == "L" else BoneRole.FOOT_R,
                position=foot_pos,
                parent_id=calf_id,
            )

        return CharacterSkeletonDefinition(
            skeleton_id=skeleton_id,
            root_bone_id="root",
            archetype=SkeletonArchetype.HUMANOID,
            bind_pose=bind_pose,
            bones=bones,
            scale=height_meters,
        )
