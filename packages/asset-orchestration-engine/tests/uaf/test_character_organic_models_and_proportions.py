"""
Tests for Organic Character Models and Proportions.
UAF-81.26 Sections 3, 4, 6, 7, 20, 114, 115.
"""

from uaf.character_organic.models.definition import (
    CharacterArchetype26,
    CharacterProportions,
    LayeredClothingItem,
    OrganicCharacterDefinition,
)


def test_character_proportions_and_bounds():
    prop_ok = CharacterProportions(height_cm=180.0)
    assert prop_ok.is_valid is True

    prop_too_short = CharacterProportions(height_cm=20.0)
    assert prop_too_short.is_valid is False

    prop_too_tall = CharacterProportions(height_cm=500.0)
    assert prop_too_tall.is_valid is False


def test_organic_character_definition_and_hashing():
    prop = CharacterProportions(height_cm=175.0)
    cloth = [
        LayeredClothingItem("Jacket", "TORSO", thickness_mm=3.0, clearance_mm=1.5),
    ]
    c_def = OrganicCharacterDefinition(
        "Char_Hero_Spec",
        CharacterArchetype26.HUMAN,
        prop,
        cloth,
        hair_style="HAIR_PONYTAIL",
        has_facial_landmarks=True,
        seed=112233,
    )

    assert c_def.archetype == "HUMAN"
    assert len(c_def.definition_hash) == 64
    data = c_def.to_dict()
    assert data["hair_style"] == "HAIR_PONYTAIL"
    assert len(data["clothing_layers"]) == 1
