"""
UAF-81.33 Acceptance Tests (Sections 131, 8, 9, 128, 140).
Verifies:
- Section 131: Final Acceptance Criteria (Generates and validates all 9 Golden Reference Characters:
  Golden Human, Golden Soldier, Golden Robot, Golden Android, Golden Alien, Golden Creature, Golden Armored Character, Golden Clothed Character, Golden Boss).
- Sections 8, 9, 128, 140: Non-Negotiable Requirements Test (Zero tolerance for unrealistic heights outside [50, 400]cm,
  bone count < 15, missing Unreal physics asset, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_creature_rig.engine.character_creature_fabricator import CharacterCreatureRigFabricationPlatform
from uaf.character_creature_rig.validation.character_creature_validator import CharacterCreatureRigValidator
from uaf.character_creature_rig.models.definition import (
    CharacterCreatureRigDefinition,
    CharacterType33,
    CharacterGenerationStrategy33,
    CharacterBodyProportions33,
)
from uaf.character_creature_rig.package.character_creature_package import CharacterCreatureRigPackage


def test_final_character_creature_rig_acceptance_section_131():
    """
    Acceptance Test Section 131:
    Synthesizes and validates all 9 Golden Reference Characters.
    """
    builders = [
        ("Char_Gold_Human", CharacterCreatureRigFabricationPlatform.build_golden_human),
        ("Char_Gold_Soldier", CharacterCreatureRigFabricationPlatform.build_golden_soldier),
        ("Char_Gold_Robot", CharacterCreatureRigFabricationPlatform.build_golden_robot),
        ("Char_Gold_Android", CharacterCreatureRigFabricationPlatform.build_golden_android),
        ("Char_Gold_Alien", CharacterCreatureRigFabricationPlatform.build_golden_alien),
        ("Char_Gold_Creature", CharacterCreatureRigFabricationPlatform.build_golden_creature),
        ("Char_Gold_Armored", CharacterCreatureRigFabricationPlatform.build_golden_armored_character),
        ("Char_Gold_Clothed", CharacterCreatureRigFabricationPlatform.build_golden_clothed_character),
        ("Char_Gold_Boss", CharacterCreatureRigFabricationPlatform.build_golden_boss),
    ]

    for asset_id, builder_fn in builders:
        c_def, sk_ref, skel_ref, phys_ref = builder_fn(asset_id)
        assert c_def.proportions.is_valid is True
        assert c_def.bone_count >= 15

        report = CharacterCreatureRigValidator.validate_character_creature_rig(c_def, sk_ref, skel_ref, phys_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterCreatureRigPackage(
            asset_id=asset_id,
            character_def=c_def,
            skeletal_mesh_ref=sk_ref,
            skeleton_ref=skel_ref,
            physics_asset_ref=phys_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_8_9_128_140():
    """
    Acceptance Test Sections 8, 9, 128, 140:
    Non-negotiable requirements:
    1. Section 8 & 9: Height outside [50, 400]cm strictly fails.
    2. Section 128: Skeleton with bone count < 15 strictly fails.
    3. Section 140: Missing physics asset reference strictly fails.
    4. Section 140: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    c_def, sk_ref, skel_ref, phys_ref = CharacterCreatureRigFabricationPlatform.build_golden_human("Char_Fault_Test")

    # 1. Section 8 & 9 violation: Height 450cm (> 400cm limit)
    bad_prop = CharacterBodyProportions33(height_cm=450.0)
    bad_cdef_height = CharacterCreatureRigDefinition(
        "Char_BadHeight",
        CharacterType33.HUMANOID,
        proportions=bad_prop,
    )
    rep_height = CharacterCreatureRigValidator.validate_character_creature_rig(bad_cdef_height, sk_ref, skel_ref, phys_ref)
    assert rep_height.is_valid is False
    assert rep_height.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("outside [50.0, 400.0]cm" in iss for iss in rep_height.issues)

    # 2. Section 128 violation: Bone count 8 (< 15 bones)
    bad_cdef_bones = CharacterCreatureRigDefinition(
        "Char_BadBones",
        CharacterType33.HUMANOID,
        proportions=c_def.proportions,
        bone_count=8,
    )
    rep_bones = CharacterCreatureRigValidator.validate_character_creature_rig(bad_cdef_bones, sk_ref, skel_ref, phys_ref)
    assert rep_bones.is_valid is False
    assert rep_bones.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("below the 15 bone minimum" in iss for iss in rep_bones.issues)

    # 3. Section 140 violation: Missing physics asset reference
    rep_phys = CharacterCreatureRigValidator.validate_character_creature_rig(c_def, sk_ref, skel_ref, "")
    assert rep_phys.is_valid is False
    assert rep_phys.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("valid physics asset reference" in iss for iss in rep_phys.issues)

    # 4. Section 140 violation: Absolute machine path in skeletal mesh reference
    bad_mesh_path = "C:\\UnrealProjects\\Chars\\SK_Mannequin.uasset"
    rep_path = CharacterCreatureRigValidator.validate_character_creature_rig(c_def, bad_mesh_path, skel_ref, phys_ref)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
