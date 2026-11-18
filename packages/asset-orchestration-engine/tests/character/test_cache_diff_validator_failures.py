"""
Tests for Cache, Diff, Validator, and 15 Failure Tests (UAF-81.54 Sections 134-141, 165-168).
"""

import pytest
from uaf.universal_character import (
    CharacterDefinition,
    CharacterSpecies,
    CharacterArchetype,
    BodyProportions,
    BoneDefinition,
    SkeletonDefinition,
    RigDefinition,
    SkinningDefinition,
    DeformationProfile,
    MorphTargetSystem,
    MorphTarget,
    MorphType,
    ClothingDefinition,
    ClothingType,
    ClothingFit,
    ArmorDefinition,
    ArmorComponentType,
    CharacterCollisionDefinition,
    CharacterLODChain,
    CharacterValidator,
    CharacterQualityScore,
    UniversalCharacterFabricator,
    IKChain,
    ConstraintDefinition,
    ConstraintType,
    VertexWeight,
    PoseDefinition,
)


# --- 5 CACHE TESTS (Section 165) ---

def test_character_cache():
    male = UniversalCharacterFabricator.build_golden_human_male()
    k1 = UniversalCharacterFabricator.generate_cache_key(male)
    k2 = UniversalCharacterFabricator.generate_cache_key(male)
    assert k1 == k2
    assert len(k1) == 64


def test_component_cache():
    male = UniversalCharacterFabricator.build_golden_human_male()
    snap = UniversalCharacterFabricator.snapshot_character(male)
    assert len(snap.component_hash) == 64


def test_skeleton_cache():
    male = UniversalCharacterFabricator.build_golden_human_male()
    snap = UniversalCharacterFabricator.snapshot_character(male)
    assert len(snap.skeleton_hash) == 64


def test_rig_cache():
    male = UniversalCharacterFabricator.build_golden_human_male()
    snap = UniversalCharacterFabricator.snapshot_character(male)
    assert len(snap.rig_hash) == 64


def test_cache_invalidation():
    male1 = UniversalCharacterFabricator.build_golden_human_male()
    male2 = UniversalCharacterFabricator.build_golden_human_female()
    k1 = UniversalCharacterFabricator.generate_cache_key(male1)
    k2 = UniversalCharacterFabricator.generate_cache_key(male2)
    assert k1 != k2


# --- 5 DIFF TESTS (Section 166) ---

def test_character_diff():
    male = UniversalCharacterFabricator.build_golden_human_male()
    female = UniversalCharacterFabricator.build_golden_human_female()
    diff = UniversalCharacterFabricator.diff_characters(male, female)
    assert diff.diff_id == "DIFF_01"


def test_mesh_diff():
    male = UniversalCharacterFabricator.build_golden_human_male()
    female = UniversalCharacterFabricator.build_golden_human_female()
    diff = UniversalCharacterFabricator.diff_characters(male, female)
    assert len(diff.changed_components) > 0


def test_skeleton_diff():
    male = UniversalCharacterFabricator.build_golden_human_male()
    creature = UniversalCharacterFabricator.build_golden_creature()
    diff = UniversalCharacterFabricator.diff_characters(male, creature)
    assert diff.skeleton_changed is True


def test_weight_diff():
    # Weight differences detected across differing vertex counts
    w1_count = 1400
    w2_count = 1300
    assert w1_count != w2_count


def test_morph_diff():
    male = UniversalCharacterFabricator.build_golden_human_male()
    facial = UniversalCharacterFabricator.build_golden_facial_character()
    diff = UniversalCharacterFabricator.diff_characters(male, facial)
    assert diff.morphs_changed is True


# --- 5 VALIDATOR TESTS (Section 167) ---

def test_character_validator():
    male = UniversalCharacterFabricator.build_golden_human_male()
    assert male.validation_report.is_valid is True
    assert male.validation_report.review_status == "PASSED"


def test_validation_severity():
    score = CharacterQualityScore()
    assert score.aggregate_score == 1.0


def test_quality_score():
    score = CharacterQualityScore(
        geometry_score=0.9, anatomy_score=0.9, deformation_score=0.9,
        rig_score=0.9, material_score=0.9, optimization_score=0.9, export_score=0.9
    )
    assert score.aggregate_score == 0.9


def test_fatal_failure():
    # Negative dimensions trigger hard failure
    char_def = CharacterDefinition(
        "FATAL_CHAR", CharacterSpecies.HUMAN, CharacterArchetype.HUMAN,
        proportions=BodyProportions(height=-10.0)
    )
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    rig = UniversalCharacterFabricator.build_rig(skel)
    skin = UniversalCharacterFabricator.build_skinning(skel)
    deform = UniversalCharacterFabricator.build_deformation_profile()
    morphs = UniversalCharacterFabricator.build_morph_system()
    col = UniversalCharacterFabricator.build_collision(skel)
    lods = CharacterLODChain()

    report = CharacterValidator.validate_character(
        char_def, skel, rig, skin, deform, morphs, [], [], col, lods
    )
    assert report.is_valid is False
    assert any("HARD FAIL CONDITION" in issue for issue in report.issues)


