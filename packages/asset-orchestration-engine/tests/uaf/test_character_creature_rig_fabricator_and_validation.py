"""
Tests for Character Creature Rig Fabricator, Validator, and Package.
UAF-81.33 Sections 124, 125, 131, 140, 141.
"""

from uaf.character_creature_rig.engine.character_creature_fabricator import CharacterCreatureRigFabricationPlatform
from uaf.character_creature_rig.validation.character_creature_validator import CharacterCreatureRigValidator
from uaf.character_creature_rig.package.character_creature_package import CharacterCreatureRigPackage


def test_character_creature_rig_fabrication_all_nine_golden_characters():
    builders = [
        CharacterCreatureRigFabricationPlatform.build_golden_human,
        CharacterCreatureRigFabricationPlatform.build_golden_soldier,
        CharacterCreatureRigFabricationPlatform.build_golden_robot,
        CharacterCreatureRigFabricationPlatform.build_golden_android,
        CharacterCreatureRigFabricationPlatform.build_golden_alien,
        CharacterCreatureRigFabricationPlatform.build_golden_creature,
        CharacterCreatureRigFabricationPlatform.build_golden_armored_character,
        CharacterCreatureRigFabricationPlatform.build_golden_clothed_character,
        CharacterCreatureRigFabricationPlatform.build_golden_boss,
    ]

    for builder in builders:
        c_def, sk_ref, skel_ref, phys_ref = builder()
        assert c_def.proportions.is_valid is True
        assert c_def.bone_count >= 15
        assert sk_ref.startswith("SK_")
        assert skel_ref.startswith("SKEL_")
        assert phys_ref.startswith("PHYS_")


def test_character_creature_rig_package_validation_and_serialization():
    c_def, sk_ref, skel_ref, phys_ref = CharacterCreatureRigFabricationPlatform.build_golden_soldier("Char_PkgSoldier")

    report = CharacterCreatureRigValidator.validate_character_creature_rig(c_def, sk_ref, skel_ref, phys_ref)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterCreatureRigPackage(
        asset_id="Char_PkgSoldier",
        character_def=c_def,
        skeletal_mesh_ref=sk_ref,
        skeleton_ref=skel_ref,
        physics_asset_ref=phys_ref,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Char_PkgSoldier"
    assert data["character_def"]["character_type"] == "PLAYER"
    assert data["validation_report"]["review_status"] == "PASSED"
