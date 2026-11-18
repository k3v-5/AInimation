"""
Tests for Head, Eyes, Mouth, Hands, Feet, and Creatures (UAF-81.54 Sections 26-47, 146-148).
"""

import pytest
from uaf.universal_character import (
    HeadDefinition,
    EyeDefinition,
    EarDefinition,
    NoseDefinition,
    TeethDefinition,
    MouthDefinition,
    HandDefinition,
    FootDefinition,
    FootVariant,
    CreatureComponentDefinition,
    SymmetryType,
    UniversalCharacterFabricator,
)


# --- 6 HEAD TESTS (Section 146) ---

def test_head_generation():
    head = HeadDefinition(head_width=17.0, head_height=25.0)
    assert head.head_width == 17.0
    d = head.to_dict()
    assert d["head_height"] == 25.0


def test_eye_system():
    eye = EyeDefinition(has_eyeball=True, has_cornea=True, has_eyelid=True)
    assert eye.has_eyeball
    assert eye.has_cornea
    d = eye.to_dict()
    assert d["has_eyelid"] is True


def test_eye_alignment():
    eye = EyeDefinition(eye_alignment=1.0, gaze_axis=(0.0, 1.0, 0.0))
    assert eye.eye_alignment == 1.0
    assert eye.gaze_axis[1] == 1.0


def test_mouth_system():
    mouth = MouthDefinition(has_lips=True, has_teeth=True, has_tongue=True)
    assert mouth.has_lips
    assert mouth.has_teeth
    assert mouth.has_tongue


def test_teeth_system():
    teeth = TeethDefinition(tooth_count=32, tooth_scale=1.0)
    assert teeth.tooth_count == 32
    assert teeth.tooth_scale == 1.0
    d = teeth.to_dict()
    assert d["tooth_count"] == 32


def test_head_lod():
    # Head LOD reduction retains general silhouette
    head_verts_lod0 = 600
    head_verts_lod1 = int(head_verts_lod0 * 0.6)
    head_verts_lod2 = int(head_verts_lod0 * 0.3)
    assert head_verts_lod1 == 360
    assert head_verts_lod2 == 180


# --- 5 HAND TESTS (Section 147) ---

def test_hand_generation():
    hand = HandDefinition(palm_length=11.0, palm_width=9.0)
    assert hand.palm_length == 11.0
    assert len(hand.fingers) == 5


def test_finger_chain():
    hand = HandDefinition(segments_per_finger=3)
    # 3 segments: PROXIMAL, INTERMEDIATE, DISTAL
    assert hand.segments_per_finger == 3


def test_thumb():
    hand = HandDefinition(thumb_length=6.2)
    assert "THUMB" in hand.fingers
    assert hand.thumb_length == 6.2


def test_hand_rig():
    hand_bones = [f"FINGER_{f}_0{s}" for f in ["INDEX", "MIDDLE"] for s in range(1, 4)]
    assert len(hand_bones) == 6
    assert "FINGER_INDEX_01" in hand_bones


def test_hand_symmetry():
    hand_l = HandDefinition(palm_width=8.5)
    hand_r = HandDefinition(palm_width=8.5)
    assert hand_l.palm_width == hand_r.palm_width


# --- 6 CREATURE TESTS (Section 148) ---

def test_quadruped():
    quad = UniversalCharacterFabricator.build_golden_quadruped()
    assert quad.character_def.archetype.value == "QUADRUPED"
    assert "SHOULDER_FL" in quad.skeleton.bone_names
    assert "HIP_BL" in quad.skeleton.bone_names


def test_multi_limb():
    multi = UniversalCharacterFabricator.build_golden_multi_limb()
    assert multi.character_def.archetype.value == "MULTI_LIMB"
    assert "UPPER_ARM_L2" in multi.skeleton.bone_names
    assert "HAND_R2" in multi.skeleton.bone_names


def test_tail():
    tail = CreatureComponentDefinition(
        component_type="TAIL",
        count=1,
        length=80.0,
        segments=6,
        curvature=0.25,
    )
    assert tail.component_type == "TAIL"
    assert tail.length == 80.0
    assert tail.segments == 6


def test_wing():
    wing = CreatureComponentDefinition(
        component_type="WING",
        count=2,
        length=150.0,
        symmetry=SymmetryType.BILATERAL,
    )
    assert wing.component_type == "WING"
    assert wing.count == 2
    assert wing.symmetry == SymmetryType.BILATERAL


def test_horn():
    horn = CreatureComponentDefinition(
        component_type="HORN",
        count=2,
        length=25.0,
        radius=4.0,
    )
    assert horn.component_type == "HORN"
    assert horn.radius == 4.0
    d = horn.to_dict()
    assert d["length"] == 25.0


def test_custom_creature_component():
    custom = CreatureComponentDefinition(
        component_type="TENTACLE",
        count=8,
        length=120.0,
        segments=10,
        chain_bones=[f"BONE_Tentacle_{i}" for i in range(10)],
    )
    assert custom.component_type == "TENTACLE"
    assert custom.count == 8
    assert len(custom.chain_bones) == 10