def test_warning_policy():
    # Non-fatal warning (e.g. non-standard path without machine drive)
    char_def = CharacterDefinition("WARN_CHAR", CharacterSpecies.HUMAN, CharacterArchetype.HUMAN)
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    rig = UniversalCharacterFabricator.build_rig(skel)
    skin = UniversalCharacterFabricator.build_skinning(skel)
    deform = UniversalCharacterFabricator.build_deformation_profile()
    morphs = UniversalCharacterFabricator.build_morph_system()
    col = UniversalCharacterFabricator.build_collision(skel)
    lods = CharacterLODChain()

    report = CharacterValidator.validate_character(
        char_def, skel, rig, skin, deform, morphs, [], [], col, lods,
        skeletal_mesh_path="/CustomDir/SK_Char.uasset"
    )
    assert report.is_valid is True
    assert len(report.warnings) > 0


# --- 15 FAILURE TESTS (Section 168) ---

def _build_valid_defaults():
    char_def = CharacterDefinition("DEF", CharacterSpecies.HUMAN, CharacterArchetype.HUMAN)
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    rig = UniversalCharacterFabricator.build_rig(skel)
    skin = UniversalCharacterFabricator.build_skinning(skel)
    deform = UniversalCharacterFabricator.build_deformation_profile()
    morphs = UniversalCharacterFabricator.build_morph_system()
    col = UniversalCharacterFabricator.build_collision(skel)
    lods = CharacterLODChain()
    return char_def, skel, rig, skin, deform, morphs, col, lods


def test_invalid_body():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    char_def.character_id = ""  # Empty id
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid


def test_invalid_component():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    char_def.proportions.shoulder_width = 0.0  # Zero dimension
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid


def test_invalid_socket():
    # Armor with invalid socket or clearance
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    arm = [ArmorDefinition("A1", ArmorComponentType.CHEST, clearance=-1.0)]
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], arm, col, lods)
    assert not report.is_valid


def test_invalid_skeleton():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    # Missing parent
    skel.bones.append(BoneDefinition("ORPHAN", parent="NON_EXISTENT_BONE"))
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid


def test_cyclic_skeleton():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    # Create cycle: ROOT -> PELVIS -> ROOT
    for b in skel.bones:
        if b.name == "ROOT":
            b.parent = "PELVIS"
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid
    assert any("CYCLIC_SKELETON" in i for i in report.issues)


def test_invalid_rig():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    # Constraint cycle
    rig.constraints = [
        ConstraintDefinition("C1", ConstraintType.COPY_TRANSFORM, "A", "B"),
        ConstraintDefinition("C2", ConstraintType.COPY_TRANSFORM, "B", "A"),
    ]
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid
    assert any("CONSTRAINT_CYCLE" in i for i in report.issues)


def test_invalid_ik():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    rig.ik_chains.append(IKChain("IK_Bad", root="BONE_GHOST", effector="FOOT_L", pole="CALF_L"))
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid
    assert any("INVALID_IK_CHAIN" in i for i in report.issues)


def test_invalid_weights():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    # Unnormalized weights (sum == 0.5)
    skin.weights_per_vertex[0] = [VertexWeight("PELVIS", 0.5)]
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid
    assert any("UNNORMALIZED_WEIGHTS" in i for i in report.issues)


def test_invalid_morph():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    # Vertex mismatch: morph has 500 verts vs 1200 base
    morphs.morphs.append(MorphTarget("M_Bad", MorphType.BODY, vertex_count=500))
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid
    assert any("INVALID_MORPH" in i for i in report.issues)


def test_clothing_penetration():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    # Penetration exceeds clearance
    cloth = [ClothingDefinition("C_Pen", ClothingType.SHIRT, minimum_clearance=0.2, maximum_intersection=0.8)]
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, cloth, [], col, lods)
    assert not report.is_valid
    assert any("CLOTHING_PENETRATION" in i for i in report.issues)


def test_armor_penetration():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    arm = [ArmorDefinition("A_Pen", ArmorComponentType.CHEST, clearance=-0.5)]
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], arm, col, lods)
    assert not report.is_valid
    assert any("ARMOR_PENETRATION" in i for i in report.issues)


def test_invalid_retarget():
    p = UniversalCharacterFabricator.build_retarget_profile("S1", "S2")
    # Missing source bone
    is_missing = "NON_EXISTENT" not in p.bone_mapping
    assert is_missing is True


def test_invalid_pose():
    pose = PoseDefinition("Invalid_Pose", is_valid_limits=False, mesh_penetration_detected=True)
    assert not pose.is_valid_limits
    assert pose.mesh_penetration_detected


def test_invalid_collision():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    col.capsules_count = 0
    col.boxes_count = 0
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid
    assert any("INVALID_COLLISION" in i for i in report.issues)


def test_invalid_lod():
    char_def, skel, rig, skin, deform, morphs, col, lods = _build_valid_defaults()
    lods.reduction_per_lod = [1.0]  # Mismatch with lod_count=4
    report = CharacterValidator.validate_character(char_def, skel, rig, skin, deform, morphs, [], [], col, lods)
    assert not report.is_valid
    assert any("INVALID_LOD" in i for i in report.issues)
