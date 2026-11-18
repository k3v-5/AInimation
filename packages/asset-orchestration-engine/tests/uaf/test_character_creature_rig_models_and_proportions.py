"""
Tests for Character Creature Rig Models and Proportions.
UAF-81.33 Sections 2, 3, 4, 6, 8, 9, 128.
"""

from uaf.character_creature_rig.models.definition import (
    CharacterType33,
    CharacterGenerationStrategy33,
    CharacterBodyProportions33,
    CharacterCreatureRigDefinition,
)


def test_character_body_proportions_and_bounds():
    prop_ok = CharacterBodyProportions33(height_cm=180.0, shoulder_width_cm=45.0, chest_width_cm=40.0)
    assert prop_ok.is_valid is True

    prop_tiny = CharacterBodyProportions33(height_cm=30.0)  # < 50cm
    assert prop_tiny.is_valid is False

    prop_giant = CharacterBodyProportions33(height_cm=500.0)  # > 400cm
    assert prop_giant.is_valid is False


def test_character_creature_rig_definition_and_hashing():
    prop = CharacterBodyProportions33(height_cm=185.0)
    c_def = CharacterCreatureRigDefinition(
        character_id="Char_Spec_Warrior",
        character_type=CharacterType33.PLAYER,
        strategy=CharacterGenerationStrategy33.HYBRID,
        proportions=prop,
        bone_count=65,
        has_facial_rig=True,
        has_clothing=True,
        seed=112233,
    )

    assert c_def.is_valid_skeleton is True
    assert len(c_def.definition_hash) == 64
    data = c_def.to_dict()
    assert data["character_type"] == "PLAYER"
    assert data["strategy"] == "HYBRID"
    assert data["bone_count"] == 65

    bad_skeleton = CharacterCreatureRigDefinition(
        character_id="Char_Bad_Skel",
        character_type=CharacterType33.ROBOT,
        bone_count=8,  # < 15 bones
    )
    assert bad_skeleton.is_valid_skeleton is False
