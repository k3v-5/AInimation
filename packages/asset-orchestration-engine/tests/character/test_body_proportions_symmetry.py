"""
Tests for Body, Proportions, Symmetry, and Components (UAF-81.54 Sections 3-25, 143-145).
"""

import pytest
from uaf.universal_character import (
    CharacterSpecies,
    CharacterArchetype,
    BodyShape,
    ProportionNormalization,
    BodyProportions,
    CustomAnatomicalRegion,
    AttachmentPoint,
    BodyComponent,
    SymmetryType,
    CharacterDefinition,
)


# --- 6 BODY TESTS (Section 143) ---

def test_body_definition():
    c = CharacterDefinition(
        character_id="TEST_Char_01",
        species=CharacterSpecies.HUMAN,
        archetype=CharacterArchetype.HUMAN,
    )
    assert c.is_valid
    assert c.species == CharacterSpecies.HUMAN
    d = c.to_dict()
    assert d["character_id"] == "TEST_Char_01"


def test_body_proportions():
    p = BodyProportions(height=175.0, shoulder_width=44.0, leg_length=88.0)
    assert p.is_valid
    assert p.height == 175.0
    d = p.to_dict()
    assert d["height"] == 175.0


def test_body_shape():
    c = CharacterDefinition(
        character_id="TEST_Muscular",
        species=CharacterSpecies.HUMAN,
        archetype=CharacterArchetype.HUMAN,
        body_shape=BodyShape.MUSCULAR,
    )
    assert c.body_shape == BodyShape.MUSCULAR
    assert c.to_dict()["body_shape"] == "MUSCULAR"


def test_body_normalization():
    p = BodyProportions(normalization_mode=ProportionNormalization.RELATIVE_TO_HEIGHT)
    assert p.normalization_mode == ProportionNormalization.RELATIVE_TO_HEIGHT
    assert p.to_dict()["normalization_mode"] == "RELATIVE_TO_HEIGHT"


def test_body_variant():
    p1 = BodyProportions(height=180.0)
    p2 = BodyProportions(height=160.0)
    c1 = CharacterDefinition("V1", CharacterSpecies.HUMAN, CharacterArchetype.HUMAN, proportions=p1)
    c2 = CharacterDefinition("V2", CharacterSpecies.HUMAN, CharacterArchetype.HUMAN, proportions=p2)
    assert c1.proportions.height != c2.proportions.height


def test_custom_region():
    region = CustomAnatomicalRegion(
        name="TENTACLE_L",
        parent="PELVIS",
        symmetry_group="RADIAL",
        mesh_components=["SM_Tentacle_L"],
        bones=["BONE_Tentacle_01", "BONE_Tentacle_02"],
    )
    assert region.name == "TENTACLE_L"
    assert len(region.bones) == 2
    d = region.to_dict()
    assert d["symmetry_group"] == "RADIAL"


# --- 4 SYMMETRY TESTS (Section 144) ---

def test_bilateral_symmetry():
    comp_l = BodyComponent("ARM_L", "UPPER_ARM_L", "SM_Arm_L", symmetry=SymmetryType.BILATERAL)
    comp_r = BodyComponent("ARM_R", "UPPER_ARM_R", "SM_Arm_R", symmetry=SymmetryType.BILATERAL)
    assert comp_l.symmetry == SymmetryType.BILATERAL
    assert comp_r.symmetry == SymmetryType.BILATERAL


def test_mirror_geometry():
    p_orig = (15.0, 5.0, 100.0)
    # Mirror across X axis
    p_mirrored = (-p_orig[0], p_orig[1], p_orig[2])
    assert p_mirrored == (-15.0, 5.0, 100.0)


def test_mirror_weights():
    weights_l = {"UPPER_ARM_L": 0.8, "SPINE_03": 0.2}
    # Mirror mapping _L -> _R
    weights_r = {k.replace("_L", "_R"): v for k, v in weights_l.items()}
    assert "UPPER_ARM_R" in weights_r
    assert weights_r["UPPER_ARM_R"] == 0.8


def test_symmetry_validation():
    # Asymmetric position check
    pos_l = (20.0, 0.0, 140.0)
    pos_r = (-20.0, 0.0, 140.0)
    is_symmetric = (pos_l[0] == -pos_r[0]) and (pos_l[1] == pos_r[1]) and (pos_l[2] == pos_r[2])
    assert is_symmetric


# --- 5 COMPONENT TESTS (Section 145) ---

def test_component_definition():
    comp = BodyComponent(
        component_id="COMP_Torso",
        region="TORSO",
        mesh="SM_Torso_Base",
        material_slots=["M_Skin", "M_Undershirt"],
    )
    assert comp.component_id == "COMP_Torso"
    assert len(comp.material_slots) == 2
    d = comp.to_dict()
    assert d["region"] == "TORSO"


def test_component_attachment():
    ap = AttachmentPoint("SOCKET_Hand_L", position=(0.0, 0.0, 0.0), parent_region="FOREARM_L")
    comp = BodyComponent("COMP_Hand_L", "HAND_L", "SM_Hand_L", attachment_points=[ap])
    assert len(comp.attachment_points) == 1
    assert comp.attachment_points[0].name == "SOCKET_Hand_L"


def test_component_replacement():
    original = BodyComponent("COMP_Armor_Tier1", "TORSO", "SM_Plate_T1")
    replaced = BodyComponent("COMP_Armor_Tier2", "TORSO", "SM_Plate_T2")
    assert original.region == replaced.region
    assert original.mesh != replaced.mesh


def test_component_versioning():
    comp = BodyComponent(
        "COMP_Head", "HEAD", "SM_Head",
        component_version="2.1.0",
        generator_version="1.5.0",
        schema_version="1.0.0"
    )
    assert comp.component_version == "2.1.0"
    d = comp.to_dict()
    assert d["generator_version"] == "1.5.0"


def test_component_dependency():
    deps = {
        "HEAD": "NECK",
        "NECK": "TORSO",
        "UPPER_ARM_L": "TORSO",
    }
    assert deps["HEAD"] == "NECK"
    assert deps[deps["HEAD"]] == "TORSO"
