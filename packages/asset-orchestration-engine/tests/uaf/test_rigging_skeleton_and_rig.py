"""
Tests for Skeleton Hierarchy, Bone Roles, and Rig Definition.
UAF-81.5 Sections 4, 5, 6, 8, 10, 18, 22.
"""

from uaf.rigging.skeleton.bone import BoneRole, BoneDefinition
from uaf.rigging.skeleton.skeleton_definition import (
    BindPoseType,
    SkeletonArchetype,
    CharacterSkeletonDefinition,
)
from uaf.rigging.skeleton.skeleton_builder import SkeletonBuilder
from uaf.rigging.rig.ik_constraint import IKType, IKConstraint
from uaf.rigging.rig.rig_definition import RigLayer, RigDefinition
from uaf.geometry.anatomy.landmarks import LandmarkSystem


def test_bone_definition_and_serialization():
    bone = BoneDefinition(
        bone_id="spine_01",
        name="spine_01",
        role=BoneRole.SPINE_01,
        position=[0.0, 0.0, 1.1],
        parent_id="pelvis",
    )
    assert bone.role == BoneRole.SPINE_01
    assert bone.deformation_enabled is True
    data = bone.to_dict()
    assert data["bone_id"] == "spine_01"
    assert data["parent_id"] == "pelvis"


def test_skeleton_builder_humanoid_hierarchy():
    lms = LandmarkSystem.create_default_humanoid(height_meters=1.80)
    skeleton = SkeletonBuilder.build_humanoid_skeleton(
        skeleton_id="skel_hero_01",
        landmarks=lms,
        height_meters=1.80,
    )

    assert skeleton.bone_count >= 19
    assert skeleton.root_bone_id == "root"
    assert skeleton.archetype == SkeletonArchetype.HUMANOID
    assert len(skeleton.skeleton_hash) == 64

    # Verify standard hierarchy
    root_bone = skeleton.get_bone("root")
    assert root_bone.parent_id is None

    pelvis_bone = skeleton.get_bone("pelvis")
    assert pelvis_bone.parent_id == "root"

    head_bone = skeleton.get_bone("head")
    assert head_bone.parent_id == "neck"

    # Arms and Legs symmetry
    assert skeleton.get_bone("upperarm_L") is not None
    assert skeleton.get_bone("upperarm_R") is not None
    assert skeleton.get_bone("thigh_L") is not None
    assert skeleton.get_bone("thigh_R") is not None


def test_rig_definition_and_ik_chains():
    rig = RigDefinition.create_standard_humanoid_rig("rig_hero_01", "skel_hero_01")
    assert rig.rig_id == "rig_hero_01"
    assert len(rig.ik_chains) == 4  # 2 Arms, 2 Legs
    assert len(rig.control_bones) >= 8
    assert RigLayer.IK.value in [l.value if hasattr(l, "value") else l for l in rig.layers]

    # Verify Hand IK chain
    hand_ik = [c for c in rig.ik_chains if c.chain_id == "IK_Arm_L"][0]
    assert hand_ik.ik_type == IKType.HAND_IK
    assert hand_ik.root_bone == "upperarm_L"
    assert hand_ik.tip_bone == "hand_L"
