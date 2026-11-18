"""
Tests for Determinism, 10 Golden Characters, and End-to-End Pipeline (UAF-81.54 Sections 169, 170, 171, 173).
"""

import pytest
from uaf.universal_character import (
    CharacterSpecies,
    CharacterArchetype,
    BodyProportions,
    HeadDefinition,
    HandDefinition,
    CreatureComponentDefinition,
    ClothingDefinition,
    ClothingType,
    ArmorDefinition,
    ArmorComponentType,
    AccessoryDefinition,
    AccessoryType,
    UniversalCharacterFabricator,
    CharacterValidator,
    CharacterDefinition,
    CharacterLODChain,
)


# --- 15 DETERMINISM TESTS (Section 169) ---

def test_det_body_generation():
    p1 = BodyProportions(height=180.0, shoulder_width=45.0)
    p2 = BodyProportions(height=180.0, shoulder_width=45.0)
    assert p1.to_dict() == p2.to_dict()


def test_det_component_generation():
    m1 = UniversalCharacterFabricator.build_golden_human_male()
    m2 = UniversalCharacterFabricator.build_golden_human_male()
    assert [c.to_dict() for c in m1.components] == [c.to_dict() for c in m2.components]


def test_det_head_generation():
    h1 = HeadDefinition(head_width=16.0, head_height=24.0)
    h2 = HeadDefinition(head_width=16.0, head_height=24.0)
    assert h1.to_dict() == h2.to_dict()


def test_det_hand_generation():
    hd1 = HandDefinition(palm_length=10.5)
    hd2 = HandDefinition(palm_length=10.5)
    assert hd1.to_dict() == hd2.to_dict()


def test_det_creature_generation():
    c1 = CreatureComponentDefinition("TAIL", length=50.0)
    c2 = CreatureComponentDefinition("TAIL", length=50.0)
    assert c1.to_dict() == c2.to_dict()


def test_det_clothing_generation():
    cl1 = ClothingDefinition("C1", ClothingType.SHIRT)
    cl2 = ClothingDefinition("C1", ClothingType.SHIRT)
    assert cl1.to_dict() == cl2.to_dict()


def test_det_armor_generation():
    ar1 = ArmorDefinition("A1", ArmorComponentType.CHEST)
    ar2 = ArmorDefinition("A1", ArmorComponentType.CHEST)
    assert ar1.to_dict() == ar2.to_dict()


def test_det_skeleton_generation():
    s1 = UniversalCharacterFabricator.build_humanoid_skeleton("S_Det")
    s2 = UniversalCharacterFabricator.build_humanoid_skeleton("S_Det")
    assert s1.to_dict() == s2.to_dict()


def test_det_rig_generation():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    r1 = UniversalCharacterFabricator.build_rig(skel, "R_Det")
    r2 = UniversalCharacterFabricator.build_rig(skel, "R_Det")
    assert r1.to_dict() == r2.to_dict()


def test_det_weight_generation():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    w1 = UniversalCharacterFabricator.build_skinning(skel, 100, "W_Det")
    w2 = UniversalCharacterFabricator.build_skinning(skel, 100, "W_Det")
    assert w1.to_dict() == w2.to_dict()


def test_det_weight_transfer():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    w1 = UniversalCharacterFabricator.build_skinning(skel, 50, "WT_1")
    w2 = UniversalCharacterFabricator.build_skinning(skel, 50, "WT_2")
    assert len(w1.weights_per_vertex) == len(w2.weights_per_vertex)


def test_det_morph_generation():
    m1 = UniversalCharacterFabricator.build_morph_system(1200, "M_Det")
    m2 = UniversalCharacterFabricator.build_morph_system(1200, "M_Det")
    assert m1.to_dict() == m2.to_dict()


def test_det_facial_rig():
    m1 = UniversalCharacterFabricator.build_morph_system(1200)
    m2 = UniversalCharacterFabricator.build_morph_system(1200)
    assert m1.facial_rig.to_dict() == m2.facial_rig.to_dict()


