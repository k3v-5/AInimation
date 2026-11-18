"""
UAF-81.49 Acceptance Tests (Sections 140, 139, 145, 146, 141, 157).
Verifies:
- Section 140: Final Acceptance Criteria (Generates and validates all 5 Golden Characters:
  Human, Robot, Creature, Boss, Armored Character).
- Sections 139, 145, 146: Hard Fail Conditions Test (Zero tolerance for invalid anatomical dimensions,
  bone count < 20, missing ragdoll physics, player missing facial rig or clothing, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_creature_system.engine.character_creature_fabricator import CharacterCreatureFabricationPlatform
from uaf.character_creature_system.validation.character_creature_validator import CharacterCreatureValidator
from uaf.character_creature_system.models.definition import (
    CharacterCreatureSpecification,
    CharacterType49,
    SpeciesType49,
    BodyDimensions49,
)
from uaf.character_creature_system.package.character_creature_package import CharacterCreaturePackage


def test_final_character_creature_acceptance_section_140():
    """
    Acceptance Test Section 140:
    Synthesizes and validates all 5 Golden Characters.
    """
    builders = [
        ("Char_Gold_Human49", CharacterCreatureFabricationPlatform.build_golden_human),
        ("Char_Gold_Robot49", CharacterCreatureFabricationPlatform.build_golden_robot),
        ("Char_Gold_Creature49", CharacterCreatureFabricationPlatform.build_golden_creature),
        ("Char_Gold_Boss49", CharacterCreatureFabricationPlatform.build_golden_boss),
        ("Char_Gold_Armored49", CharacterCreatureFabricationPlatform.build_golden_armored_character),
    ]

    for char_id, builder_fn in builders:
        spec, sk_path, abp_path, phys_path = builder_fn(char_id)
        assert spec.is_valid_production is True

        report = CharacterCreatureValidator.validate_character_creature(spec, sk_path, abp_path, phys_path)
        assert report.is_valid is True, f"Failed for {char_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterCreaturePackage(
            character_id=char_id,
            spec=spec,
            skeletal_mesh_path=sk_path,
            anim_blueprint_path=abp_path,
            physics_asset_path=phys_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["character_id"] == char_id


def test_hard_fail_conditions_section_139_145_146():
    """
    Acceptance Test Sections 139, 145, 146:
    Hard fail conditions:
    1. INVALID_ANATOMICAL_DIMENSIONS: Height outside [50, 500]cm or non-positive spans.
    2. INVALID_BONE_COUNT: Bone count < 20.
    3. MISSING_CORE_SUBSYSTEMS: Missing ragdoll, or player character missing facial rig or clothing/armor.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, sk_path, abp_path, phys_path = CharacterCreatureFabricationPlatform.build_golden_human("Char_Fault_Test")

    # 1. Height violation: 30cm (< 50cm)
    bad_dims = BodyDimensions49(height_cm=30.0, shoulder_width_cm=20.0, chest_width_cm=15.0, waist_width_cm=10.0, pelvis_width_cm=12.0, arm_length_cm=10.0, leg_length_cm=10.0)
    bad_spec_dims = CharacterCreatureSpecification(
        "Char_Midget",
        CharacterType49.PLAYER,
        SpeciesType49.HUMAN,
        dimensions=bad_dims,
    )
    rep_dims = CharacterCreatureValidator.validate_character_creature(bad_spec_dims, sk_path, abp_path, phys_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_ANATOMICAL_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Bone count violation: 15 bones (< 20)
    bad_spec_bones = CharacterCreatureSpecification(
        "Char_FewBones",
        CharacterType49.PLAYER,
        SpeciesType49.HUMAN,
        bone_count=15,
    )
    rep_bones = CharacterCreatureValidator.validate_character_creature(bad_spec_bones, sk_path, abp_path, phys_path)
    assert rep_bones.is_valid is False
    assert rep_bones.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_BONE_COUNT" in iss for iss in rep_bones.issues)

    # 3. Missing ragdoll physics
    bad_spec_rag = CharacterCreatureSpecification(
        "Char_NoRagdoll",
        CharacterType49.PLAYER,
        SpeciesType49.HUMAN,
        has_ragdoll=False,
    )
    rep_rag = CharacterCreatureValidator.validate_character_creature(bad_spec_rag, sk_path, abp_path, phys_path)
    assert rep_rag.is_valid is False
    assert rep_rag.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_rag.issues)

    # 4. Path purity violation: Absolute machine path
    bad_sk_path = "D:\\UnrealProjects\\Characters\\SK_Hero.uasset"
    rep_path = CharacterCreatureValidator.validate_character_creature(spec, bad_sk_path, abp_path, phys_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
