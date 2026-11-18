"""
UAF-81.37 Acceptance Tests (Sections 136, 133, 151, 152, 153, 155).
Verifies:
- Section 136: Final Acceptance Criteria (Generates and validates all 10 Golden Characters:
  Human Male, Human Female, Heavy Soldier, Light Soldier, Robot, Android, Alien, Creature, Boss, Armored Character).
- Sections 133, 151, 153: Hard Fail Conditions Test (Zero tolerance for invalid proportions, insufficient bone count,
  missing physics asset, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.character_pipeline.engine.character_pipeline_fabricator import CharacterPipelineFabricationPlatform
from uaf.character_pipeline.validation.character_pipeline_validator import CharacterPipelineValidator
from uaf.character_pipeline.models.definition import (
    CharacterProductionSpecification,
    CharacterArchetype37,
    CharacterProportions37,
)
from uaf.character_pipeline.package.character_pipeline_package import CharacterPipelinePackage


def test_final_character_pipeline_acceptance_section_136():
    """
    Acceptance Test Section 136:
    Synthesizes and validates all 10 Golden Characters.
    """
    builders = [
        ("Char_Gold_HumanMale", CharacterPipelineFabricationPlatform.build_golden_human_male),
        ("Char_Gold_HumanFemale", CharacterPipelineFabricationPlatform.build_golden_human_female),
        ("Char_Gold_HeavySoldier", CharacterPipelineFabricationPlatform.build_golden_heavy_soldier),
        ("Char_Gold_LightSoldier", CharacterPipelineFabricationPlatform.build_golden_light_soldier),
        ("Char_Gold_Robot", CharacterPipelineFabricationPlatform.build_golden_robot),
        ("Char_Gold_Android", CharacterPipelineFabricationPlatform.build_golden_android),
        ("Char_Gold_Alien", CharacterPipelineFabricationPlatform.build_golden_alien),
        ("Char_Gold_Creature", CharacterPipelineFabricationPlatform.build_golden_creature),
        ("Char_Gold_Boss", CharacterPipelineFabricationPlatform.build_golden_boss),
        ("Char_Gold_Armored", CharacterPipelineFabricationPlatform.build_golden_armored_character),
    ]

    for char_id, builder_fn in builders:
        spec, sk_path, phys_path = builder_fn(char_id)
        assert spec.is_valid_rig_structure is True

        report = CharacterPipelineValidator.validate_character_pipeline(spec, sk_path, phys_path)
        assert report.is_valid is True, f"Failed for {char_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = CharacterPipelinePackage(
            character_id=char_id,
            spec=spec,
            skeletal_mesh_path=sk_path,
            physics_asset_path=phys_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["character_id"] == char_id


def test_hard_fail_conditions_section_133_151_153():
    """
    Acceptance Test Sections 133, 151, 153:
    Hard fail conditions:
    1. INVALID_PROPORTIONS: Height outside [50.0, 450.0] or non-positive limb dimensions.
    2. INVALID_BONE_COUNT: Bone count < 15.
    3. MISSING_PHYSICS_ASSET: has_physics_asset is False.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, sk_path, phys_path = CharacterPipelineFabricationPlatform.build_golden_human_male("Char_Fault_Test")

    # 1. Proportion violation: Height 480.0 cm (> 450.0 cm)
    bad_prop = CharacterProportions37(height_cm=480.0)
    bad_spec_prop = CharacterProductionSpecification(
        "Char_Giant",
        CharacterArchetype37.HUMAN,
        proportions=bad_prop,
    )
    rep_prop = CharacterPipelineValidator.validate_character_pipeline(bad_spec_prop, sk_path, phys_path)
    assert rep_prop.is_valid is False
    assert rep_prop.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_PROPORTIONS" in iss for iss in rep_prop.issues)

    # 2. Bone count violation: 8 bones (< 15)
    bad_spec_bones = CharacterProductionSpecification(
        "Char_FewBones",
        CharacterArchetype37.HUMAN,
        bone_count=8,
    )
    rep_bones = CharacterPipelineValidator.validate_character_pipeline(bad_spec_bones, sk_path, phys_path)
    assert rep_bones.is_valid is False
    assert rep_bones.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_BONE_COUNT" in iss for iss in rep_bones.issues)

    # 3. Physics asset violation: has_physics_asset = False
    bad_spec_phys = CharacterProductionSpecification(
        "Char_NoPhys",
        CharacterArchetype37.HUMAN,
        has_physics_asset=False,
    )
    rep_phys = CharacterPipelineValidator.validate_character_pipeline(bad_spec_phys, sk_path, phys_path)
    assert rep_phys.is_valid is False
    assert rep_phys.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_PHYSICS_ASSET" in iss for iss in rep_phys.issues)

    # 4. Path purity violation: Absolute machine path
    bad_sk_path = "D:\\UnrealProjects\\Characters\\SK_Human.uasset"
    rep_path = CharacterPipelineValidator.validate_character_pipeline(spec, bad_sk_path, phys_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
