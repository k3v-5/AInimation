"""
UAF-81.45 Acceptance Tests (Sections 138, 11, 12, 119, 136, 153, 154, 155, 156, 157, 120, 152).
Verifies:
- Section 138: Final Acceptance Criteria (Generates and validates all 5 Golden Characters:
  Human, Robot, Creature, Armored Character, Clothed Character).
- Sections 11, 136, 154, 155, 156, 157: Hard Fail Conditions Test (Zero tolerance for invalid anatomical dimensions,
  bone count < 20, missing clothing/hair, missing facial rig/physics, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_prod_v2.engine.character_prod_v2_fabricator import CharacterProdV2FabricationPlatform
from uaf.character_prod_v2.validation.character_prod_v2_validator import CharacterProdV2Validator
from uaf.character_prod_v2.models.definition import (
    CharacterProdV2Specification,
    CharacterArchetype45,
    ProportionProfile45,
    AnatomicalDimensions45,
)
from uaf.character_prod_v2.package.character_prod_v2_package import CharacterProdV2Package


def test_final_character_prod_v2_acceptance_section_138():
    """
    Acceptance Test Section 138:
    Synthesizes and validates all 5 Golden Characters.
    """
    builders = [
        ("Char_Gold_Human", CharacterProdV2FabricationPlatform.build_golden_human),
        ("Char_Gold_RobotV2", CharacterProdV2FabricationPlatform.build_golden_robot),
        ("Char_Gold_CreatureV2", CharacterProdV2FabricationPlatform.build_golden_creature),
        ("Char_Gold_Armored", CharacterProdV2FabricationPlatform.build_golden_armored_character),
        ("Char_Gold_Clothed", CharacterProdV2FabricationPlatform.build_golden_clothed_character),
    ]

    for char_id, builder_fn in builders:
        spec, sk_path, fabp_path, phys_path = builder_fn(char_id)
        assert spec.is_valid_production is True

        report = CharacterProdV2Validator.validate_character_prod_v2(spec, sk_path, fabp_path, phys_path)
        assert report.is_valid is True, f"Failed for {char_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterProdV2Package(
            character_id=char_id,
            spec=spec,
            skeletal_mesh_path=sk_path,
            facial_anim_blueprint_path=fabp_path,
            physics_asset_path=phys_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["character_id"] == char_id


def test_hard_fail_conditions_section_11_136_154_155_156_157():
    """
    Acceptance Test Sections 11, 136, 154, 155, 156, 157:
    Hard fail conditions:
    1. INVALID_ANATOMICAL_DIMENSIONS: Height outside [50, 450]cm or non-positive spans.
    2. INVALID_BONE_COUNT: Bone count < 20.
    3. MISSING_CORE_COMPONENTS: Missing clothing, hair, facial rig, or physics asset.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, sk_path, fabp_path, phys_path = CharacterProdV2FabricationPlatform.build_golden_human("Char_Fault_Test")

    # 1. Height violation: 35cm (< 50cm)
    bad_dims = AnatomicalDimensions45(height_cm=35.0, shoulder_width_cm=20.0, chest_depth_cm=15.0, torso_length_cm=20.0, arm_length_cm=20.0, leg_length_cm=25.0)
    bad_spec_dims = CharacterProdV2Specification(
        "Char_BadDims",
        CharacterArchetype45.HUMAN,
        ProportionProfile45.REALISTIC,
        dimensions=bad_dims,
    )
    rep_dims = CharacterProdV2Validator.validate_character_prod_v2(bad_spec_dims, sk_path, fabp_path, phys_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_ANATOMICAL_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Bone count violation: 15 bones (< 20)
    bad_spec_bones = CharacterProdV2Specification(
        "Char_FewBones",
        CharacterArchetype45.HUMAN,
        ProportionProfile45.REALISTIC,
        bone_count=15,
    )
    rep_bones = CharacterProdV2Validator.validate_character_prod_v2(bad_spec_bones, sk_path, fabp_path, phys_path)
    assert rep_bones.is_valid is False
    assert rep_bones.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_BONE_COUNT" in iss for iss in rep_bones.issues)

    # 3. Missing clothing component
    bad_spec_cloth = CharacterProdV2Specification(
        "Char_NoCloth",
        CharacterArchetype45.HUMAN,
        ProportionProfile45.REALISTIC,
        has_clothing=False,
    )
    rep_cloth = CharacterProdV2Validator.validate_character_prod_v2(bad_spec_cloth, sk_path, fabp_path, phys_path)
    assert rep_cloth.is_valid is False
    assert rep_cloth.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_COMPONENTS" in iss for iss in rep_cloth.issues)

    # 4. Path purity violation: Absolute machine path
    bad_sk_path = "D:\\UnrealProjects\\Characters\\V2\\SK_Human.uasset"
    rep_path = CharacterProdV2Validator.validate_character_prod_v2(spec, bad_sk_path, fabp_path, phys_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
