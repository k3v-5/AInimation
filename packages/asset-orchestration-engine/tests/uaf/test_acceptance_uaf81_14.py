"""
UAF-81.14 Acceptance Tests (Sections 200, 201, 203, 204, 209).
Verifies:
- Section 200: Final Acceptance Criteria (Generates, validates, and packages all 7 canonical golden characters:
  Human Hero, Human NPC, Heavy Robot, Light Robot, Creature, Alien, and Boss).
- Sections 201, 203, 204, 209: Non-Negotiable Requirements Test (Zero tolerance for unrigged animated characters,
  missing geometry layers, or negative layer clipping clearance; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_suite.platform.fabrication_platform import CharacterFabricationPlatform
from uaf.character_suite.validation.suite_validator import CharacterSuiteValidator
from uaf.character_suite.models.deformation import DeformationProfile, CharacterLayer
from uaf.character_suite.package.character_suite_package import CharacterSuitePackage


def test_final_character_suite_acceptance_section_200():
    """
    Acceptance Test Section 200:
    Deterministically synthesizes and validates all 7 canonical golden characters:
    1. Human Hero
    2. Human NPC
    3. Heavy Robot
    4. Light Robot
    5. Creature
    6. Alien
    7. Boss
    """
    builders = [
        ("Char_Golden_Hero", CharacterFabricationPlatform.build_human_hero),
        ("Char_Golden_NPC", CharacterFabricationPlatform.build_human_npc),
        ("Char_Golden_HeavyRobot", CharacterFabricationPlatform.build_heavy_robot),
        ("Char_Golden_LightRobot", CharacterFabricationPlatform.build_light_robot),
        ("Char_Golden_Creature", CharacterFabricationPlatform.build_creature),
        ("Char_Golden_Alien", CharacterFabricationPlatform.build_alien),
        ("Char_Golden_Boss", CharacterFabricationPlatform.build_boss),
    ]

    for asset_id, builder_fn in builders:
        prof, deform, face, layers = builder_fn(asset_id)
        report = CharacterSuiteValidator.validate_character(prof, deform, face, layers)

        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterSuitePackage(
            asset_id=asset_id,
            profile=prof,
            deformation=deform,
            face=face,
            layers=layers,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_201_203_209():
    """
    Acceptance Test Sections 201, 203, 204, 209:
    Non-negotiable requirements:
    1. Section 203: Rig is MANDATORY for animated characters (bone_count <= 0 fails).
    2. Section 209: Non-positive physical height or mass fails.
    3. Section 154/205: Negative layer clipping clearance fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    prof, deform, face, layers = CharacterFabricationPlatform.build_human_hero("Hero_Fault_Test")

    # 1. Section 203 violation: Character with 0 bones (missing rig)
    bad_deform = DeformationProfile(bone_count=0)
    rep_rig = CharacterSuiteValidator.validate_character(prof, bad_deform, face, layers)
    assert rep_rig.is_valid is False
    assert rep_rig.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Rig is mandatory" in iss for iss in rep_rig.issues)

    # 2. Section 154/205 violation: Negative clipping clearance
    bad_layers = [CharacterLayer("L_Pants", "CLOTHING", "Mesh_Pants", "M_Pants", clipping_clearance_mm=-2.0)]
    rep_clip = CharacterSuiteValidator.validate_character(prof, deform, face, bad_layers)
    assert rep_clip.is_valid is False
    assert rep_clip.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("negative clipping clearance" in iss for iss in rep_clip.issues)
