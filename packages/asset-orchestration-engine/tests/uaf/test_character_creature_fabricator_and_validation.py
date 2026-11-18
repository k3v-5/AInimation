"""
Tests for Character Creature Fabricator, Validator, and Package.
UAF-81.21 Sections 146, 147, 155, 171.
"""

from uaf.character_creature.engine.creature_fabricator import CharacterCreatureFabricationPlatform
from uaf.character_creature.validation.creature_validator import CharacterCreatureValidator
from uaf.character_creature.package.creature_package import CharacterCreaturePackage


def test_character_creature_fabrication_canonical_archetypes():
    archetypes = [
        CharacterCreatureFabricationPlatform.build_human_character,
        CharacterCreatureFabricationPlatform.build_robot_character,
        CharacterCreatureFabricationPlatform.build_alien_character,
        CharacterCreatureFabricationPlatform.build_creature_character,
        CharacterCreatureFabricationPlatform.build_heavy_armor_character,
        CharacterCreatureFabricationPlatform.build_light_armor_character,
        CharacterCreatureFabricationPlatform.build_cloth_heavy_character,
        CharacterCreatureFabricationPlatform.build_cloth_light_character,
        CharacterCreatureFabricationPlatform.build_complex_multilayer_character,
    ]

    for builder in archetypes:
        char_def, parts, layers, skel_ref = builder()
        assert len(parts) >= 5
        assert len(layers) >= 1
        assert skel_ref.startswith("SKEL_")


def test_character_creature_package_validation_and_serialization():
    char_def, parts, layers, skel_ref = CharacterCreatureFabricationPlatform.build_complex_multilayer_character("Char_PkgSoldier")

    report = CharacterCreatureValidator.validate_character(char_def, parts, layers, skel_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterCreaturePackage(
        asset_id="Char_PkgSoldier",
        character_def=char_def,
        body_parts=parts,
        equipment_layers=layers,
        skeleton_ref=skel_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Char_PkgSoldier"
    assert len(data["body_parts"]) >= 5
    assert len(data["equipment_layers"]) >= 6
    assert data["validation_report"]["review_status"] == "PASSED"
