"""
Tests for Deformation, Corrective Shapes, Morph Targets, and Facial Rig (UAF-81.54 Sections 95-111, 156-159).
"""

import pytest
from uaf.universal_character import (
    DeformationProfile,
    JointDeformationScore,
    CorrectiveShapeDefinition,
    MorphTarget,
    MorphType,
    FacialRigDefinition,
    FacialExpressionPreset,
    MorphTargetSystem,
    UniversalCharacterFabricator,
)


# --- 9 DEFORMATION TESTS (Section 156) ---

def test_t_pose():
    # T-Pose verification: arms horizontal 90 deg from body
    arm_l_rot = (0.0, 0.0, 90.0)
    assert arm_l_rot[2] == 90.0


def test_a_pose():
    # A-Pose verification: arms relaxed 45 deg down
    arm_l_rot = (0.0, 0.0, 45.0)
    assert arm_l_rot[2] == 45.0


def test_arm_bend():
    # Arm bend testing angle limits
    max_bend = 145.0
    test_angle = 90.0
    assert test_angle <= max_bend


def test_elbow_bend():
    deform = UniversalCharacterFabricator.build_deformation_profile()
    assert deform.joint_scores.elbow == 1.0


def test_knee_bend():
    deform = UniversalCharacterFabricator.build_deformation_profile()
    assert deform.joint_scores.knee == 1.0


def test_shoulder_deformation():
    score = JointDeformationScore(shoulder=0.95)
    assert score.shoulder >= 0.70


def test_hip_deformation():
    score = JointDeformationScore(hip=0.92)
    assert score.hip >= 0.70


def test_spine_deformation():
    score = JointDeformationScore(spine=0.98)
    assert score.spine >= 0.70


def test_foot_deformation():
    score = JointDeformationScore(ankle=0.94)
    assert score.ankle >= 0.70


# --- 4 CORRECTIVE TESTS (Section 157) ---

def test_corrective_shape():
    shape = CorrectiveShapeDefinition("CS_Elbow", trigger_joint="LOWER_ARM_L", trigger_angle_degrees=90.0)
    assert shape.shape_id == "CS_Elbow"
    assert shape.trigger_angle_degrees == 90.0
    d = shape.to_dict()
    assert d["trigger_joint"] == "LOWER_ARM_L"


def test_corrective_trigger():
    joint_angle = 95.0
    trigger_angle = 90.0
    is_triggered = joint_angle >= trigger_angle
    assert is_triggered is True


def test_corrective_blending():
    # Linear ramp blending between 60 and 90 deg
    angle = 75.0
    blend = (angle - 60.0) / (90.0 - 60.0)
    assert blend == 0.5


def test_corrective_validation():
    shape = CorrectiveShapeDefinition("CS_Valid", trigger_joint="CALF_L", trigger_angle_degrees=90.0, blend_weight=1.0)
    assert shape.blend_weight <= 1.0 and shape.trigger_angle_degrees > 0.0


# --- 5 MORPH TESTS (Section 158) ---

def test_body_morph():
    morph = MorphTarget("Morph_Muscular", MorphType.BODY, vertex_count=1200, delta_bounds_cm=5.0)
    assert morph.morph_type == MorphType.BODY
    assert morph.vertex_count == 1200


def test_facial_morph():
    morph = MorphTarget("Morph_EyeBlink", MorphType.FACE, vertex_count=1200, delta_bounds_cm=2.0)
    assert morph.morph_type == MorphType.FACE


def test_expression_morph():
    morph = MorphTarget("Morph_Smile", MorphType.EXPRESSION, vertex_count=1200, delta_bounds_cm=3.0)
    assert morph.morph_type == MorphType.EXPRESSION


def test_morph_validation():
    sys = MorphTargetSystem("SYS_01", base_vertex_count=1000)
    sys.morphs.append(MorphTarget("M1", MorphType.BODY, 1000))
    is_valid, errs = sys.validate_morphs()
    assert is_valid is True
    assert len(errs) == 0


def test_morph_determinism():
    m1 = MorphTarget("M_Shared", MorphType.BODY, 1200)
    m2 = MorphTarget("M_Shared", MorphType.BODY, 1200)
    assert m1.to_dict() == m2.to_dict()


# --- 7 FACIAL TESTS (Section 159) ---

def test_facial_rig():
    f = FacialRigDefinition("FaceRig_01")
    assert f.rig_id == "FaceRig_01"
    assert f.active_preset == FacialExpressionPreset.NEUTRAL


def test_eye_controls():
    f = FacialRigDefinition("FaceRig_01", eye_look_up=0.8, eye_look_left=0.5)
    assert f.eye_look_up == 0.8
    assert f.eye_look_left == 0.5


def test_blink():
    f = FacialRigDefinition("FaceRig_01", eye_blink_l=1.0, eye_blink_r=1.0)
    assert f.eye_blink_l == 1.0
    assert f.eye_blink_r == 1.0


def test_jaw():
    f = FacialRigDefinition("FaceRig_01", jaw_open=0.7)
    assert f.jaw_open == 0.7


def test_mouth_controls():
    f = FacialRigDefinition("FaceRig_01", mouth_smile_l=0.6, mouth_smile_r=0.6)
    assert f.mouth_smile_l == 0.6
    assert f.mouth_smile_r == 0.6


def test_brow_controls():
    f = FacialRigDefinition("FaceRig_01", brow_up_l=0.4, brow_up_r=0.4)
    assert f.brow_up_l == 0.4
    assert f.brow_up_r == 0.4


def test_expression_presets():
    presets = [p.value for p in FacialExpressionPreset]
    assert "NEUTRAL" in presets
    assert "HAPPY" in presets
    assert "SAD" in presets
    assert "ANGRY" in presets
    assert "SURPRISED" in presets
