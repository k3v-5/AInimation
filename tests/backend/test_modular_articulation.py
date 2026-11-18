"""
Unit and Integration Tests for Modular Articulation & Zero-Deformation Rigid Engine.
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from backend.ai.modular_articulation import (
    ColorCriteria,
    DeformationPolicy,
    ModularDecompositionRecipe,
    ModularPartCategory,
    ModularPartDefinition,
    SpatialBounds,
    generate_blender_modular_articulation_script,
    get_modular_recipe,
    verify_rigid_isometry,
)


def test_spatial_bounds_containment() -> None:
    """Validate spatial bounding box logic."""
    bounds = SpatialBounds(min_x=-0.2, max_x=0.2, min_z=1.0, max_z=1.5)
    assert bounds.contains(0.0, 0.0, 1.2) is True
    assert bounds.contains(0.3, 0.0, 1.2) is False  # outside X
    assert bounds.contains(0.0, 0.0, 0.8) is False  # outside Z


def test_color_criteria_matching() -> None:
    """Validate chroma matching for texture-aware segmentation."""
    red_crit = ColorCriteria(min_r=0.6, max_r=1.0, min_g=0.0, max_g=0.3, min_b=0.0, max_b=0.3)
    assert red_crit.matches(0.85, 0.1, 0.1) is True
    assert red_crit.matches(0.2, 0.8, 0.2) is False  # Green


def test_preset_recipes_integrity() -> None:
    """Validate puppet, robot, and armored humanoid modular presets."""
    for style in ("puppet_ragdoll", "bipedal_robot", "armored_humanoid"):
        recipe = get_modular_recipe(style)
        assert len(recipe.parts) >= 2
        assert recipe.bridge_edge_threshold_m > 0.0
        assert recipe.character_style == style

    # Specific puppet check: must have isometric rigid head and axe
    puppet = get_modular_recipe("puppet_ragdoll")
    part_names = {p.name: p for p in puppet.parts}
    assert "Part_Head_Complete" in part_names
    assert "Part_Axe_Complete" in part_names

    head = part_names["Part_Head_Complete"]
    assert head.deformation_policy == DeformationPolicy.ISOMETRIC_RIGID
    assert head.target_bone == "Head"

    axe = part_names["Part_Axe_Complete"]
    assert axe.deformation_policy == DeformationPolicy.ISOMETRIC_RIGID
    assert axe.target_bone == "Spine"

    # Specific robot check: all limbs must be mechanical links
    robot = get_modular_recipe("bipedal_robot")
    for p in robot.parts:
        assert p.deformation_policy == DeformationPolicy.MECHANICAL_LINK


def test_rigid_isometry_mathematical_proof() -> None:
    """
    Prove that rigid SE(3) transformation preserves pairwise Euclidean distances
    with zero variance (sigma^2 = 0.000000), while non-isometric transforms fail.
    """
    # 50 random vertices forming a rigid component (e.g. helmet or axe)
    np.random.seed(42)
    verts = np.random.uniform(-0.5, 0.5, size=(50, 3)).astype(np.float64)

    # Valid SE(3) transform: 3D rotation (35 deg yaw, 20 deg pitch) + translation
    yaw = math.radians(35.0)
    pitch = math.radians(20.0)
    r_yaw = np.array([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1],
    ])
    r_pitch = np.array([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)],
    ])
    rot = r_yaw @ r_pitch
    trans = np.array([0.25, -0.15, 0.40])

    se3_matrix = np.eye(4, dtype=np.float64)
    se3_matrix[:3, :3] = rot
    se3_matrix[:3, 3] = trans

    max_distortion = verify_rigid_isometry(verts, se3_matrix)
    assert max_distortion < 1e-12, f"Expected 0 distortion, got {max_distortion}"

    # Non-isometric transform (non-uniform scale / shear) must show distortion > 0
    non_se3 = se3_matrix.copy()
    non_se3[0, 0] *= 1.35  # 35% stretching
    distortion_stretched = verify_rigid_isometry(verts, non_se3)
    assert distortion_stretched > 0.05, f"Expected distortion on stretched mesh, got {distortion_stretched}"


def test_generate_blender_script_syntax() -> None:
    """Verify generated Blender modular script has all required sections."""
    puppet = get_modular_recipe("puppet_ragdoll")
    script = generate_blender_modular_articulation_script(puppet)
    assert "import bmesh" in script
    assert "Modular_Parts" in script
    assert "Part_Head_Complete" in script
    assert "Part_Axe_Complete" in script
    assert "calc_length()" in script
    assert "isometric_rigid" in script
