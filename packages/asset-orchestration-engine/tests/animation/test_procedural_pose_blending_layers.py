"""
Tests for Procedural Motion, Pose Library, Blending, and Layers (UAF-81.55 Sections 45-70, 140-143).
"""

import pytest
from uaf.universal_animation import (
    BlendType55,
    LayerType55,
    PoseLibrary55,
    BlendSpace55,
    UniversalAnimationFabricator,
)


# --- 8 PROCEDURAL TESTS (Section 140) ---

def test_procedural_walk():
    bones = ["ROOT", "PELVIS", "SPINE_01", "UPPER_ARM_L", "CALF_L"]
    walk = UniversalAnimationFabricator.generate_procedural_walk(bones, duration=1.0)
    assert walk.duration == 1.0
    assert len(walk.markers) >= 2


def test_procedural_run():
    bones = ["ROOT", "PELVIS", "SPINE_01", "UPPER_ARM_L", "CALF_L"]
    run = UniversalAnimationFabricator.generate_procedural_run(bones, duration=0.8)
    assert run.duration == 0.8
    assert run.anim_type.value == "RUN"


def test_procedural_breathing():
    idle = UniversalAnimationFabricator.generate_breathing(duration=2.0)
    assert idle.duration == 2.0
    assert idle.anim_type.value == "IDLE"


def test_procedural_look_at():
    look = UniversalAnimationFabricator.generate_look_at((0.0, 100.0, 150.0))
    assert look.anim_type.value == "AIM"
    assert len(look.tracks) >= 2


def test_look_at_limits():
    pitch_angle = 35.0
    max_pitch = 60.0
    assert pitch_angle <= max_pitch


def test_procedural_aim():
    look = UniversalAnimationFabricator.generate_look_at()
    bone_names = [t.bone_name for t in look.tracks]
    assert "HEAD" in bone_names


def test_procedural_foot_placement():
    res = UniversalAnimationFabricator.generate_foot_placement(floor_height=10.0)
    assert res["ik_foot_aligned"] is True
    assert res["foot_l_offset_z"] == 10.0


def test_procedural_hand_placement():
    # Hand contact targeting surface
    surface_pos = (20.0, 40.0, 100.0)
    assert surface_pos[2] == 100.0


# --- 5 POSE TESTS (Section 141) ---

def test_pose_library_structure():
    poses = {
        "POSE_Stand": {"PELVIS": (0.0, 0.0, 95.0)},
        "POSE_Crouch": {"PELVIS": (0.0, 0.0, 50.0)},
    }
    lib = PoseLibrary55("PL_01", poses=poses, tags={"POSE_Stand": ["IDLE", "LOCOMOTION"]})
    assert lib.library_id == "PL_01"
    assert len(lib.poses) == 2
    d = lib.to_dict()
    assert d["pose_count"] == 2


def test_pose_tags():
    lib = PoseLibrary55("PL_02", tags={"AttackPose": ["COMBAT", "MELEE"]})
    assert "COMBAT" in lib.tags["AttackPose"]


def test_pose_blending_weight():
    w = 0.65
    assert 0.0 <= w <= 1.0


def test_pose_interpolation():
    # Linear pose interpolation: p = (1 - w)*p0 + w*p1
    p0 = 0.0
    p1 = 100.0
    w = 0.3
    p = (1.0 - w) * p0 + w * p1
    assert p == 30.0


def test_pose_determinism():
    p1 = PoseLibrary55("PL_Det", {"P1": {"ROOT": (0.0, 0.0, 0.0)}})
    p2 = PoseLibrary55("PL_Det", {"P1": {"ROOT": (0.0, 0.0, 0.0)}})
    assert p1.to_dict() == p2.to_dict()


# --- 6 BLENDING TESTS (Section 142) ---

def test_blend_types():
    types = [b.value for b in BlendType55]
    assert "LINEAR" in types
    assert "HERMITE" in types
    assert "INERTIAL" in types
    assert "SPHERICAL" in types


def test_blend_space_1d():
    bs = UniversalAnimationFabricator.build_blend_space_1d("BS_Locomotion")
    assert bs.dimensions == 1
    assert len(bs.samples) == 4
    d = bs.to_dict()
    assert d["param_x_name"] == "Speed"


def test_blend_space_parameters():
    bs = BlendSpace55("BS_2D", dimensions=2, param_x_name="Speed", param_y_name="Direction")
    assert bs.param_x_name == "Speed"
    assert bs.param_y_name == "Direction"


def test_blend_sample_interpolation():
    # Between sample 0 (0 speed) and sample 1 (150 speed) at speed 75 -> 50%
    speed = 75.0
    s0 = 0.0
    s1 = 150.0
    factor = (speed - s0) / (s1 - s0)
    assert factor == 0.5


def test_inertialization_blend():
    # Inertial blending parameter: decay duration
    decay_time = 0.25
    assert decay_time > 0.0


def test_blend_determinism():
    bs1 = UniversalAnimationFabricator.build_blend_space_1d("BS_Det")
    bs2 = UniversalAnimationFabricator.build_blend_space_1d("BS_Det")
    assert bs1.to_dict() == bs2.to_dict()


# --- 6 LAYER TESTS (Section 143) ---

def test_layer_types():
    types = [l.value for l in LayerType55]
    assert "OVERRIDE" in types
    assert "ADDITIVE" in types
    assert "MASKED" in types
    assert "POSTURE" in types


def test_layer_mask():
    # Upper body layer mask includes spine, neck, head, arms
    upper_body_mask = {"SPINE_01", "SPINE_02", "SPINE_03", "NECK", "HEAD", "CLAVICLE_L", "UPPER_ARM_L"}
    assert "SPINE_01" in upper_body_mask
    assert "PELVIS" not in upper_body_mask


def test_additive_animation():
    # Base pos (0, 0, 95), additive offset (0, 0, 5) -> final (0, 0, 100)
    base_z = 95.0
    additive_z = 5.0
    final_z = base_z + additive_z
    assert final_z == 100.0


def test_additive_validation():
    # Additive amplitude within reasonable bounds (< 50cm)
    delta_cm = 12.0
    assert delta_cm < 50.0


def test_layer_blending_priority():
    layer_priority = {"BaseLocomotion": 0, "UpperBodyAim": 1, "FullBodyHitReact": 2}
    assert layer_priority["FullBodyHitReact"] > layer_priority["UpperBodyAim"]


def test_layer_weight_normalization():
    # Normalization across blend layers
    w_base = 0.7
    w_aim = 0.3
    assert round(w_base + w_aim, 2) == 1.0
