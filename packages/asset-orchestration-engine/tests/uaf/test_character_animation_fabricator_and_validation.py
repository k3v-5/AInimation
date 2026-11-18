"""
Tests for Character Animation Fabricator, Validator, and Package.
UAF-81.17 Sections 175, 213, 217.
"""

from uaf.character_animation.engine.animation_fabricator import CharacterAnimationFabricator
from uaf.character_animation.validation.animation_validator import CharacterAnimationValidator
from uaf.character_animation.package.animation_package import CharacterAnimationPackage


def test_character_animation_fabrication_and_validation():
    skel, ik_chains, skinning, clips, phys_bodies = CharacterAnimationFabricator.build_character_animation_suite("Char_Hero")

    assert len(skel.bones) > 10
    assert len(ik_chains) == 5
    assert skinning.weights_sum_normalized is True
    assert set(clips.keys()) == {"IDLE", "WALK", "RUN", "ATTACK", "DEATH"}
    assert len(phys_bodies) > 0

    report = CharacterAnimationValidator.validate_animation_suite(skel, ik_chains, skinning, clips, phys_bodies)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterAnimationPackage(
        asset_id="Char_Hero",
        skeleton=skel,
        ik_chains=ik_chains,
        skinning=skinning,
        clips=clips,
        physics_bodies=phys_bodies,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Char_Hero"
    assert "IDLE" in data["clips"]
    assert data["validation_report"]["review_status"] == "PASSED"
