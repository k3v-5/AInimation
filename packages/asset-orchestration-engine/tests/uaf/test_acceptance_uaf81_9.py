"""
UAF-81.9 Acceptance Tests (Sections 160, 161).
Verifies:
- Section 160: Final Acceptance Test (Fully animatable character synthesis: Skeleton, Skinning,
  IK Rig, Ragdoll Physics, Animation Clips, Animation Blueprint Contract, Animation LOD, and Packaging).
- Section 161: Non-Negotiable Rule Test (A character is never production-ready with mesh + material only;
  missing skeleton or skinning strictly flags MANUAL_REVIEW_REQUIRED).
"""

from uaf.animation.models.classification import CharacterClassification, RigProfile
from uaf.animation.models.clip import AnimationClip
from uaf.animation.models.state_machine import AnimationBlueprintContract
from uaf.animation.models.lod import AnimationLODProfile
from uaf.animation.validation.character_validator import (
    AnimatedCharacterValidator,
    CharacterBuildState,
)
from uaf.animation.package.character_package import AnimatedCharacterPackage
from uaf.rigging.skeleton.skeleton_builder import SkeletonBuilder
from uaf.rigging.skinning.skinning_definition import SkinningDefinition, VertexWeights
from uaf.rigging.rig.rig_definition import RigDefinition
from uaf.rigging.physics.physics_asset import PhysicsAssetDefinition


def test_final_animated_character_acceptance_section_160():
    """
    Acceptance Test Section 160:
    Full pipeline synthesis of production-ready animated character:
    - Biped humanoid skeleton from landmarks
    - Skinning weights with normalized influences
    - Control rig with Hand & Foot IK
    - Physics ragdoll asset
    - Locomotion animation clips (Idle, Walk with events)
    - Animation Blueprint State Machine (Idle <-> Walk <-> Run) with Attack montage
    - Distance-based Animation LOD profile
    - Validates quality_score >= 0.80, advances to RUNTIME_READY, packages into AnimatedCharacterPackage
    """
    asset_id = "Char_Golden_Hero_Commander"

    # 1. Skeleton & Skinning
    skeleton = SkeletonBuilder.build_humanoid_skeleton(f"skel_{asset_id}", height_meters=1.82)
    skinning = SkinningDefinition(
        mesh_id=f"mesh_{asset_id}",
        skeleton_id=skeleton.skeleton_id,
        weights={0: VertexWeights(0, {"pelvis": 0.5, "spine_01": 0.5})},
    )

    # 2. Control Rig & Physics
    rig = RigDefinition.create_standard_humanoid_rig(f"rig_{asset_id}", skeleton.skeleton_id)
    physics = PhysicsAssetDefinition.create_standard_ragdoll(f"phys_{asset_id}", skeleton.skeleton_id)

    # 3. Animation Clips & Events
    clip_idle = AnimationClip.create_idle_clip(f"A_{asset_id}_Idle")
    clip_walk = AnimationClip.create_walk_clip(f"A_{asset_id}_Walk")
    clips = [clip_idle, clip_walk]

    # 4. Animation Blueprint Contract
    abp = AnimationBlueprintContract.create_standard_locomotion_contract(f"ABP_{asset_id}")

    # 5. Animation LOD Profile
    lod_prof = AnimationLODProfile.create_standard_profile(f"AnimLOD_{asset_id}")

    # 6. Quality Validation Gate
    val_report = AnimatedCharacterValidator.validate_character(
        has_mesh=True,
        skeleton=skeleton,
        skinning=skinning,
        physics=physics,
        animation_clips=clips,
        blueprint_contract=abp,
    )

    assert val_report.is_valid is True
    assert val_report.build_state == CharacterBuildState.RUNTIME_READY
    assert val_report.review_status == "PASSED"
    assert val_report.quality_score.aggregate_score >= 0.80

    # 7. Final AnimatedCharacterPackage Packaging
    pkg = AnimatedCharacterPackage(
        asset_id=asset_id,
        classification=CharacterClassification.HUMANOID,
        skeleton=skeleton,
        skinning=skinning,
        rig=rig,
        animation_clips=clips,
        blueprint_contract=abp,
        physics=physics,
        lod_profile=lod_prof,
        quality_report=val_report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Char_Golden_Hero_Commander"
    assert data["classification"] == "HUMANOID"
    assert len(data["animation_clips"]) == 2
    assert data["quality_report"]["build_state"] == "RUNTIME_READY"


def test_non_negotiable_rule_section_161():
    """
    Acceptance Test Section 161:
    Non-negotiable rule:
    A character with mesh + material only (missing skeleton or skinning) is NOT production ready.
    The validator MUST reject it with build_state = REJECTED and review_status = MANUAL_REVIEW_REQUIRED.
    """
    # Character with mesh=True, but NO skeleton and NO skinning
    report = AnimatedCharacterValidator.validate_character(
        has_mesh=True,
        skeleton=None,   # VIOLATION!
        skinning=None,   # VIOLATION!
    )

    assert report.is_valid is False
    assert report.build_state == CharacterBuildState.REJECTED
    assert report.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("NON-NEGOTIABLE VIOLATION: Character lacks a structural Skeleton" in iss for iss in report.issues)
    assert any("NON-NEGOTIABLE VIOLATION: Character lacks Skinning weights" in iss for iss in report.issues)
