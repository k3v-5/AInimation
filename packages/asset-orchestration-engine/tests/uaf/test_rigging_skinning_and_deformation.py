"""
Tests for Skinning Weights, Weight Normalization, Deformation Evaluation, Facial Rig, and Physics Assets.
UAF-81.5 Sections 27, 29, 30, 35, 41, 54, 89.
"""

import pytest
from uaf.rigging.skinning.skinning_definition import VertexWeights, SkinningDefinition, WeightMethod
from uaf.rigging.skinning.weight_normalizer import WeightNormalizer
from uaf.rigging.skinning.weight_generator import WeightGenerator
from uaf.rigging.skeleton.skeleton_builder import SkeletonBuilder
from uaf.rigging.deformation.deformation_evaluator import (
    DeformationZone,
    DeformationTestPose,
    DeformationEvaluator,
)
from uaf.rigging.facial.facial_rig import FacialRigDefinition, STANDARD_FACIAL_BLENDSHAPES
from uaf.rigging.physics.physics_asset import PhysicsAssetDefinition
from uaf.geometry.models.mesh_data import MeshData


def test_weight_normalizer_pruning_capping_and_unity():
    # Construct vertex weights with 6 influences, some tiny, not summing to 1.0
    vw = VertexWeights(
        vertex_index=0,
        influences={
            "pelvis": 0.45,
            "spine_01": 0.35,
            "thigh_L": 0.15,
            "thigh_R": 0.10,
            "calf_L": 0.05,
            "hand_R": 0.0001,  # tiny weight to be pruned
        },
    )
    skinning = SkinningDefinition(
        mesh_id="mesh_test",
        skeleton_id="skel_test",
        max_influences_per_vertex=4,
        weights={0: vw},
    )

    # Normalize
    WeightNormalizer.normalize_skinning(skinning, threshold=0.001)

    norm_vw = skinning.weights[0]
    # Verify hand_R was pruned
    assert "hand_R" not in norm_vw.influences
    # Verify max influences <= 4
    assert len(norm_vw.influences) <= 4
    # Verify sum == 1.0
    assert pytest.approx(sum(norm_vw.influences.values()), 1e-4) == 1.0

    # Validation must pass
    is_valid, issues = WeightNormalizer.validate_skinning(skinning)
    assert is_valid is True
    assert len(issues) == 0


def test_weight_generator_with_mesh_and_skeleton():
    cube = MeshData.create_cube(size=1.8)
    skeleton = SkeletonBuilder.build_humanoid_skeleton("skel_test_01", height_meters=1.80)

    skinning = WeightGenerator.generate_weights(
        mesh_id="cube_body",
        mesh=cube,
        skeleton=skeleton,
        max_influences=4,
    )

    assert skinning.vertex_count == 8
    is_valid, issues = WeightNormalizer.validate_skinning(skinning)
    assert is_valid is True
    assert len(issues) == 0


def test_deformation_evaluator_stress_poses():
    cube = MeshData.create_cube(size=1.8)
    skeleton = SkeletonBuilder.build_humanoid_skeleton("skel_test_01", height_meters=1.80)
    skinning = WeightGenerator.generate_weights("cube_body", cube, skeleton)

    score = DeformationEvaluator.evaluate_deformation(skeleton, skinning)
    assert score.volume_preservation >= 0.8
    assert score.aggregate_score >= 0.75
    assert len(score.passed_poses) > 0


def test_facial_rig_definition_and_blendshapes():
    facial = FacialRigDefinition(facial_id="face_hero_01")
    assert facial.jaw_bone_id == "jaw"
    assert "eye_L" in facial.eye_bones
    assert len(facial.blendshapes) == len(STANDARD_FACIAL_BLENDSHAPES)
    assert "mouth_smile_L" in facial.blendshapes
    assert "viseme_aa" in facial.blendshapes


def test_physics_asset_ragdoll_generation():
    physics = PhysicsAssetDefinition.create_standard_ragdoll("phys_hero_01", "skel_hero_01")
    assert physics.physics_id == "phys_hero_01"
    assert len(physics.bodies) == 12
    assert len(physics.constraints) == 11
    assert physics.total_mass_kg > 50.0  # Realistic human mass
    assert len(physics.physics_hash) == 64
