"""
Tests for Character Creature System Fabricator, Validator, and Package.
UAF-81.49 Sections 140, 141, 157.
"""

from uaf.character_creature_system.engine.character_creature_fabricator import CharacterCreatureFabricationPlatform
from uaf.character_creature_system.validation.character_creature_validator import CharacterCreatureValidator
from uaf.character_creature_system.package.character_creature_package import CharacterCreaturePackage


def test_character_creature_system_fabrication_all_five_golden_characters():
    builders = [
        CharacterCreatureFabricationPlatform.build_golden_human,
        CharacterCreatureFabricationPlatform.build_golden_robot,
        CharacterCreatureFabricationPlatform.build_golden_creature,
        CharacterCreatureFabricationPlatform.build_golden_boss,
        CharacterCreatureFabricationPlatform.build_golden_armored_character,
    ]

    for builder in builders:
        spec, sk_path, abp_path, phys_path = builder()
        assert spec.is_valid_production is True
        assert sk_path.startswith("/Game/Characters/Production/Meshes/")
        assert abp_path.startswith("/Game/Characters/Production/Animations/")
        assert phys_path.startswith("/Game/Characters/Production/Physics/")


def test_character_creature_package_validation_and_serialization():
    spec, sk_path, abp_path, phys_path = CharacterCreatureFabricationPlatform.build_golden_human("Char_PkgHuman49")

    report = CharacterCreatureValidator.validate_character_creature(spec, sk_path, abp_path, phys_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterCreaturePackage(
        character_id="Char_PkgHuman49",
        spec=spec,
        skeletal_mesh_path=sk_path,
        anim_blueprint_path=abp_path,
        physics_asset_path=phys_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["character_id"] == "Char_PkgHuman49"
    assert data["spec"]["character_type"] == "PLAYER"
    assert data["validation_report"]["review_status"] == "PASSED"
