"""
Tests for Character Suite Models, Profiles, and Deformation Layers.
UAF-81.14 Sections 4, 5, 21, 24, 25, 154.
"""

from uaf.character_suite.models.profile import (
    CharacterClassification,
    CharacterQualityTier,
    CharacterStyle,
    CharacterProfile,
)
from uaf.character_suite.models.deformation import (
    DeformationProfile,
    FaceProfile,
    CharacterLayer,
)


def test_character_profile_instantiation_and_hash():
    profile = CharacterProfile(
        character_id="Char_Cyber_Operative",
        classification=CharacterClassification.HERO,
        quality_tier=CharacterQualityTier.HIGH,
        style=CharacterStyle.SEMI_REALISTIC,
        height_cm=182.0,
        body_mass_kg=80.0,
        seed=999,
    )
    assert profile.height_cm == 182.0
    assert profile.classification == CharacterClassification.HERO
    assert len(profile.profile_hash) == 64
    data = profile.to_dict()
    assert data["style"] == "SEMI_REALISTIC"


def test_deformation_and_face_profiles():
    deform = DeformationProfile(bone_count=92, max_weights_per_vertex=4, has_dual_quaternion=True)
    assert deform.bone_count == 92
    assert deform.has_dual_quaternion is True

    face = FaceProfile(morph_targets_count=52)
    assert face.morph_targets_count == 52


def test_character_layer_clipping_clearance():
    layer = CharacterLayer("L_ShoulderPads", "ARMOR", "Mesh_Pads", "M_Titanium", clipping_clearance_mm=4.0)
    assert layer.layer_type == "ARMOR"
    assert layer.clipping_clearance_mm == 4.0
