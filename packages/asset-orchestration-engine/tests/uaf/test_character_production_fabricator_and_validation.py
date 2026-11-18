"""
Tests for Character Production Fabricator, Validator, and Package.
UAF-81.29 Sections 120, 121, 122, 145, 146.
"""

from uaf.character_production.engine.production_fabricator import CharacterProductionFabricationPlatform
from uaf.character_production.validation.production_validator import CharacterProductionValidator
from uaf.character_production.package.production_package import CharacterProductionPackage


def test_character_production_fabrication_all_three_golden_archetypes():
    builders = [
        CharacterProductionFabricationPlatform.build_golden_humanoid,
        CharacterProductionFabricationPlatform.build_golden_robot,
        CharacterProductionFabricationPlatform.build_golden_creature,
    ]

    for builder in builders:
        c_def, sk_ref, skel_ref, phys_ref, lod_count = builder()
        assert c_def.proportions.is_valid is True
        assert c_def.bone_count >= 15
        assert sk_ref.startswith("SK_")
        assert skel_ref.startswith("SKEL_")
        assert phys_ref.startswith("PHYS_")
        assert lod_count >= 3


def test_character_production_package_validation_and_serialization():
    c_def, sk_ref, skel_ref, phys_ref, lod_count = CharacterProductionFabricationPlatform.build_golden_humanoid("Char_PkgHumanoid")

    report = CharacterProductionValidator.validate_production_character(c_def, sk_ref, skel_ref, phys_ref, lod_count)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterProductionPackage(
        asset_id="Char_PkgHumanoid",
        char_def=c_def,
        skeletal_mesh_ref=sk_ref,
        skeleton_ref=skel_ref,
        physics_asset_ref=phys_ref,
        lod_count=lod_count,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Char_PkgHumanoid"
    assert data["char_def"]["bone_count"] == 68
    assert data["validation_report"]["review_status"] == "PASSED"
