"""
Tests for Asset Assembly Graph and Transactional Builder with Rollback.
UAF-81.8 Sections 4, 14, 102, 103, 104, 123, 124.
"""

from uaf.assembly.graph.assembly_graph import AssetAssemblyGraph, AssetLifecycleState
from uaf.assembly.transaction.transactional_builder import TransactionalAssetBuilder
from uaf.assembly.spatial.pivot import PivotDefinition
from uaf.assembly.spatial.socket import SocketType, RuntimeSocketDefinition


def test_asset_assembly_graph_serialization_and_hash():
    graph = AssetAssemblyGraph(
        asset_id="Asset_Hero_CombatSuit",
        render_components=["comp_body", "comp_helmet"],
        material_slots={0: "M_BodySkin", 1: "M_HelmetGlass"},
        collision_shapes=["UCX_Body_01"],
        socket_ids=["Socket_Grip_R"],
        lifecycle_state=AssetLifecycleState.GENERATED,
    )
    assert len(graph.graph_hash) == 64
    data = graph.to_dict()
    assert data["asset_id"] == "Asset_Hero_CombatSuit"
    assert data["lifecycle_state"] == "GENERATED"


def test_transactional_builder_commit_success():
    builder = TransactionalAssetBuilder(asset_id="Asset_Prop_Crate")
    builder.prepare(
        render_components=["SM_Crate_LOD0"],
        material_slots={0: "MI_CrateWood"},
        collision_shapes=["UBX_Crate_01"],
        base_triangles=2000,
    )

    report = builder.validate()
    assert report.is_valid is True
    assert report.review_status == "PASSED"

    success = builder.commit()
    assert success is True
    assert builder.is_committed is True
    assert builder.graph.lifecycle_state == AssetLifecycleState.PUBLISHED


def test_transactional_builder_rollback_on_failure():
    builder = TransactionalAssetBuilder(asset_id="Asset_Broken_Prop")
    # Prepare with NO collision shapes and NO material slots for static mesh (causes failure)
    builder.prepare(
        render_components=["SM_Broken_01"],
        material_slots={},
        collision_shapes=[],
    )

    report = builder.validate()
    assert report.is_valid is False
    assert report.review_status == "MANUAL_REVIEW_REQUIRED"

    success = builder.commit()
    assert success is False
    assert builder.is_committed is False
    assert builder.graph.lifecycle_state == AssetLifecycleState.REJECTED
