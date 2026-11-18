"""
Tests for Character Creature Models, Dimensions, and Morphology.
UAF-81.49 Sections 4, 5, 6, 8, 10, 140, 158.
"""

from uaf.character_creature_system.models.definition import (
    CharacterType49,
    SpeciesType49,
    BodyRepresentation49,
    BodyDimensions49,
    CharacterCreatureSpecification,
)


def test_body_dimensions_and_validity():
    dims_ok = BodyDimensions49(height_cm=180.0, shoulder_width_cm=46.0, chest_width_cm=38.0, waist_width_cm=32.0, pelvis_width_cm=36.0, arm_length_cm=76.0, leg_length_cm=96.0)
    assert dims_ok.is_valid is True

    dims_too_short = BodyDimensions49(height_cm=30.0)  # < 50.0cm
    assert dims_too_short.is_valid is False

    dims_too_tall = BodyDimensions49(height_cm=550.0)  # > 500.0cm
    assert dims_too_tall.is_valid is False

    dims_neg = BodyDimensions49(height_cm=180.0, leg_length_cm=-10.0)
    assert dims_neg.is_valid is False


def test_character_creature_specification_and_hashing():
    spec = CharacterCreatureSpecification(
        character_id="Char_Test_Spec",
        character_type=CharacterType49.PLAYER,
        species=SpeciesType49.HUMAN,
        body_repr=BodyRepresentation49.HYBRID,
        dimensions=BodyDimensions49(height_cm=182.0, shoulder_width_cm=47.0, chest_width_cm=39.0, waist_width_cm=33.0, pelvis_width_cm=37.0, arm_length_cm=77.0, leg_length_cm=97.0),
        bone_count=72,
        has_clothing=True,
        has_armor=False,
        has_hair=True,
        has_facial_rig=True,
        has_ragdoll=True,
        seed=112233,
    )

    assert spec.is_valid_production is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["character_type"] == "PLAYER"
    assert data["species"] == "HUMAN"
    assert data["bone_count"] == 72

    bad_spec_bones = CharacterCreatureSpecification(
        character_id="Char_TooFewBones",
        character_type=CharacterType49.PLAYER,
        species=SpeciesType49.HUMAN,
        bone_count=12,  # < 20
    )
    assert bad_spec_bones.is_valid_production is False
