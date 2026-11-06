"""
Unit and Integration Tests for Advanced Kinematics, IK, Joint Limits, and Anti-Collision Engine.
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from backend.ai.advanced_kinematics import (
    BipedalWalkCycleParams,
    CollisionCapsule,
    IKChainSpec,
    JointLimit,
    KinematicRigResult,
    build_blender_kinematic_constraints_script,
    generate_bipedal_walk_cycle,
    get_standard_collision_hulls,
    get_standard_joint_limits,
    resolve_capsule_interpenetration,
    solve_two_bone_ik,
)


def test_joint_limits_integrity() -> None:
    """Validate mechanical & anatomical joint limit boundaries."""
    limits = get_standard_joint_limits("bipedal_robot")
    assert len(limits) >= 12

    limit_map = {l.bone_name: l for l in limits}
    assert "LowerLeg_L" in limit_map
    assert "LowerLeg_R" in limit_map
    assert "LowerArm_L" in limit_map

    # Knee must never bend forward (max pitch must be <= 0)
    knee_l = limit_map["LowerLeg_L"]
    assert knee_l.max_pitch_deg <= 0.0
    assert knee_l.min_pitch_deg < -90.0
    assert knee_l.min_roll_deg == 0.0 and knee_l.max_roll_deg == 0.0

    # Elbow must never hyperextend (min pitch >= 0)
    elbow_l = limit_map["LowerArm_L"]
    assert elbow_l.min_pitch_deg >= 0.0
    assert elbow_l.max_pitch_deg > 90.0


def test_collision_hulls_definitions() -> None:
    """Validate collision capsules protecting against mesh interpenetration."""
    hulls = get_standard_collision_hulls("bipedal_robot")
    assert len(hulls) >= 4

    hull_names = [h.name for h in hulls]
    assert "Hull_Torso" in hull_names
    assert "Hull_Pelvis" in hull_names
    assert "Hull_Thigh_L" in hull_names

    for h in hulls:
        assert h.radius > 0.0
        assert len(h.start_point) == 3
        assert len(h.end_point) == 3


def test_two_bone_ik_analytical_solution() -> None:
    """Verify two-bone IK solver with exact mathematical geometric distances."""
    root = (0.0, 0.0, 1.0)
    target = (0.0, 0.0, 0.10)  # Foot planted near ground
    pole = (0.0, 1.0, 0.55)    # Knee pointing forward (+Y)
    l1 = 0.45
    l2 = 0.45

    mid_pos, angle_root, angle_mid = solve_two_bone_ik(
        root_pos=root,
        target_pos=target,
        pole_pos=pole,
        length_1=l1,
        length_2=l2,
    )

    # Mid joint (knee) must be pointing towards positive Y (pole direction)
    assert mid_pos[1] > 0.0

    # Distance from root to mid must equal L1 (within floating point precision)
    d_root_mid = math.dist(root, mid_pos)
    assert pytest.approx(d_root_mid, rel=1e-3) == l1

    # Distance from mid to target must equal L2
    d_mid_target = math.dist(mid_pos, target)
    assert pytest.approx(d_mid_target, rel=1e-3) == l2

    assert angle_mid > 0.0


def test_capsule_interpenetration_resolution() -> None:
    """Verify that points penetrating collision hulls are projected safely outward."""
    hull = CollisionCapsule(
        name="Test_Torso",
        parent_bone="Spine",
        start_point=(0.0, 0.0, 0.0),
        end_point=(0.0, 0.0, 1.0),
        radius=0.20,
    )

    # 1. Point outside
    outside_pt = (0.50, 0.0, 0.50)
    resolved_out, penetrated = resolve_capsule_interpenetration(outside_pt, pos_radius=0.05, capsule=hull)
    assert penetrated is False
    assert resolved_out == outside_pt

    # 2. Point penetrating inside the capsule
    inside_pt = (0.05, 0.0, 0.50)
    resolved_in, penetrated_in = resolve_capsule_interpenetration(inside_pt, pos_radius=0.05, capsule=hull)
    assert penetrated_in is True
    # Must now be at least radius + pos_radius away from axis
    radial_dist = math.hypot(resolved_in[0], resolved_in[1])
    assert radial_dist >= 0.25


def test_walk_cycle_generation() -> None:
    """Validate procedural bipedal walk cycle keyframes."""
    params = BipedalWalkCycleParams(
        total_frames=48,
        fps=24,
        step_length=0.40,
        pelvis_bob_m=0.04,
        is_robotic=True,
    )
    tracks = generate_bipedal_walk_cycle(params, skeleton_type="bipedal_robot")

    assert "Root" in tracks
    assert "UpperLeg_L" in tracks
    assert "LowerLeg_L" in tracks
    assert "UpperArm_L" in tracks
    assert len(tracks["Root"]) == 48

    # Verify that knee never bends in reverse throughout the entire walk cycle
    knee_keys = tracks["LowerLeg_L"]
    for k in knee_keys:
        pitch = k["rotation_euler_deg"][0]
        assert pitch <= 0.001, f"Knee hyperextended at frame {k['frame']}: {pitch}"

    # Verify arms swing contralaterally
    arm_l_0 = tracks["UpperArm_L"][0]["rotation_euler_deg"][0]
    arm_r_0 = tracks["UpperArm_R"][0]["rotation_euler_deg"][0]
    # Opposite sign or phase offset
    assert abs(arm_l_0 + arm_r_0) < 5.0


def test_blender_script_generation() -> None:
    """Validate generated Blender Python script syntax and content."""
    script = build_blender_kinematic_constraints_script(
        skeleton_type="bipedal_robot",
        enable_ik=True,
        enable_joint_limits=True,
    )
    assert "LIMIT_ROTATION" in script
    assert "LimitRot_" in script
    assert "IK_Leg_" in script
    assert "import bpy" in script
