"""
Tests for Character Prod V2 Fabricator, Validator, and Package.
UAF-81.45 Sections 120, 138, 152.
"""

from uaf.character_prod_v2.engine.character_prod_v2_fabricator import CharacterProdV2FabricationPlatform
from uaf.character_prod_v2.validation.character_prod_v2_validator import CharacterProdV2Validator
from uaf.character_prod_v2.package.character_prod_v2_package import CharacterProdV2Package


def test_character_prod_v2_fabrication_all_five_golden_characters():
    builders = [
        CharacterProdV2FabricationPlatform.build_golden_human,
        CharacterProdV2FabricationPlatform.build_golden_robot,
        CharacterProdV2FabricationPlatform.build_golden_creature,
        CharacterProdV2FabricationPlatform.build_golden_armored_character,
        CharacterProdV2FabricationPlatform.build_golden_clothed_character,
    ]

    for builder in builders:
        spec, sk_path, fabp_path, phys_path = builder()
        assert spec.is_valid_production is True
        assert sk_path.startswith("/Game/Characters/V2/Meshes/")
        assert fabp_path.startswith("/Game/Characters/V2/Animations/")
        assert phys_path.startswith("/Game/Characters/V2/Physics/")


def test_character_prod_v2_package_validation_and_serialization():
    spec, sk_path, fabp_path, phys_path = CharacterProdV2FabricationPlatform.build_golden_human("Char_PkgHumanV2")

    report = CharacterProdV2Validator.validate_character_prod_v2(spec, sk_path, fabp_path, phys_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterProdV2Package(
        character_id="Char_PkgHumanV2",
        spec=spec,
        skeletal_mesh_path=sk_path,
        facial_anim_blueprint_path=fabp_path,
        physics_asset_path=phys_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["character_id"] == "Char_PkgHumanV2"
    assert data["spec"]["archetype"] == "HUMAN"
    assert data["validation_report"]["review_status"] == "PASSED"
