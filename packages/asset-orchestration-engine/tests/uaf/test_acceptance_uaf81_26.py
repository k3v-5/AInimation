"""
UAF-81.26 Acceptance Tests (Sections 115, 6, 114, 129, 135).
Verifies:
- Section 115: Final Acceptance Criteria (Generates and validates all 5 Golden Reference Characters:
  Golden Human, Golden Soldier, Golden Robot, Golden Creature, Golden Boss).
- Sections 6, 114, 129, 135: Non-Negotiable Requirements Test (Zero tolerance for invalid height,
  mesh penetration clearance, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_organic.engine.organic_fabricator import CharacterOrganicFabricationPlatform
from uaf.character_organic.validation.organic_validator import CharacterOrganicValidator
from uaf.character_organic.models.definition import (
    OrganicCharacterDefinition,
    CharacterArchetype26,
    CharacterProportions,
    LayeredClothingItem,
)
from uaf.character_organic.package.organic_package import CharacterOrganicPackage


def test_final_character_organic_acceptance_section_115():
    """
    Acceptance Test Section 115:
    Synthesizes and validates all 5 Golden Reference Characters.
    """
    builders = [
        ("Char_Gold_Human", CharacterOrganicFabricationPlatform.build_golden_human),
        ("Char_Gold_Soldier", CharacterOrganicFabricationPlatform.build_golden_soldier),
        ("Char_Gold_Robot", CharacterOrganicFabricationPlatform.build_golden_robot),
        ("Char_Gold_Creature", CharacterOrganicFabricationPlatform.build_golden_creature),
        ("Char_Gold_Boss", CharacterOrganicFabricationPlatform.build_golden_boss),
    ]

    for asset_id, builder_fn in builders:
        c_def, sk_ref, skel_ref, lod_count = builder_fn(asset_id)
        assert c_def.proportions.is_valid is True

        report = CharacterOrganicValidator.validate_character(c_def, sk_ref, skel_ref, lod_count)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterOrganicPackage(
            asset_id=asset_id,
            character_def=c_def,
            skeletal_mesh_ref=sk_ref,
            skeleton_ref=skel_ref,
            lod_count=lod_count,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_6_114_129_135():
    """
    Acceptance Test Sections 6, 114, 129, 135:
    Non-negotiable requirements:
    1. Section 6 & 114: Character height out of realistic physical bounds strictly fails.
    2. Section 114 & 135: Clothing layer clearance < 0.5mm strictly fails.
    3. Section 129: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    c_def, sk_ref, skel_ref, lod_count = CharacterOrganicFabricationPlatform.build_golden_human("Char_Fault_Test")

    # 1. Section 6 & 114 violation: Height out of bounds (e.g. 15 cm)
    bad_proportions = CharacterProportions(height_cm=15.0)
    bad_cdef_height = OrganicCharacterDefinition(
        "Char_BadHeight",
        CharacterArchetype26.HUMAN,
        bad_proportions,
    )
    rep_height = CharacterOrganicValidator.validate_character(bad_cdef_height, sk_ref, skel_ref, lod_count)
    assert rep_height.is_valid is False
    assert rep_height.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("out of realistic physical bounds" in iss for iss in rep_height.issues)

    # 2. Section 114 & 135 violation: Clothing clearance too small (<0.5mm causes mesh penetration)
    bad_clothing = [
        LayeredClothingItem("Jacket_Clipping", "TORSO", thickness_mm=2.0, clearance_mm=0.1),  # VIOLATION: 0.1mm!
    ]
    bad_cdef_cloth = OrganicCharacterDefinition(
        "Char_BadCloth",
        CharacterArchetype26.HUMAN,
        c_def.proportions,
        bad_clothing,
    )
    rep_cloth = CharacterOrganicValidator.validate_character(bad_cdef_cloth, sk_ref, skel_ref, lod_count)
    assert rep_cloth.is_valid is False
    assert rep_cloth.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("causes mesh penetration/clipping" in iss for iss in rep_cloth.issues)

    # 3. Section 129 violation: Absolute machine path in skeletal mesh reference
    bad_sk_path = "D:\\UnrealProjects\\Game\\Content\\Characters\\SK_Hero.uasset"
    rep_path = CharacterOrganicValidator.validate_character(c_def, bad_sk_path, skel_ref, lod_count)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
