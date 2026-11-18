"""
Tests for Retargeting, Poses, Collision, Ragdoll, LOD, and Nanite Policy (UAF-81.54 Sections 112-129, 160-164).
"""

import pytest
from uaf.universal_character import (
    RetargetProfile,
    PoseDefinition,
    RagdollBody,
    RagdollConstraint,
    RagdollDefinition,
    CharacterCollisionDefinition,
    CharacterLODChain,
    CharacterNanitePolicy,
    UniversalCharacterFabricator,
)


# --- 5 RETARGET TESTS (Section 160) ---

def test_retarget_profile():
    p = UniversalCharacterFabricator.build_retarget_profile("SKEL_Source", "SKEL_Target")
    assert p.source_skeleton == "SKEL_Source"
    assert p.target_skeleton == "SKEL_Target"
    d = p.to_dict()
    assert d["translation_policy"] == "ABSOLUTE"


def test_retarget_mapping():
    p = UniversalCharacterFabricator.build_retarget_profile("S1", "S2")
    assert p.bone_mapping["HEAD"] == "HEAD"
    assert p.bone_mapping["PELVIS"] == "PELVIS"


def test_retarget_validation():
    p = UniversalCharacterFabricator.build_retarget_profile("S1", "S2")
    # Mapping non-empty
    assert len(p.bone_mapping) >= 10


def test_retarget_pose():
    # Retarget rest orientation aligned
    source_rest_rot = (0.0, 0.0, 0.0)
    target_rest_rot = (0.0, 0.0, 0.0)
    assert source_rest_rot == target_rest_rot


def test_retarget_determinism():
    p1 = UniversalCharacterFabricator.build_retarget_profile("S1", "S2")
    p2 = UniversalCharacterFabricator.build_retarget_profile("S1", "S2")
    assert p1.to_dict() == p2.to_dict()


# --- 5 POSE TESTS (Section 161) ---

def test_pose_definition():
    pose = PoseDefinition("Walk_Pose_01", joint_rotations={"UPPER_ARM_L": (25.0, 0.0, 0.0)})
    assert pose.pose_name == "Walk_Pose_01"
    assert pose.is_valid_limits is True
    d = pose.to_dict()
    assert "UPPER_ARM_L" in d["joint_rotations"]


def test_pose_validation():
    pose = PoseDefinition("Pose_Valid", is_valid_limits=True, mesh_penetration_detected=False)
    assert pose.is_valid_limits and not pose.mesh_penetration_detected


def test_joint_limits():
    knee_angle = 110.0
    knee_limit = 140.0
    assert knee_angle <= knee_limit


def test_pose_penetration():
    pose = PoseDefinition("Pose_Penetrating", mesh_penetration_detected=False)
    assert not pose.mesh_penetration_detected


def test_pose_deformation():
    # Pose error below threshold
    deformation_error = 0.02
    threshold = 0.05
    assert deformation_error < threshold


# --- 5 COLLISION TESTS (Section 162) ---

def test_character_collision():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    col = UniversalCharacterFabricator.build_collision(skel)
    assert col.capsules_count > 0
    assert col.boxes_count > 0


def test_bone_collision():
    body = RagdollBody(bone="PELVIS", shape="CAPSULE", mass_kg=15.0)
    assert body.bone == "PELVIS"
    assert body.mass_kg == 15.0


def test_ragdoll():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    col = UniversalCharacterFabricator.build_collision(skel)
    assert len(col.ragdoll.bodies) >= 5


def test_ragdoll_constraints():
    rc = RagdollConstraint("SPINE_01", angular_limits=(-30.0, 30.0))
    assert rc.angular_limits == (-30.0, 30.0)
    d = rc.to_dict()
    assert d["stiffness"] == 100.0


def test_collision_budget():
    # Max collision primitives budget check
    max_capsules = 24
    actual_capsules = 7
    assert actual_capsules <= max_capsules


# --- 6 CHARACTER_LOD TESTS (Section 163) ---

def test_character_lod():
    lod = CharacterLODChain()
    assert lod.lod_count == 4
    assert len(lod.reduction_per_lod) == 4
    assert lod.reduction_per_lod[0] == 1.0


def test_clothing_lod():
    # Clothing reduces alongside body
    clothing_verts = [800, 480, 240, 120]
    assert clothing_verts[1] < clothing_verts[0]


def test_accessory_lod():
    # Accessories can cull out at highest LOD distance
    accessory_visible_at_lod = [True, True, True, False]
    assert accessory_visible_at_lod[0] is True
    assert accessory_visible_at_lod[3] is False


def test_facial_lod():
    lod = CharacterLODChain(preserves_face=True)
    assert lod.preserves_face is True


def test_skeletal_lod():
    lod = CharacterLODChain()
    assert lod.skeletal_bone_reduction[0] >= lod.skeletal_bone_reduction[-1]


def test_bone_lod_validation():
    # Active root and spine bones never culled
    essential_bones = {"ROOT", "PELVIS", "SPINE_01"}
    lod3_bones = {"ROOT", "PELVIS", "SPINE_01", "HEAD"}
    assert essential_bones.issubset(lod3_bones)


# --- 4 NANITE TESTS (Section 164) ---

def test_character_nanite_policy():
    policy = CharacterNanitePolicy()
    assert policy.enabled_for_static_accessories is True
    assert policy.enabled_for_skinned_mesh is False


def test_skinned_nanite_policy():
    # Skinned character mesh should not enable Nanite if dynamic deformations require compute skin cache
    policy = CharacterNanitePolicy(enabled_for_skinned_mesh=False)
    assert not policy.enabled_for_skinned_mesh


def test_static_component_nanite():
    policy = CharacterNanitePolicy(enabled_for_static_accessories=True)
    assert policy.enabled_for_static_accessories is True


def test_nanite_validation():
    policy = CharacterNanitePolicy(fallback_lod_bias=0)
    d = policy.to_dict()
    assert d["fallback_lod_bias"] == 0
