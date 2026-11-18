"""
UAF-81.23 Acceptance Tests (Sections 123, 5, 99, 117, 122).
Verifies:
- Section 123: Final Acceptance Criteria (Generates and validates all 7 character archetypes:
  biped humanoid, armored character, clothed character, non-human creature, weapon-armed character,
  facial character, secondary motion character).
- Sections 5, 99, 117, 122: Non-Negotiable Requirements Test (Zero tolerance for skeleton cycles,
  missing/multiple roots, non-positive clip durations, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.animation_motion.engine.motion_fabricator import AnimationMotionFabricationPlatform
from uaf.animation_motion.validation.motion_validator import AnimationMotionValidator
from uaf.animation_motion.models.skeleton import CharacterRigDefinition, StandardSkeletonHierarchy, RigBoneNode, BoneRoleType
from uaf.animation_motion.models.motion import MotionClip, MotionClipType
from uaf.animation_motion.package.motion_package import AnimationMotionPackage


def test_final_animation_motion_acceptance_section_123():
    """
    Acceptance Test Section 123:
    Synthesizes and validates all 7 required character archetypes.
    """
    builders = [
        ("Rig_Gold_Biped", AnimationMotionFabricationPlatform.build_biped_humanoid),
        ("Rig_Gold_Armored", AnimationMotionFabricationPlatform.build_armored_character),
        ("Rig_Gold_Clothed", AnimationMotionFabricationPlatform.build_clothed_character),
        ("Rig_Gold_Creature", AnimationMotionFabricationPlatform.build_non_human_creature),
        ("Rig_Gold_Armed", AnimationMotionFabricationPlatform.build_weapon_armed_character),
        ("Rig_Gold_Facial", AnimationMotionFabricationPlatform.build_facial_character),
        ("Rig_Gold_Secondary", AnimationMotionFabricationPlatform.build_secondary_motion_character),
    ]

    for asset_id, builder_fn in builders:
        rig_def, clips, phys_ref, cr_ref = builder_fn(asset_id)
        assert len(clips) >= 3

        report = AnimationMotionValidator.validate_rig_and_motion(rig_def, clips, phys_ref, cr_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = AnimationMotionPackage(
            asset_id=asset_id,
            rig_def=rig_def,
            clips=clips,
            physics_asset_ref=phys_ref,
            control_rig_ref=cr_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_5_99_117_122():
    """
    Acceptance Test Sections 5, 99, 117, 122:
    Non-negotiable requirements:
    1. Section 5 & 122: Hierarchy with cycles strictly fails.
    2. Section 99: Clip with duration <= 0.0s strictly fails.
    3. Section 117: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    rig_def, clips, phys_ref, cr_ref = AnimationMotionFabricationPlatform.build_biped_humanoid("Rig_Fault_Test")

    # 1. Section 5 & 122 violation: Skeleton cycle
    cyclic_skel = StandardSkeletonHierarchy()
    cyclic_skel.add_bone(RigBoneNode("Bone_X", BoneRoleType.ROOT, "Bone_Z"))
    cyclic_skel.add_bone(RigBoneNode("Bone_Y", BoneRoleType.SPINE, "Bone_X"))
    cyclic_skel.add_bone(RigBoneNode("Bone_Z", BoneRoleType.SPINE, "Bone_Y"))
    bad_rig = CharacterRigDefinition("Rig_Cyclic", "HUMANOID", cyclic_skel)

    rep_cycle = AnimationMotionValidator.validate_rig_and_motion(bad_rig, clips, phys_ref, cr_ref)
    assert rep_cycle.is_valid is False
    assert rep_cycle.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Cycle detected" in iss or "unique root bone" in iss for iss in rep_cycle.issues)

    # 2. Section 99 violation: Zero or negative clip duration
    bad_clips = [
        MotionClip("Anim_Freeze", MotionClipType.LOOP, duration_seconds=0.0, is_looping=True),
    ]
    rep_duration = AnimationMotionValidator.validate_rig_and_motion(rig_def, bad_clips, phys_ref, cr_ref)
    assert rep_duration.is_valid is False
    assert rep_duration.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("non-positive duration" in iss for iss in rep_duration.issues)

    # 3. Section 117 violation: Absolute machine path in physics asset
    bad_phys_path = "C:\\UnrealProjects\\Game\\Content\\Physics\\PHYS_Rig.uasset"
    rep_path = AnimationMotionValidator.validate_rig_and_motion(rig_def, clips, bad_phys_path, cr_ref)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent reference path" in iss for iss in rep_path.issues)
