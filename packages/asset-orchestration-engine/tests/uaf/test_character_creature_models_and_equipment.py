"""
Tests for Character Creature Models and Modular Equipment.
UAF-81.21 Sections 3, 4, 8, 9, 18, 19, 20.
"""

from uaf.character_creature.models.definition import (
    CharacterSpecies,
    AnatomicalLandmarks,
    CharacterDefinition21,
)
from uaf.character_creature.models.equipment import (
    BodyPartType,
    EquipmentLayerType,
    ModularEquipmentLayer,
)


def test_character_definition_and_hashing():
    landmarks = AnatomicalLandmarks(pelvis_height=98.0, shoulder_width=44.0, arm_length=74.0, leg_length=96.0)
    char_def = CharacterDefinition21(
        "Char_Spec_Vanguard",
        CharacterSpecies.HUMAN,
        height_cm=182.0,
        mass_kg=78.0,
        generation_strategy="HYBRID",
        landmarks=landmarks,
        seed=112233,
    )
    assert char_def.species == "HUMAN"
    assert char_def.landmarks.arm_length == 74.0
    assert len(char_def.definition_hash) == 64
    data = char_def.to_dict()
    assert data["species"] == "HUMAN"


def test_modular_equipment_layer():
    layer = ModularEquipmentLayer("Vest_Tac", EquipmentLayerType.ARMOR_CHEST, is_rigid=True, clearance_mm=4.0)
    assert layer.is_rigid is True
    assert layer.clearance_mm == 4.0
    data = layer.to_dict()
    assert data["layer_type"] == "ARMOR_CHEST"
