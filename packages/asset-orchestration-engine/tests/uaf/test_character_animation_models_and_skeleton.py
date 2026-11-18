"""
Tests for Character Animation Models, Skeleton, IK, and Skinning.
UAF-81.17 Sections 8, 9, 14, 15, 25, 35, 39.
"""

from uaf.character_animation.models.skeleton import BoneRole, BoneNode, SkeletonHierarchy
from uaf.character_animation.models.ik import IKSolverType, IKChain
from uaf.character_animation.models.skinning import SkinningMethod, SkinningWeightData


def test_skeleton_hierarchy_and_cycle_detection():
    skel = SkeletonHierarchy.create_standard_humanoid_skeleton("SK_Test_Human")
    assert skel.root_bone == "root"
    assert "pelvis" in skel.bones
    assert "head" in skel.bones
    assert skel.has_cycles() is False
    assert len(skel.skeleton_hash) == 64

    # Test cycle detection
    skel.bones["root"].parent = "pelvis"  # Creates cycle: root -> pelvis -> root
    assert skel.has_cycles() is True


def test_ik_chains_and_skinning():
    ik_chains = IKChain.create_humanoid_ik_set()
    assert len(ik_chains) == 5
    assert any(ik.chain_type == "LOOK_AT" for ik in ik_chains)

    skin = SkinningWeightData(
        vertex_count=8000,
        max_influences_per_vertex=4,
        skinning_method=SkinningMethod.DUAL_QUATERNION,
        weights_sum_normalized=True,
    )
    assert skin.weights_sum_normalized is True
    assert skin.to_dict()["skinning_method"] == "DUAL_QUATERNION"
