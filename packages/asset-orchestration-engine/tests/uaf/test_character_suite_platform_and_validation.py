"""
Tests for Character Fabrication Platform, Validation, and Package.
UAF-81.14 Sections 158, 200, 208, 211.
"""

from uaf.character_suite.platform.fabrication_platform import CharacterFabricationPlatform
from uaf.character_suite.validation.suite_validator import CharacterSuiteValidator
from uaf.character_suite.package.character_suite_package import CharacterSuitePackage


def test_fabrication_platform_seven_golden_characters():
    # 1. Human Hero
    p_hero, d_hero, f_hero, l_hero = CharacterFabricationPlatform.build_human_hero("Hero_01")
    assert d_hero.bone_count >= 100
    assert f_hero.morph_targets_count == 52

    # 2. Human NPC
    p_npc, d_npc, f_npc, l_npc = CharacterFabricationPlatform.build_human_npc("NPC_01")
    assert d_npc.bone_count >= 40

    # 3. Heavy Robot
    p_hrob, d_hrob, f_hrob, l_hrob = CharacterFabricationPlatform.build_heavy_robot("Heavy_01")
    assert p_hrob.body_mass_kg >= 400.0

    # 4. Light Robot
    p_lrob, d_lrob, f_lrob, l_lrob = CharacterFabricationPlatform.build_light_robot("Light_01")
    assert p_lrob.height_cm <= 170.0

    # 5. Creature
    p_cre, d_cre, f_cre, l_cre = CharacterFabricationPlatform.build_creature("Beast_01")
    assert d_cre.has_dual_quaternion is True

    # 6. Alien
    p_aln, d_aln, f_aln, l_aln = CharacterFabricationPlatform.build_alien("Alien_01")
    assert any(l.layer_type == "ARMOR" for l in l_aln)

    # 7. Boss
    p_bos, d_bos, f_bos, l_bos = CharacterFabricationPlatform.build_boss("Boss_01")
    assert p_bos.height_cm >= 300.0
    assert len(l_bos) == 3


def test_character_suite_package_validation_and_serialization():
    prof, deform, face, layers = CharacterFabricationPlatform.build_human_hero("Hero_Pkg_Test")

    report = CharacterSuiteValidator.validate_character(prof, deform, face, layers)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = CharacterSuitePackage(
        asset_id="Hero_Pkg_Test",
        profile=prof,
        deformation=deform,
        face=face,
        layers=layers,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["profile"]["classification"] == "HERO"
    assert data["validation_report"]["review_status"] == "PASSED"
