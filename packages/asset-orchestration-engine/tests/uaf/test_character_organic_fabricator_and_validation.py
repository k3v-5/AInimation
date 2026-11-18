"""
Tests for Organic Character Fabricator, Validator, and Package.
UAF-81.26 Sections 115, 123, 140, 141.
"""

from uaf.character_organic.engine.organic_fabricator import CharacterOrganicFabricationPlatform
from uaf.character_organic.validation.organic_validator import CharacterOrganicValidator
from uaf.character_organic.package.organic_package import CharacterOrganicPackage


def test_character_organic_fabrication_all_five_golden_archetypes():
    builders = [
        CharacterOrganicFabricationPlatform.build_golden_human,
        CharacterOrganicFabricationPlatform.build_golden_soldier,
        CharacterOrganicFabricationPlatform.build_golden_robot,
        CharacterOrganicFabricationPlatform.build_golden_creature,
        CharacterOrganicFabricationPlatform.build_golden_boss,
    ]

    for builder in builders:
        c_def, sk_ref, skel_ref, lod_count = builder()
        assert c_def.proportions.is_valid is True
        assert sk_ref.startswith("SK_")
        assert skel_ref.startswith("SKEL_")
        assert lod_count >= 3


def test_character_organic_package_validation_and_serialization():
    c_def, sk_ref, skel_ref, lod_count = CharacterOrganicFabricationPlatform.build_golden_soldier("Char_PkgSoldier")

    report = CharacterOrganicValidator.validate_character(c_def, sk_ref, skel_ref, lod_count)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterOrganicPackage(
        asset_id="Char_PkgSoldier",
        character_def=c_def,
        skeletal_mesh_ref=sk_ref,
        skeleton_ref=skel_ref,
        lod_count=lod_count,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Char_PkgSoldier"
    assert len(data["character_def"]["clothing_layers"]) >= 3
    assert data["validation_report"]["review_status"] == "PASSED"
