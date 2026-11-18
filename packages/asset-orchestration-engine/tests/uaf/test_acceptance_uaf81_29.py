"""
UAF-81.29 Acceptance Tests (Sections 120, 121, 122, 2, 6, 134, 135).
Verifies:
- Sections 120, 121, 122: Final Acceptance Criteria (Generates and validates all 3 Golden Reference Characters:
  Golden Humanoid, Golden Robot, Golden Creature).
- Sections 2, 6, 134, 135: Non-Negotiable Requirements Test (Zero tolerance for invalid stature,
  insufficient bones, missing physics asset, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_production.engine.production_fabricator import CharacterProductionFabricationPlatform
from uaf.character_production.validation.production_validator import CharacterProductionValidator
from uaf.character_production.models.definition import (
    ProductionCharacterDefinition,
    CharacterType29,
    ProductionBodyProportions,
    CharacterReadinessClass,
)
from uaf.character_production.package.production_package import CharacterProductionPackage


def test_final_character_production_acceptance_sections_120_to_122():
    """
    Acceptance Test Sections 120, 121, 122:
    Synthesizes and validates all 3 Golden Reference Characters.
    """
    builders = [
        ("Char_Gold_Humanoid", CharacterProductionFabricationPlatform.build_golden_humanoid),
        ("Char_Gold_Robot", CharacterProductionFabricationPlatform.build_golden_robot),
        ("Char_Gold_Creature", CharacterProductionFabricationPlatform.build_golden_creature),
    ]

    for asset_id, builder_fn in builders:
        c_def, sk_ref, skel_ref, phys_ref, lod_count = builder_fn(asset_id)
        assert c_def.proportions.is_valid is True
        assert c_def.bone_count >= 15

        report = CharacterProductionValidator.validate_production_character(c_def, sk_ref, skel_ref, phys_ref, lod_count)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterProductionPackage(
            asset_id=asset_id,
            char_def=c_def,
            skeletal_mesh_ref=sk_ref,
            skeleton_ref=skel_ref,
            physics_asset_ref=phys_ref,
            lod_count=lod_count,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_2_6_134_135():
    """
    Acceptance Test Sections 2, 6, 134, 135:
    Non-negotiable requirements:
    1. Section 6 & 135: Character height out of realistic physical bounds strictly fails.
    2. Section 135: Bone count < 15 strictly fails.
    3. Section 2 & 135: Missing PhysicsAsset for Unreal readiness strictly fails.
    4. Section 135: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    c_def, sk_ref, skel_ref, phys_ref, lod_count = CharacterProductionFabricationPlatform.build_golden_humanoid("Char_Fault_Test")

    # 1. Section 6 & 135 violation: Height out of bounds (e.g. 10 cm)
    bad_props = ProductionBodyProportions(height_cm=10.0)
    bad_cdef_height = ProductionCharacterDefinition(
        "Char_BadHeight",
        CharacterType29.HUMAN,
        bad_props,
    )
    rep_height = CharacterProductionValidator.validate_production_character(bad_cdef_height, sk_ref, skel_ref, phys_ref, lod_count)
    assert rep_height.is_valid is False
    assert rep_height.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("outside realistic physical bounds" in iss for iss in rep_height.issues)

    # 2. Section 135 violation: Bone count < 15 (e.g. 4 bones)
    bad_cdef_bones = ProductionCharacterDefinition(
        "Char_BadBones",
        CharacterType29.HUMAN,
        c_def.proportions,
        bone_count=4,
    )
    rep_bones = CharacterProductionValidator.validate_production_character(bad_cdef_bones, sk_ref, skel_ref, phys_ref, lod_count)
    assert rep_bones.is_valid is False
    assert rep_bones.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("minimum required 15" in iss for iss in rep_bones.issues)

    # 3. Section 2 & 135 violation: Missing PhysicsAsset reference
    rep_phys = CharacterProductionValidator.validate_production_character(c_def, sk_ref, skel_ref, "", lod_count)
    assert rep_phys.is_valid is False
    assert rep_phys.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("lacks PhysicsAsset reference" in iss for iss in rep_phys.issues)

    # 4. Section 135 violation: Absolute machine path in skeleton reference
    bad_skel_path = "E:\\UnrealProjects\\Game\\Content\\Skeletons\\SKEL_Body.uasset"
    rep_path = CharacterProductionValidator.validate_production_character(c_def, sk_ref, bad_skel_path, phys_ref, lod_count)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
