"""
Tests for Character Production Models and Readiness Classes.
UAF-81.29 Sections 2, 3, 4, 5, 6, 80 to 85.
"""

from uaf.character_production.models.definition import (
    CharacterType29,
    CharacterReadinessClass,
    ProductionBodyProportions,
    ProductionCharacterDefinition,
)


def test_production_body_proportions_and_bounds():
    prop_ok = ProductionBodyProportions(height_cm=180.0)
    assert prop_ok.is_valid is True

    prop_too_small = ProductionBodyProportions(height_cm=30.0)
    assert prop_too_small.is_valid is False

    prop_too_tall = ProductionBodyProportions(height_cm=450.0)
    assert prop_too_tall.is_valid is False


def test_production_character_definition_and_hashing():
    prop = ProductionBodyProportions(height_cm=175.0)
    c_def = ProductionCharacterDefinition(
        character_id="Char_Protagonist_Spec",
        character_type=CharacterType29.HUMAN,
        proportions=prop,
        bone_count=65,
        has_facial_morphs=True,
        has_eye_rig=True,
        has_hand_rig=True,
        readiness_class=CharacterReadinessClass.UNREAL_READY_CHARACTER,
        seed=778899,
    )

    assert c_def.character_type == "HUMAN"
    assert c_def.readiness_class == "UNREAL_READY_CHARACTER"
    assert len(c_def.definition_hash) == 64
    data = c_def.to_dict()
    assert data["bone_count"] == 65
    assert data["has_facial_morphs"] is True