def test_det_collision_generation():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    c1 = UniversalCharacterFabricator.build_collision(skel, "COL_Det")
    c2 = UniversalCharacterFabricator.build_collision(skel, "COL_Det")
    assert c1.to_dict() == c2.to_dict()


def test_det_lod_generation():
    lod1 = CharacterLODChain()
    lod2 = CharacterLODChain()
    assert lod1.to_dict() == lod2.to_dict()


# --- 10 GOLDEN CHARACTER TESTS (Section 170, 171) ---

def test_golden_human_male():
    char = UniversalCharacterFabricator.build_golden_human_male()
    assert char.character_def.character_id == "GOLDEN_HUMAN_MALE"
    assert char.validation_report.is_valid is True
    assert char.validation_report.quality_score.aggregate_score == 1.0
    assert char.verify_readback()["readback_passed"] is True


def test_golden_human_female():
    char = UniversalCharacterFabricator.build_golden_human_female()
    assert char.character_def.character_id == "GOLDEN_HUMAN_FEMALE"
    assert char.validation_report.is_valid is True
    assert char.hair is not None
    assert char.verify_readback()["readback_passed"] is True


def test_golden_humanoid():
    char = UniversalCharacterFabricator.build_golden_humanoid()
    assert char.character_def.character_id == "GOLDEN_HUMANOID"
    assert char.validation_report.is_valid is True
    assert char.verify_readback()["readback_passed"] is True


def test_golden_robot():
    char = UniversalCharacterFabricator.build_golden_robot()
    assert char.character_def.character_id == "GOLDEN_ROBOT"
    assert char.validation_report.is_valid is True
    assert len(char.armor) >= 2
    assert char.verify_readback()["readback_passed"] is True


def test_golden_quadruped():
    char = UniversalCharacterFabricator.build_golden_quadruped()
    assert char.character_def.character_id == "GOLDEN_QUADRUPED"
    assert char.validation_report.is_valid is True
    assert "TAIL_01" in char.skeleton.bone_names
    assert char.verify_readback()["readback_passed"] is True


def test_golden_creature():
    char = UniversalCharacterFabricator.build_golden_creature()
    assert char.character_def.character_id == "GOLDEN_CREATURE"
    assert char.validation_report.is_valid is True
    assert "HORN_L" in char.skeleton.bone_names
    assert char.verify_readback()["readback_passed"] is True


def test_golden_multi_limb():
    char = UniversalCharacterFabricator.build_golden_multi_limb()
    assert char.character_def.character_id == "GOLDEN_MULTI_LIMB"
    assert char.validation_report.is_valid is True
    assert "UPPER_ARM_L2" in char.skeleton.bone_names
    assert char.verify_readback()["readback_passed"] is True


def test_golden_armored_character():
    char = UniversalCharacterFabricator.build_golden_armored_character()
    assert char.character_def.character_id == "GOLDEN_ARMORED_CHARACTER"
    assert char.validation_report.is_valid is True
    assert len(char.armor) >= 4
    assert char.verify_readback()["readback_passed"] is True


def test_golden_clothed_character():
    char = UniversalCharacterFabricator.build_golden_clothed_character()
    assert char.character_def.character_id == "GOLDEN_CLOTHED_CHARACTER"
    assert char.validation_report.is_valid is True
    assert len(char.clothing) >= 3
    assert len(char.accessories) >= 2
    assert char.verify_readback()["readback_passed"] is True


def test_golden_facial_character():
    char = UniversalCharacterFabricator.build_golden_facial_character()
    assert char.character_def.character_id == "GOLDEN_FACIAL_CHARACTER"
    assert char.validation_report.is_valid is True
    assert len(char.morphs.morphs) >= 6
    assert char.verify_readback()["readback_passed"] is True


# --- 1 END_TO_END CHARACTER TEST (Section 173) ---

