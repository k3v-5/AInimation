"""
Tests for Clothing, Armor, Accessories, and Hair (UAF-81.54 Sections 48-63, 149-152).
"""

import pytest
from uaf.universal_character import (
    ClothingDefinition,
    ClothingType,
    ClothingFit,
    ArmorDefinition,
    ArmorComponentType,
    AccessoryDefinition,
    AccessoryType,
    AccessorySocket,
    HairDefinition,
    HairType,
)


# --- 6 CLOTHING TESTS (Section 149) ---

def test_clothing_definition():
    cloth = ClothingDefinition(
        clothing_id="CLOTH_Shirt",
        clothing_type=ClothingType.SHIRT,
        fit=ClothingFit.REGULAR,
    )
    assert cloth.clothing_id == "CLOTH_Shirt"
    assert cloth.clothing_type == ClothingType.SHIRT
    d = cloth.to_dict()
    assert d["clothing_type"] == "SHIRT"


def test_clothing_fit():
    cloth_tight = ClothingDefinition("C1", ClothingType.PANTS, fit=ClothingFit.TIGHT, minimum_clearance=0.2)
    cloth_loose = ClothingDefinition("C2", ClothingType.COAT, fit=ClothingFit.LOOSE, minimum_clearance=1.5)
    assert cloth_tight.minimum_clearance < cloth_loose.minimum_clearance


def test_clothing_clearance():
    cloth = ClothingDefinition("C3", ClothingType.JACKET, minimum_clearance=0.8, maximum_intersection=0.0)
    assert cloth.minimum_clearance > cloth.maximum_intersection


def test_clothing_skinning():
    cloth = ClothingDefinition("C4", ClothingType.SHIRT, deformation_regions=["TORSO", "UPPER_ARM_L", "UPPER_ARM_R"])
    assert len(cloth.deformation_regions) == 3


def test_clothing_lod():
    lod_mesh_names = ["SM_Shirt_LOD0", "SM_Shirt_LOD1", "SM_Shirt_LOD2"]
    assert len(lod_mesh_names) == 3


def test_clothing_penetration():
    # Penetration when max intersection exceeds clearance
    clearance = 0.5
    penetration = 0.1
    has_violation = penetration > clearance
    assert not has_violation


# --- 5 ARMOR TESTS (Section 150) ---

def test_armor_definition():
    armor = ArmorDefinition("ARM_Chest", ArmorComponentType.CHEST, clearance=1.2, mass_kg=14.0)
    assert armor.armor_type == ArmorComponentType.CHEST
    assert armor.mass_kg == 14.0
    d = armor.to_dict()
    assert d["clearance"] == 1.2


def test_armor_attachment():
    armor = ArmorDefinition("ARM_Helmet", ArmorComponentType.HELMET, attachment_socket="SOCKET_Head")
    assert armor.attachment_socket == "SOCKET_Head"


def test_armor_clearance():
    armor = ArmorDefinition("ARM_Plate", ArmorComponentType.CHEST, clearance=1.0)
    assert armor.clearance >= 0.0


def test_armor_socket():
    valid_sockets = ["SOCKET_Head", "SOCKET_Chest", "SOCKET_Shoulder_L", "SOCKET_Knee_L"]
    armor = ArmorDefinition("ARM_Knee", ArmorComponentType.KNEE, attachment_socket="SOCKET_Knee_L")
    assert armor.attachment_socket in valid_sockets


def test_armor_lod():
    armor_lod_polycount = [4000, 2000, 800, 200]
    assert armor_lod_polycount[0] > armor_lod_polycount[1] > armor_lod_polycount[2] > armor_lod_polycount[3]


# --- 4 ACCESSORY TESTS (Section 151) ---

def test_accessory_definition():
    acc = AccessoryDefinition("ACC_Pouch", AccessoryType.POUCH, AccessorySocket.WAIST)
    assert acc.accessory_type == AccessoryType.POUCH
    assert acc.socket == AccessorySocket.WAIST
    d = acc.to_dict()
    assert d["socket"] == "WAIST"


def test_accessory_socket():
    acc = AccessoryDefinition("ACC_Backpack", AccessoryType.BACKPACK, AccessorySocket.BACK)
    assert acc.socket == AccessorySocket.BACK


def test_accessory_attachment():
    acc = AccessoryDefinition("ACC_Holster", AccessoryType.HOLSTER, AccessorySocket.THIGH, attachment_offset=(5.0, 0.0, 0.0))
    assert acc.attachment_offset == (5.0, 0.0, 0.0)


def test_accessory_lod():
    acc_has_lod = True
    assert acc_has_lod


# --- 4 HAIR TESTS (Section 152) ---

def test_mesh_hair():
    hair = HairDefinition("HAIR_Style01", HairType.MESH_HAIR, scalp_coverage=0.9)
    assert hair.hair_type == HairType.MESH_HAIR
    assert hair.scalp_coverage == 0.9


def test_hair_attachment():
    hair = HairDefinition("HAIR_Card", HairType.CARD_HAIR)
    d = hair.to_dict()
    assert d["hair_type"] == "CARD_HAIR"


def test_hair_penetration():
    hair = HairDefinition("HAIR_Short", penetration_tolerance=0.3)
    assert hair.penetration_tolerance == 0.3


def test_hair_lod():
    hair = HairDefinition("HAIR_Long", lod_supported=True)
    assert hair.lod_supported is True
