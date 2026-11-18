"""
UAF-81.17 Acceptance Tests (Sections 217, 14, 15, 39, 215).
Verifies:
- Section 217: Final Acceptance Criteria (Generates and validates:
  1 Skeleton, 1 Rig, 1 Skin, 1 Physics Asset, 1 IK Configuration, 5 Canonical Animations [IDLE, WALK, RUN, ATTACK, DEATH], and Export Package).
- Sections 14, 15, 39, 215: Non-Negotiable Requirements Test (Zero tolerance for cyclic skeleton hierarchies,
  unweighted vertices, or missing canonical clips; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_animation.engine.animation_fabricator import CharacterAnimationFabricator
from uaf.character_animation.validation.animation_validator import CharacterAnimationValidator
from uaf.character_animation.models.skeleton import SkeletonHierarchy, BoneNode, BoneRole
from uaf.character_animation.models.skinning import SkinningWeightData
from uaf.character_animation.package.animation_package import CharacterAnimationPackage


def test_final_character_animation_acceptance_section_217():
    """
    Acceptance Test Section 217:
    Automatically fabricates and validates full character animation suite:
    1 Skeleton, 1 Rig, 1 Skin, 1 Physics Asset, 1 IK Configuration, and 5 canonical clips (IDLE, WALK, RUN, ATTACK, DEATH).
    """
    skel, ik_chains, skinning, clips, phys_bodies = CharacterAnimationFabricator.build_character_animation_suite("Char_Golden_Production")

    # Section 217 verification:
    assert skel is not None
    assert len(skel.bones) >= 15
    assert len(ik_chains) >= 4
    assert skinning is not None and skinning.weights_sum_normalized is True
    assert len(phys_bodies) >= 8

    required_clips = {"IDLE", "WALK", "RUN", "ATTACK", "DEATH"}
    assert required_clips.issubset(set(clips.keys()))

    report = CharacterAnimationValidator.validate_animation_suite(skel, ik_chains, skinning, clips, phys_bodies)
    assert report.is_valid is True, f"Failed: {report.issues}"
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterAnimationPackage(
        asset_id="Char_Golden_Production",
        skeleton=skel,
        ik_chains=ik_chains,
        skinning=skinning,
        clips=clips,
        physics_bodies=phys_bodies,
        validation_report=report,
    )
    assert len(pkg.package_hash) == 64
    assert pkg.to_dict()["asset_id"] == "Char_Golden_Production"


def test_non_negotiable_requirements_section_14_39_215():
    """
    Acceptance Test Sections 14, 39, 215:
    Non-negotiable requirements:
    1. Section 14: Skeleton with cycle strictly fails.
    2. Section 215: Mesh with unweighted vertices strictly fails.
    3. Section 217: Missing canonical animation clip (e.g. DEATH) strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    skel, ik_chains, skinning, clips, phys_bodies = CharacterAnimationFabricator.build_character_animation_suite("Char_Fault_Test")

    # 1. Section 14 violation: Cyclic skeleton
    bad_skel = SkeletonHierarchy.create_standard_humanoid_skeleton("SK_Cyclic")
    bad_skel.bones["root"].parent = "pelvis"  # Introduces cycle
    rep_cycle = CharacterAnimationValidator.validate_animation_suite(bad_skel, ik_chains, skinning, clips, phys_bodies)
    assert rep_cycle.is_valid is False
    assert rep_cycle.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("cyclic parenting" in iss for iss in rep_cycle.issues)

    # 2. Section 215 violation: Unweighted vertices
    bad_skin = SkinningWeightData(vertex_count=5000, unweighted_vertices_count=12)
    rep_unweighted = CharacterAnimationValidator.validate_animation_suite(skel, ik_chains, bad_skin, clips, phys_bodies)
    assert rep_unweighted.is_valid is False
    assert rep_unweighted.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("unweighted vertices" in iss for iss in rep_unweighted.issues)

    # 3. Section 217 violation: Missing DEATH clip
    partial_clips = {k: v for k, v in clips.items() if k != "DEATH"}
    rep_missing = CharacterAnimationValidator.validate_animation_suite(skel, ik_chains, skinning, partial_clips, phys_bodies)
    assert rep_missing.is_valid is False
    assert rep_missing.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Missing required canonical animation clips" in iss for iss in rep_missing.issues)
