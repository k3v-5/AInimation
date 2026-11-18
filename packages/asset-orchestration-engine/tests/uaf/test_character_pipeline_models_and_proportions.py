"""
Tests for Character Pipeline Models, Proportions, and Rig Structures.
UAF-81.37 Sections 4, 5, 6, 7, 8, 9, 10, 18, 20, 136.
"""

from uaf.character_pipeline.models.definition import (
    CharacterArchetype37,
    RigType37,
    ControlType37,
    CharacterProportions37,
    CharacterProductionSpecification,
)


def test_character_proportions_and_bounds():
    prop_ok = CharacterProportions37(height_cm=180.0, shoulder_width_cm=45.0, arm_length_cm=75.0, leg_length_cm=90.0)
    assert prop_ok.is_valid is True

    prop_too_short = CharacterProportions37(height_cm=30.0)  # < 50.0 cm
    assert prop_too_short.is_valid is False

    prop_too_tall = CharacterProportions37(height_cm=500.0)  # > 450.0 cm
    assert prop_too_tall.is_valid is False

    prop_neg_limb = CharacterProportions37(height_cm=180.0, arm_length_cm=-10.0)
    assert prop_neg_limb.is_valid is False


def test_character_production_specification_and_hashing():
    spec = CharacterProductionSpecification(
        character_id="Char_Test_Soldier",
        archetype=CharacterArchetype37.HEAVY,
        proportions=CharacterProportions37(height_cm=190.0, shoulder_width_cm=52.0, arm_length_cm=80.0, leg_length_cm=95.0),
        bone_count=70,
        has_physics_asset=True,
        clothing_items_count=3,
        seed=10101,
    )

    assert spec.is_valid_rig_structure is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["archetype"] == "HEAVY"
    assert data["bone_count"] == 70

    bad_spec_bones = CharacterProductionSpecification(
        character_id="Char_LowBones",
        archetype=CharacterArchetype37.HUMAN,
        bone_count=10,  # < 15
    )
    assert bad_spec_bones.is_valid_rig_structure is False
