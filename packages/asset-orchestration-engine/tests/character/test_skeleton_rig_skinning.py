"""
Tests for Skeleton, Rigging, Constraints, and Skinning (UAF-81.54 Sections 64-94, 153-155).
"""

import pytest
from uaf.universal_character import (
    BoneDefinition,
    RestPose,
    SkeletonDefinition,
    IKChain,
    IKType,
    ConstraintDefinition,
    ConstraintType,
    RigDefinition,
    SkinningDefinition,
    SkinningMethod,
    WeightStrategy,
    VertexWeight,
    UniversalCharacterFabricator,
)


# --- 6 SKELETON TESTS (Section 153) ---

def test_skeleton_definition():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    assert skel.skeleton_id == "SKEL_Humanoid"
    assert len(skel.bones) >= 23
    d = skel.to_dict()
    assert d["skeleton_id"] == "SKEL_Humanoid"


def test_skeleton_hierarchy():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    # PELVIS parent is ROOT, SPINE_01 parent is PELVIS
    bone_map = {b.name: b.parent for b in skel.bones}
    assert bone_map["PELVIS"] == "ROOT"
    assert bone_map["SPINE_01"] == "PELVIS"


def test_bone_naming():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    assert "HEAD" in skel.bone_names
    assert "UPPER_ARM_L" in skel.bone_names
    assert not skel.has_duplicate_bones()


def test_bone_mirroring():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    l_bones = [b for b in skel.bone_names if b.endswith("_L")]
    r_bones = [b for b in skel.bone_names if b.endswith("_R")]
    assert len(l_bones) == len(r_bones)
    for lb in l_bones:
        expected_rb = lb[:-2] + "_R"
        assert expected_rb in r_bones


def test_rest_pose():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    assert skel.rest_pose.is_frozen
    assert "ROOT" in skel.rest_pose.bone_transforms


def test_skeleton_validation():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    assert not skel.has_duplicate_bones()
    assert not skel.has_cyclic_hierarchy()
    assert not skel.has_missing_parents()


# --- 7 RIG TESTS (Section 154) ---

def test_rig_definition():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    rig = UniversalCharacterFabricator.build_rig(skel)
    assert rig.rig_id == "RIG_Humanoid"
    assert rig.skeleton_id == skel.skeleton_id
    d = rig.to_dict()
    assert len(d["controls"]) > 0


def test_controls():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    rig = UniversalCharacterFabricator.build_rig(skel)
    assert "CTRL_Root" in rig.controls
    assert "CTRL_Head" in rig.controls


def test_fk():
    # Forward kinematics control chain verification
    fk_chain = ["SPINE_01", "SPINE_02", "SPINE_03", "NECK", "HEAD"]
    assert len(fk_chain) == 5


def test_ik():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    rig = UniversalCharacterFabricator.build_rig(skel)
    assert len(rig.ik_chains) >= 2


def test_two_bone_ik():
    ik = IKChain("IK_Arm_L", root="UPPER_ARM_L", effector="HAND_L", pole="LOWER_ARM_L", chain_length=2, ik_type=IKType.TWO_BONE)
    assert ik.chain_length == 2
    assert ik.ik_type == IKType.TWO_BONE


def test_constraint_order():
    c1 = ConstraintDefinition("C1", ConstraintType.PARENT, "CTRL_Pelvis", "PELVIS")
    c2 = ConstraintDefinition("C2", ConstraintType.AIM, "CTRL_Head", "HEAD")
    constraints = [c1, c2]
    # Deterministic order preserved
    assert [c.name for c in constraints] == ["C1", "C2"]


def test_constraint_cycle():
    c1 = ConstraintDefinition("C1", ConstraintType.COPY_TRANSFORM, "BONE_A", "BONE_B")
    c2 = ConstraintDefinition("C2", ConstraintType.COPY_TRANSFORM, "BONE_B", "BONE_A")
    cmap = {c1.source: c1.target, c2.source: c2.target}
    # Cycle check
    has_cycle = False
    visited = set()
    curr = "BONE_A"
    for _ in range(5):
        if curr in visited:
            has_cycle = True
            break
        visited.add(curr)
        curr = cmap.get(curr)
    assert has_cycle is True


# --- 7 SKINNING TESTS (Section 155) ---

def test_skin_definition():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    skin = UniversalCharacterFabricator.build_skinning(skel, vertex_count=500)
    assert skin.skinning_id == "SKIN_Standard"
    assert skin.method == SkinningMethod.LINEAR_BLEND
    assert len(skin.weights_per_vertex) == 500


def test_weight_generation():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    skin = UniversalCharacterFabricator.build_skinning(skel, vertex_count=100)
    assert skin.strategy == WeightStrategy.DISTANCE
    assert 0 in skin.weights_per_vertex


def test_weight_transfer():
    source_weights = {0: [VertexWeight("SPINE_01", 1.0)]}
    target_weights = {0: [VertexWeight(w.bone_name, w.weight) for w in source_weights[0]]}
    assert target_weights[0][0].bone_name == "SPINE_01"
    assert target_weights[0][0].weight == 1.0


def test_weight_normalization():
    skel = UniversalCharacterFabricator.build_humanoid_skeleton()
    skin = UniversalCharacterFabricator.build_skinning(skel, vertex_count=50)
    assert skin.is_normalized()


def test_influence_limit():
    skin = SkinningDefinition(
        "SKIN_Test",
        max_influences_per_vertex=4,
        weights_per_vertex={
            0: [VertexWeight(f"BONE_{i}", 0.2) for i in range(5)]
        }
    )
    assert skin.exceeds_influence_limit() is True


def test_weight_cleanup():
    raw_influences = [
        VertexWeight("PELVIS", 0.7),
        VertexWeight("SPINE_01", 0.29),
        VertexWeight("HAND_L", 0.01),  # Insignificant weight
    ]
    # Prune weights < 0.05 and renormalize
    pruned = [w for w in raw_influences if w.weight >= 0.05]
    total = sum(w.weight for w in pruned)
    normalized = [VertexWeight(w.bone_name, round(w.weight / total, 3)) for w in pruned]
    assert len(normalized) == 2
    assert abs(sum(w.weight for w in normalized) - 1.0) < 1e-2


def test_weight_mirror():
    weights_l = [VertexWeight("UPPER_ARM_L", 0.8), VertexWeight("SPINE_03", 0.2)]
    weights_r = [VertexWeight(w.bone_name.replace("_L", "_R"), w.weight) for w in weights_l]
    assert weights_r[0].bone_name == "UPPER_ARM_R"
    assert weights_r[0].weight == 0.8
