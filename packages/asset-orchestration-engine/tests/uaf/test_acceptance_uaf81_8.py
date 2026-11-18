"""
UAF-81.8 Acceptance Tests (Sections 110, 132, 133).
Verifies:
- Section 110: Golden Asset Acceptance Test (Full end-to-end production-ready packaging of
  render geometry, material slots, collision, sockets, pivot, LODs, and Nanite policy).
- Section 133: Non-Negotiable Principle Test (Missing collision or unassigned material slots
  strictly aborts publish, executes rollback, and flags MANUAL_REVIEW_REQUIRED).
"""

from uaf.assembly.spatial.pivot import PivotType, OriginPolicy, PivotDefinition
from uaf.assembly.spatial.socket import SocketType, RuntimeSocketDefinition
from uaf.assembly.optimization.lod_policy import NanitePolicy, LODChain
from uaf.assembly.graph.assembly_graph import AssetAssemblyGraph, AssetLifecycleState
from uaf.assembly.transaction.transactional_builder import TransactionalAssetBuilder
from uaf.assembly.validation.runtime_validator import RuntimeAssetValidator
from uaf.assembly.package.runtime_package import RuntimeAssetPackage


def test_golden_asset_acceptance_section_110():
    """
    Acceptance Test Section 110:
    Golden Asset end-to-end production readiness:
    - Normalizes Pivot and Origin Policy
    - Assembles Render Geometry, Material Slots, Collision Shapes, and Gameplay Sockets
    - Generates 4-level LOD chain with Nanite policy
    - Transactional validation passes with quality_score >= 0.85
    - State advances to PUBLISHED and packages into RuntimeAssetPackage
    """
    asset_id = "SM_Golden_TacticalTurret"

    # 1. Setup Pivot & Sockets
    pivot = PivotDefinition(
        pivot_type=PivotType.BOTTOM,
        position=[0.0, 0.0, 0.0],
        origin_policy=OriginPolicy.BASE,
    )
    socket_muzzle = RuntimeSocketDefinition(
        socket_id="Socket_Muzzle_Flash",
        parent_attachment="Turret_Barrel",
        position=[0.0, 1.2, 0.4],
        socket_type=SocketType.MUZZLE,
    )

    # 2. Execute Transactional Build
    builder = TransactionalAssetBuilder(asset_id=asset_id, is_static=True)
    builder.prepare(
        render_components=["SM_Turret_Base", "SM_Turret_Barrel"],
        material_slots={0: "M_TurretMetal", 1: "M_TurretSensors"},
        collision_shapes=["UCX_Turret_Base", "UCX_Turret_Barrel"],
        pivot=pivot,
        sockets=[socket_muzzle],
        base_triangles=8000,
    )

    # 3. Validate Production Readiness
    val_report = builder.validate()
    assert val_report.is_valid is True
    assert val_report.review_status == "PASSED"
    assert val_report.quality_score.aggregate_score >= 0.85

    # 4. Commit to PUBLISHED state (Section 124)
    committed = builder.commit()
    assert committed is True
    assert builder.graph.lifecycle_state == AssetLifecycleState.PUBLISHED

    # 5. Export to RuntimeAssetPackage
    pkg = RuntimeAssetPackage(
        asset_id=asset_id,
        graph=builder.graph,
        pivot=pivot,
        sockets=[socket_muzzle],
        lod_chain=builder.lod_chain,
        nanite_policy=NanitePolicy.AUTO,
        quality_report=val_report,
    )

    assert len(pkg.build_hash) == 64
    pkg_dict = pkg.to_dict()
    assert pkg_dict["asset_id"] == "SM_Golden_TacticalTurret"
    assert pkg_dict["graph"]["lifecycle_state"] == "PUBLISHED"
    assert len(pkg_dict["lod_chain"]["lods"]) == 4
    assert pkg_dict["quality_report"]["review_status"] == "PASSED"


def test_non_negotiable_principle_section_133():
    """
    Acceptance Test Section 133:
    Non-negotiable principle:
    An asset is NOT production-ready if collision is missing or socket scale is non-positive.
    Transactional builder must refuse commit, rollback state, and report MANUAL_REVIEW_REQUIRED.
    """
    builder = TransactionalAssetBuilder(asset_id="SM_Defective_Pillar", is_static=True)
    bad_socket = RuntimeSocketDefinition(
        socket_id="Socket_Bad",
        parent_attachment="root",
        scale=[-1.0, 1.0, 1.0],  # VIOLATION: Non-positive scale
    )

    # Missing collision for static mesh + defective socket
    builder.prepare(
        render_components=["SM_Pillar"],
        material_slots={0: "M_Stone"},
        collision_shapes=[],  # VIOLATION: Static mesh lacks collision
        sockets=[bad_socket],
    )

    val_report = builder.validate()
    assert val_report.is_valid is False
    assert val_report.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("lacks physics collision" in iss for iss in val_report.issues)
    assert any("non-positive scale" in iss for iss in val_report.issues)

    # Attempt commit -> MUST fail and trigger rollback
    committed = builder.commit()
    assert committed is False
    assert builder.graph.lifecycle_state == AssetLifecycleState.REJECTED
