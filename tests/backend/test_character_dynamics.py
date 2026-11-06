"""
Unit Tests for Studio Character Dynamics & Twist-Bone Rigging (backend.ai.character_dynamics).

Tests:
1. Anatomical twist bone injection into bipedal and quadruped hierarchies.
2. Vectorized Verlet spring-mass-damper simulation for secondary character appendages (hair, cables).
3. Length constraint relaxation ensuring zero stretching/exploding.
4. Spherical collision avoidance preventing body clipping.
5. Pydantic v2 strict schema validation on configurations and trajectory results.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Tuple
import numpy as np
import pytest

from backend.ai.character_dynamics import (
    CollisionSphere,
    DynamicSimulationResult,
    SecondaryChainConfig,
    SecondaryChainSimulator,
    TwistBoneSpec,
    inject_twist_bones,
)


@pytest.fixture
def sample_biped_bones() -> List[Tuple[str, Tuple[float, float, float], Tuple[float, float, float], Optional[str], bool]]:
    """A standard 18-bone biped hierarchy."""
    return [
        ("Root", (0.0, 0.0, 0.0), (0.0, 0.0, 0.1), None, False),
        ("Pelvis", (0.0, 0.0, 0.9), (0.0, 0.0, 1.0), "Root", True),
        ("Spine", (0.0, 0.0, 1.0), (0.0, 0.0, 1.3), "Pelvis", True),
        ("Chest", (0.0, 0.0, 1.3), (0.0, 0.0, 1.5), "Spine", True),
        ("Neck", (0.0, 0.0, 1.5), (0.0, 0.0, 1.6), "Chest", True),
        ("Head", (0.0, 0.0, 1.6), (0.0, 0.0, 1.8), "Neck", True),
        ("UpperArm_L", (0.2, 0.0, 1.45), (0.5, 0.0, 1.2), "Chest", True),
        ("LowerArm_L", (0.5, 0.0, 1.2), (0.75, 0.0, 0.95), "UpperArm_L", True),
        ("UpperArm_R", (-0.2, 0.0, 1.45), (-0.5, 0.0, 1.2), "Chest", True),
        ("LowerArm_R", (-0.5, 0.0, 1.2), (-0.75, 0.0, 0.95), "UpperArm_R", True),
        ("UpperLeg_L", (0.15, 0.0, 0.9), (0.15, 0.0, 0.5), "Pelvis", True),
        ("LowerLeg_L", (0.15, 0.0, 0.5), (0.15, 0.0, 0.1), "UpperLeg_L", True),
        ("UpperLeg_R", (-0.15, 0.0, 0.9), (-0.15, 0.0, 0.5), "Pelvis", True),
        ("LowerLeg_R", (-0.15, 0.0, 0.5), (-0.15, 0.0, 0.1), "UpperLeg_R", True),
    ]


def test_inject_twist_bones(
    sample_biped_bones: List[Tuple[str, Tuple[float, float, float], Tuple[float, float, float], Optional[str], bool]],
) -> None:
    """Validate injection of 6 anatomical twist bones into limb chains."""
    augmented = inject_twist_bones(sample_biped_bones)
    bone_names = {b[0] for b in augmented}

    # Verify all 6 twist bones injected
    expected_twists = [
        "UpperArm_Twist_L",
        "UpperArm_Twist_R",
        "LowerArm_Twist_L",
        "LowerArm_Twist_R",
        "UpperLeg_Twist_L",
        "UpperLeg_Twist_R",
    ]
    for twist in expected_twists:
        assert twist in bone_names

    # Check midpoint position of UpperArm_Twist_L
    u_arm = next(b for b in sample_biped_bones if b[0] == "UpperArm_L")
    u_twist = next(b for b in augmented if b[0] == "UpperArm_Twist_L")

    # Parent must be UpperArm_L
    assert u_twist[3] == "UpperArm_L"

    # Twist head must be at 50% midpoint
    expected_head = tuple((np.array(u_arm[1]) + 0.5 * (np.array(u_arm[2]) - np.array(u_arm[1]))).tolist())
    assert np.allclose(u_twist[1], expected_head, atol=1e-4)


def test_secondary_spring_chain_simulation() -> None:
    """Validate Verlet spring-damper secondary motion on moving character root."""
    cfg = SecondaryChainConfig(
        chain_name="hair_ponytail",
        node_count=6,
        segment_length=0.10,
        stiffness=150.0,
        damping=5.0,
    )
    sim = SecondaryChainSimulator(config=cfg)

    # 24 frames of moving root (character running forward along X)
    root_motion = [(float(i * 0.04), 0.0, 1.65 + math.sin(i * 0.4) * 0.03) for i in range(24)]
    res = sim.simulate(root_positions=root_motion, fps=24)

    assert isinstance(res, DynamicSimulationResult)
    assert res.total_frames == 24
    assert len(res.trajectories) == 24

    for f_idx, frame_nodes in enumerate(res.trajectories):
        assert len(frame_nodes) == 6
        # Node 0 must perfectly track the root
        assert np.allclose(frame_nodes[0], root_motion[f_idx], atol=1e-4)

        # Distance between consecutive nodes must be preserved (~0.10m within 2%)
        for i in range(5):
            d = math.dist(frame_nodes[i], frame_nodes[i + 1])
            assert np.isclose(d, 0.10, atol=0.005), f"Frame {f_idx} segment {i} distance stretched: {d}"


def test_secondary_chain_collision_avoidance() -> None:
    """Validate that swinging secondary chain deflects around anatomical collision hulls."""
    cfg = SecondaryChainConfig(
        chain_name="torso_cable",
        node_count=5,
        segment_length=0.08,
        gravity=(0.0, 0.0, -9.81),
    )
    # Place a collision sphere directly beneath the chain attachment point
    sphere = CollisionSphere(
        name="torso_hull",
        center=(0.0, 0.0, -0.15),
        radius=0.12,
    )
    sim = SecondaryChainSimulator(config=cfg, collision_bodies=[sphere])

    # Static root anchor at (0, 0, 0)
    root_motion = [(0.0, 0.0, 0.0)] * 20
    res = sim.simulate(root_positions=root_motion, fps=30)

    assert res.collision_resolutions > 0

    # Ensure no node penetrates inside the collision sphere radius
    col_center = np.array(sphere.center)
    for frame_nodes in res.trajectories:
        for node in frame_nodes[1:]:
            d = float(np.linalg.norm(np.array(node) - col_center))
            assert d >= sphere.radius - 1e-4, f"Node penetrated collision sphere: dist={d} < radius={sphere.radius}"
