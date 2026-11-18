"""
Tests for Character Prod V2 Models, Anatomical Dimensions, and Profiles.
UAF-81.45 Sections 4, 5, 9, 20, 138, 146.
"""

from uaf.character_prod_v2.models.definition import (
    CharacterArchetype45,
    ProportionProfile45,
    SymmetryMode45,
    PlatformProfile45,
    AnatomicalDimensions45,
    CharacterProdV2Specification,
)


def test_anatomical_dimensions_and_validity():
    dims_ok = AnatomicalDimensions45(height_cm=180.0, shoulder_width_cm=45.0, chest_depth_cm=28.0, torso_length_cm=60.0, arm_length_cm=75.0, leg_length_cm=95.0)
    assert dims_ok.is_valid is True

    dims_too_short = AnatomicalDimensions45(height_cm=40.0)  # < 50.0cm
    assert dims_too_short.is_valid is False

    dims_too_tall = AnatomicalDimensions45(height_cm=480.0)  # > 450.0cm
    assert dims_too_tall.is_valid is False

    dims_neg_arm = AnatomicalDimensions45(height_cm=180.0, arm_length_cm=-5.0)
    assert dims_neg_arm.is_valid is False


def test_character_prod_v2_specification_and_hashing():
    spec = CharacterProdV2Specification(
        character_id="Char_Test_Hero",
        archetype=CharacterArchetype45.HUMAN,
        proportion_profile=ProportionProfile45.HEROIC,
        symmetry_mode=SymmetryMode45.FULL,
        platform_profile=PlatformProfile45.PC_HIGH,
        dimensions=AnatomicalDimensions45(height_cm=185.0, shoulder_width_cm=48.0, chest_depth_cm=30.0, torso_length_cm=62.0, arm_length_cm=78.0, leg_length_cm=96.0),
        bone_count=72,
        has_facial_rig=True,
        has_clothing=True,
        has_hair=True,
        has_physics_asset=True,
        seed=445566,
    )

    assert spec.is_valid_production is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["archetype"] == "HUMAN"
    assert data["bone_count"] == 72

    bad_spec_bones = CharacterProdV2Specification(
        character_id="Char_TooFewBones",
        archetype=CharacterArchetype45.HUMAN,
        proportion_profile=ProportionProfile45.HEROIC,
        bone_count=10,  # < 20
    )
    assert bad_spec_bones.is_valid_production is False
