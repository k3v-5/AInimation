"""
Tests for AnimatedCharacterValidator and AnimatedCharacterPackage.
UAF-81.9 Sections 143, 145, 148, 160.
"""

from uaf.animation.validation.character_validator import (
    AnimatedCharacterValidator,
    CharacterBuildState,
    AnimatedCharacterQualityScore,
)
from uaf.animation.models.classification import CharacterClassification
from uaf.animation.models.clip import AnimationClip
from uaf.animation.models.state_machine import AnimationBlueprintContract
from uaf.animation.models.lod import AnimationLODProfile
from uaf.animation.package.character_package import AnimatedCharacterPackage
from uaf.rigging.skeleton.skeleton_builder import SkeletonBuilder
from uaf.rigging.skinning.skinning_definition import SkinningDefinition, VertexWeights
from uaf.rigging.physics.physics_asset import PhysicsAssetDefinition


def test_animated_character_validator_passing():
    skeleton = SkeletonBuilder.build_humanoid_skeleton("skel_hero", height_meters=1.80)
    skinning = SkinningDefinition(
        mesh_id="mesh_body",
        skeleton_id=skeleton.skeleton_id,
        weights={0: VertexWeights(0, {"pelvis": 1.0})},
    )
    physics = PhysicsAssetDefinition.create_standard_ragdoll("phys_hero", skeleton.skeleton_id)
    clips = [AnimationClip.create_idle_clip(), AnimationClip.create_walk_clip()]
    abp = AnimationBlueprintContract.create_standard_locomotion_contract()

    report = AnimatedCharacterValidator.validate_character(
        has_mesh=True,
        skeleton=skeleton,
        skinning=skinning,
        physics=physics,
        animation_clips=clips,
        blueprint_contract=abp,
    )

    assert report.is_valid is True
    assert report.build_state == CharacterBuildState.RUNTIME_READY
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.80


def test_animated_character_package_serialization():
    skeleton = SkeletonBuilder.build_humanoid_skeleton("skel_hero", height_meters=1.80)
    skinning = SkinningDefinition(
        mesh_id="mesh_body",
        skeleton_id=skeleton.skeleton_id,
        weights={0: VertexWeights(0, {"pelvis": 1.0})},
    )
    clips = [AnimationClip.create_idle_clip()]
    abp = AnimationBlueprintContract.create_standard_locomotion_contract()

    pkg = AnimatedCharacterPackage(
        asset_id="Char_Hero_SpecOps",
        classification=CharacterClassification.HUMANOID,
        skeleton=skeleton,
        skinning=skinning,
        animation_clips=clips,
        blueprint_contract=abp,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Char_Hero_SpecOps"
    assert data["classification"] == "HUMANOID"
    assert len(data["animation_clips"]) == 1
