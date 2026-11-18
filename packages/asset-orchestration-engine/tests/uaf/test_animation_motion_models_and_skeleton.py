"""
Tests for Animation Motion Models and Skeleton Hierarchy.
UAF-81.23 Sections 3, 4, 5, 7, 8, 98, 99.
"""

from uaf.animation_motion.models.skeleton import (
    BoneRoleType,
    RigBoneNode,
    StandardSkeletonHierarchy,
    CharacterRigDefinition,
)
from uaf.animation_motion.models.motion import (
    MotionClipType,
    MotionClip,
)


def test_character_rig_definition_and_hashing():
    skel = StandardSkeletonHierarchy()
    skel.add_bone(RigBoneNode("root", BoneRoleType.ROOT, None))
    skel.add_bone(RigBoneNode("pelvis", BoneRoleType.PELVIS, "root"))
    skel.add_bone(RigBoneNode("spine", BoneRoleType.SPINE, "pelvis"))

    assert skel.find_root().bone_id == "root"
    assert skel.has_cycles() is False

    rig_def = CharacterRigDefinition("Rig_Hero_Test", "HUMANOID_STANDARD", skel, seed=123456)
    assert rig_def.character_id == "Rig_Hero_Test"
    assert len(rig_def.definition_hash) == 64
    data = rig_def.to_dict()
    assert data["rig_profile"] == "HUMANOID_STANDARD"


def test_skeleton_hierarchy_cycle_and_root_detection():
    skel = StandardSkeletonHierarchy()
    # Cycle: A -> B -> C -> A
    skel.add_bone(RigBoneNode("Bone_A", BoneRoleType.SPINE, "Bone_C"))
    skel.add_bone(RigBoneNode("Bone_B", BoneRoleType.SPINE, "Bone_A"))
    skel.add_bone(RigBoneNode("Bone_C", BoneRoleType.SPINE, "Bone_B"))

    assert skel.has_cycles() is True
    assert skel.find_root() is None


def test_motion_clip():
    clip = MotionClip("Anim_Sprint", MotionClipType.LOOP, duration_seconds=0.75, is_looping=True, root_motion_enabled=True)
    assert clip.is_looping is True
    assert clip.root_motion_enabled is True
    data = clip.to_dict()
    assert data["duration_seconds"] == 0.75
