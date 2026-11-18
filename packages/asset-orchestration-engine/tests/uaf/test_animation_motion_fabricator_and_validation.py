"""
Tests for Animation Motion Fabricator, Validator, and Package.
UAF-81.23 Sections 111, 116, 122, 123.
"""

from uaf.animation_motion.engine.motion_fabricator import AnimationMotionFabricationPlatform
from uaf.animation_motion.validation.motion_validator import AnimationMotionValidator
from uaf.animation_motion.package.motion_package import AnimationMotionPackage


def test_animation_motion_fabrication_all_seven_required_archetypes():
    archetypes = [
        AnimationMotionFabricationPlatform.build_biped_humanoid,
        AnimationMotionFabricationPlatform.build_armored_character,
        AnimationMotionFabricationPlatform.build_clothed_character,
        AnimationMotionFabricationPlatform.build_non_human_creature,
        AnimationMotionFabricationPlatform.build_weapon_armed_character,
        AnimationMotionFabricationPlatform.build_facial_character,
        AnimationMotionFabricationPlatform.build_secondary_motion_character,
    ]

    for builder in archetypes:
        rig_def, clips, phys_ref, cr_ref = builder()
        assert len(rig_def.skeleton.bones) >= 10
        assert rig_def.skeleton.find_root() is not None
        assert rig_def.skeleton.has_cycles() is False
        assert len(clips) >= 3
        assert phys_ref.startswith("PHYS_")
        assert cr_ref.startswith("CR_")


def test_animation_motion_package_validation_and_serialization():
    rig_def, clips, phys_ref, cr_ref = AnimationMotionFabricationPlatform.build_biped_humanoid("Rig_PkgHumanoid")

    report = AnimationMotionValidator.validate_rig_and_motion(rig_def, clips, phys_ref, cr_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = AnimationMotionPackage(
        asset_id="Rig_PkgHumanoid",
        rig_def=rig_def,
        clips=clips,
        physics_asset_ref=phys_ref,
        control_rig_ref=cr_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Rig_PkgHumanoid"
    assert len(data["clips"]) >= 4
    assert data["validation_report"]["review_status"] == "PASSED"
