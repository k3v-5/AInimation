"""
Tests for Character Assembly Models, Skeletal Dimensions, and Rigging Profiles.
UAF-81.42 Sections 3, 5, 8, 15, 24, 29, 147.
"""

from uaf.character_assembly.models.definition import (
    CharacterClassification42,
    SkeletonProfile42,
    ControlRigType42,
    RetargetProfile42,
    SkeletalDimensions42,
    CharacterAssemblySpecification,
)


def test_skeletal_dimensions_and_validity():
    dims_ok = SkeletalDimensions42(height_cm=180.0, arm_span_cm=175.0, leg_height_cm=95.0)
    assert dims_ok.is_valid is True

    dims_too_short = SkeletalDimensions42(height_cm=30.0)  # < 50.0cm
    assert dims_too_short.is_valid is False

    dims_too_tall = SkeletalDimensions42(height_cm=500.0)  # > 450.0cm
    assert dims_too_tall.is_valid is False

    dims_neg_arm = SkeletalDimensions42(height_cm=180.0, arm_span_cm=-10.0)
    assert dims_neg_arm.is_valid is False


def test_character_assembly_specification_and_hashing():
    spec = CharacterAssemblySpecification(
        character_id="Char_Test_Warrior",
        classification=CharacterClassification42.HUMANOID,
        skeleton_profile=SkeletonProfile42.HUMANOID_STANDARD,
        dimensions=SkeletalDimensions42(height_cm=185.0, arm_span_cm=180.0, leg_height_cm=95.0),
        retarget_profile=RetargetProfile42.UNREAL_MANNEQUIN,
        bone_count=68,
        has_ik_chains=True,
        has_retarget_profile=True,
        has_ragdoll_physics=True,
        seed=112233,
    )

    assert spec.is_valid_assembly is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["classification"] == "HUMANOID"
    assert data["bone_count"] == 68

    bad_spec_bones = CharacterAssemblySpecification(
        character_id="Char_TooFewBones",
        classification=CharacterClassification42.HUMANOID,
        skeleton_profile=SkeletonProfile42.HUMANOID_STANDARD,
        bone_count=10,  # < 20 bones
    )
    assert bad_spec_bones.is_valid_assembly is False
