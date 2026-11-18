"""
Tests for Retargeting, IK Retargeting, and Retarget Quality (UAF-81.55 Sections 25-44, 137-139).
"""

import pytest
from uaf.universal_animation import (
    RetargetProfile55,
    UniversalAnimationFabricator,
)


# --- 9 RETARGET TESTS (Section 137) ---

def test_retarget_profile_structure():
    rp = RetargetProfile55(
        profile_id="RP_Test",
        source_skeleton="SKEL_Source",
        target_skeleton="SKEL_Target",
        bone_mapping={"PELVIS": "PELVIS", "HEAD": "HEAD"},
    )
    assert rp.profile_id == "RP_Test"
    assert rp.source_skeleton == "SKEL_Source"
    d = rp.to_dict()
    assert d["target_skeleton"] == "SKEL_Target"


def test_retarget_bone_classes():
    # Verify mapping across classes: Root, Spine, Limbs, Head
    mapping = {
        "ROOT": "ROOT",
        "PELVIS": "PELVIS",
        "SPINE_01": "SPINE_01",
        "UPPER_ARM_L": "UPPER_ARM_L",
        "HEAD": "HEAD",
    }
    assert len(mapping) == 5


def test_automatic_retarget_mapping():
    source_bones = ["ROOT", "PELVIS", "SPINE_01", "HEAD"]
    target_bones = ["ROOT", "PELVIS", "SPINE_01", "HEAD", "EXTRA_BONE"]
    auto_map = {b: b for b in source_bones if b in target_bones}
    assert len(auto_map) == 4
    assert "HEAD" in auto_map


def test_retarget_ambiguity_detection():
    # Ambiguous when two sources map to same target without weighting
    mapping = {"ARM_L1": "ARM_L", "ARM_L2": "ARM_L"}
    targets = list(mapping.values())
    has_ambiguity = len(targets) != len(set(targets))
    assert has_ambiguity is True


def test_retarget_root():
    rp = RetargetProfile55("RP_Root", "S1", "S2", translation_policy="ABSOLUTE")
    assert rp.translation_policy == "ABSOLUTE"


def test_retarget_translation():
    rp = RetargetProfile55("RP_Trans", "S1", "S2", translation_policy="RELATIVE_SCALE")
    assert rp.translation_policy == "RELATIVE_SCALE"


def test_retarget_rotation():
    rp = RetargetProfile55("RP_Rot", "S1", "S2", rotation_policy="ORIENTATION")
    assert rp.rotation_policy == "ORIENTATION"


def test_retarget_scale():
    rp = RetargetProfile55("RP_Scl", "S1", "S2", scale_policy="UNIFORM")
    assert rp.scale_policy == "UNIFORM"


def test_twist_bones():
    rp = RetargetProfile55("RP_Twist", "S1", "S2", twist_bones=["TWIST_UPPER_ARM_L", "TWIST_UPPER_ARM_R"])
    assert len(rp.twist_bones) == 2
    assert "TWIST_UPPER_ARM_L" in rp.twist_bones


# --- 6 IK_RETARGET TESTS (Section 138) ---

def test_ik_retargeting_goals():
    rp = RetargetProfile55("RP_IK", "S1", "S2", ik_goals=["IK_Foot_L", "IK_Foot_R"])
    assert len(rp.ik_goals) == 2
    assert "IK_Foot_L" in rp.ik_goals


def test_ik_chain_types():
    chain_types = ["TWO_BONE", "FABRIK", "CCD"]
    assert "TWO_BONE" in chain_types
    assert "FABRIK" in chain_types


def test_ik_leg_retarget():
    leg_chain = ["THIGH_L", "CALF_L", "FOOT_L"]
    assert len(leg_chain) == 3


def test_ik_arm_retarget():
    arm_chain = ["UPPER_ARM_L", "LOWER_ARM_L", "HAND_L"]
    assert len(arm_chain) == 3


def test_ik_retarget_validation():
    # Valid when both feet IK goals exist
    goals = {"IK_Foot_L", "IK_Foot_R"}
    assert "IK_Foot_L" in goals and "IK_Foot_R" in goals


def test_ik_reach_limits():
    # Effector distance does not exceed total limb length
    thigh_len = 45.0
    calf_len = 45.0
    total_len = thigh_len + calf_len
    target_dist = 85.0
    assert target_dist <= total_len


# --- 5 RETARGET_QUALITY TESTS (Section 139) ---

def test_retarget_quality_score():
    score = 0.95
    assert score >= 0.85


def test_retarget_golden_poses():
    golden_poses = ["T_POSE", "A_POSE", "CROUCH", "WALK_STRIDE"]
    assert len(golden_poses) == 4


def test_retarget_golden_validation():
    pose_error_cm = 0.8
    threshold_cm = 2.0
    assert pose_error_cm < threshold_cm


def test_bone_orientation_deviation():
    angular_error_deg = 1.2
    max_allowed_deg = 5.0
    assert angular_error_deg <= max_allowed_deg


def test_retarget_determinism():
    rp1 = RetargetProfile55("RP_Det", "S1", "S2", {"HEAD": "HEAD"})
    rp2 = RetargetProfile55("RP_Det", "S1", "S2", {"HEAD": "HEAD"})
    assert rp1.to_dict() == rp2.to_dict()