def test_end_to_end_character_pipeline():
    """
    Executes the complete end-to-end pipeline specified in Section 173:
    CHARACTER DEFINITION -> BODY PROPORTIONS -> ANATOMICAL COMPONENTS -> HEAD -> HANDS ->
    FEET -> CLOTHING -> ARMOR -> ACCESSORIES -> SKELETON -> RIG -> SKINNING -> WEIGHT VALIDATION ->
    MORPHS -> FACIAL RIG -> CORRECTIVE DEFORMATION -> POSE TESTS -> COLLISION -> RAGDOLL ->
    LOD -> MATERIAL VALIDATION -> UNREAL EXPORT -> READBACK -> FINAL CHARACTER VALIDATION.
    """
    # 1. CHARACTER DEFINITION & PROPORTIONS
    char_def = CharacterDefinition(
        character_id="E2E_Hero_Character",
        species=CharacterSpecies.HUMAN,
        archetype=CharacterArchetype.HUMAN,
        proportions=BodyProportions(height=185.0, shoulder_width=48.0, chest_depth=30.0),
        seed=999,
    )
    assert char_def.is_valid

    # 2. SKELETON
    skel = UniversalCharacterFabricator.build_humanoid_skeleton("SKEL_E2E_Hero")
    assert not skel.has_duplicate_bones()
    assert not skel.has_cyclic_hierarchy()

    # 3. RIG & IK
    rig = UniversalCharacterFabricator.build_rig(skel, "RIG_E2E_Hero", has_foot_ik=True, has_hand_ik=True)
    assert len(rig.ik_chains) == 4

    # 4. SKINNING & WEIGHTS
    skin = UniversalCharacterFabricator.build_skinning(skel, vertex_count=2000, skinning_id="SKIN_E2E_Hero")
    assert skin.is_normalized()

    # 5. MORPHS & FACIAL RIG
    morphs = UniversalCharacterFabricator.build_morph_system(2000, "MORPH_E2E_Hero", has_facial=True)

    # 6. DEFORMATION & CORRECTIVES
    deform = UniversalCharacterFabricator.build_deformation_profile("DEF_E2E_Hero")

    # 7. CLOTHING, ARMOR, ACCESSORIES
    clothing = [ClothingDefinition("CLOTH_E2E_Pants", ClothingType.PANTS)]
    armor = [ArmorDefinition("ARM_E2E_Chest", ArmorComponentType.CHEST, clearance=1.0)]
    accessories = [AccessoryDefinition("ACC_E2E_Belt", AccessoryType.BELT)]

    # 8. COLLISION & RAGDOLL
    col = UniversalCharacterFabricator.build_collision(skel, "COL_E2E_Hero")

    # 9. LOD
    lod = CharacterLODChain(lod_count=4)

    # 10. RETARGET
    retarget = UniversalCharacterFabricator.build_retarget_profile(skel.skeleton_id, "SKEL_Target_UE5")

    # 11. FABRICATE & UNREAL EXPORT
    package = UniversalCharacterFabricator.fabricate(
        character_def=char_def,
        skeleton=skel,
        rig=rig,
        skinning=skin,
        deformation=deform,
        morphs=morphs,
        clothing=clothing,
        armor=armor,
        accessories=accessories,
        collision=col,
        lod_chain=lod,
        retarget=retarget,
        vertex_count=2000,
        triangle_count=4000,
    )

    # 12. READBACK
    readback = package.verify_readback()
    assert readback["readback_passed"] is True
    assert readback["bone_count"] == len(skel.bones)
    assert readback["vertex_count"] == 2000
    assert readback["triangle_count"] == 4000

    # 13. FINAL CHARACTER VALIDATION
    assert package.validation_report.is_valid is True
    assert package.validation_report.review_status == "PASSED"
    assert package.validation_report.quality_score.aggregate_score == 1.0
    assert len(package.canonical_hash) == 64
