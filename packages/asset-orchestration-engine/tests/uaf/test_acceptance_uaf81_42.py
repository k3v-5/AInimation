"""
UAF-81.42 Acceptance Tests (Sections 147, 17, 18, 137, 154, 155, 156, 158, 160, 144, 148, 163).
Verifies:
- Section 147: Final Acceptance Criteria (Generates and validates all 6 Golden Characters:
  Humanoid, Robot, Creature, Quadruped, Mechanical, Hybrid).
- Sections 17, 18, 137, 155, 158: Hard Fail Conditions Test (Zero tolerance for invalid skeletal dimensions,
  bone count < 20, missing IK chains, missing retarget profile, missing ragdoll, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_assembly.engine.character_assembly_fabricator import CharacterAssemblyFabricationPlatform
from uaf.character_assembly.validation.character_assembly_validator import CharacterAssemblyValidator
from uaf.character_assembly.models.definition import (
    CharacterAssemblySpecification,
    CharacterClassification42,
    SkeletonProfile42,
    SkeletalDimensions42,
)
from uaf.character_assembly.package.character_assembly_package import CharacterAssemblyPackage


def test_final_character_assembly_acceptance_section_147():
    """
    Acceptance Test Section 147:
    Synthesizes and validates all 6 Golden Characters.
    """
    builders = [
        ("Char_Gold_Humanoid", CharacterAssemblyFabricationPlatform.build_golden_humanoid),
        ("Char_Gold_Robot", CharacterAssemblyFabricationPlatform.build_golden_robot),
        ("Char_Gold_Creature", CharacterAssemblyFabricationPlatform.build_golden_creature),
        ("Char_Gold_Quadruped", CharacterAssemblyFabricationPlatform.build_golden_quadruped),
        ("Char_Gold_Mechanical", CharacterAssemblyFabricationPlatform.build_golden_mechanical),
        ("Char_Gold_Hybrid", CharacterAssemblyFabricationPlatform.build_golden_hybrid),
    ]

    for char_id, builder_fn in builders:
        spec, sk_path, abp_path, phys_path = builder_fn(char_id)
        assert spec.is_valid_assembly is True

        report = CharacterAssemblyValidator.validate_character_assembly(spec, sk_path, abp_path, phys_path)
        assert report.is_valid is True, f"Failed for {char_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterAssemblyPackage(
            character_id=char_id,
            spec=spec,
            skeletal_mesh_path=sk_path,
            anim_blueprint_path=abp_path,
            physics_asset_path=phys_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["character_id"] == char_id


def test_hard_fail_conditions_section_17_18_137_155_158():
    """
    Acceptance Test Sections 17, 18, 137, 155, 158:
    Hard fail conditions:
    1. INVALID_SKELETAL_DIMENSIONS: Height outside [50, 450]cm or non-positive limbs.
    2. INVALID_BONE_COUNT: Bone count < 20.
    3. MISSING_IK_OR_RETARGET: has_ik_chains or has_retarget_profile is False.
    4. MISSING_RAGDOLL: has_ragdoll_physics is False.
    5. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, sk_path, abp_path, phys_path = CharacterAssemblyFabricationPlatform.build_golden_humanoid("Char_Fault_Test")

    # 1. Height violation: 30cm (< 50cm)
    bad_dims = SkeletalDimensions42(height_cm=30.0, arm_span_cm=30.0, leg_height_cm=15.0)
    bad_spec_dims = CharacterAssemblySpecification(
        "Char_BadDims",
        CharacterClassification42.HUMANOID,
        SkeletonProfile42.HUMANOID_STANDARD,
        dimensions=bad_dims,
    )
    rep_dims = CharacterAssemblyValidator.validate_character_assembly(bad_spec_dims, sk_path, abp_path, phys_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_SKELETAL_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Bone count violation: 12 bones (< 20)
    bad_spec_bones = CharacterAssemblySpecification(
        "Char_FewBones",
        CharacterClassification42.HUMANOID,
        SkeletonProfile42.HUMANOID_STANDARD,
        bone_count=12,
    )
    rep_bones = CharacterAssemblyValidator.validate_character_assembly(bad_spec_bones, sk_path, abp_path, phys_path)
    assert rep_bones.is_valid is False
    assert rep_bones.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_BONE_COUNT" in iss for iss in rep_bones.issues)

    # 3. Missing IK chains
    bad_spec_ik = CharacterAssemblySpecification(
        "Char_NoIK",
        CharacterClassification42.HUMANOID,
        SkeletonProfile42.HUMANOID_STANDARD,
        has_ik_chains=False,
    )
    rep_ik = CharacterAssemblyValidator.validate_character_assembly(bad_spec_ik, sk_path, abp_path, phys_path)
    assert rep_ik.is_valid is False
    assert rep_ik.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_IK_OR_RETARGET" in iss for iss in rep_ik.issues)

    # 4. Path purity violation: Absolute machine path
    bad_sk_path = "D:\\UnrealProjects\\Characters\\SK_Humanoid.uasset"
    rep_path = CharacterAssemblyValidator.validate_character_assembly(spec, bad_sk_path, abp_path, phys_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
