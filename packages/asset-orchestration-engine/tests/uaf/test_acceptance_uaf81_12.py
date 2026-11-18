"""
UAF-81.12 Acceptance Tests (Sections 202, 203, 204).
Verifies:
- Section 202: Final Acceptance Criteria (Generates, validates, and packages all 6 canonical environments:
  Modular Room, Multi-Room Building, Multi-Floor Facility, Combat Arena, Outdoor Environment, and Hybrid Environment).
- Sections 203 & 204: Non-Negotiable Requirements Test (Zero tolerance for disconnected spaces, invalid scales,
  or pieces missing physics collision; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.environment.generator.environment_fabricator import ProceduralEnvironmentFabricator
from uaf.environment.validation.environment_validator import EnvironmentValidator
from uaf.environment.spatial.grid import GridProfile
from uaf.environment.spatial.piece import ModularPiece
from uaf.environment.topology.facility_graph import BuildingFacilityGraph, RoomNode, RoomType
from uaf.environment.package.environment_package import EnvironmentPackage


def test_final_environment_fabrication_acceptance_section_202():
    """
    Acceptance Test Section 202:
    Deterministically synthesizes all 6 canonical environments:
    1. Modular Room
    2. Multi-Room Building
    3. Multi-Floor Facility
    4. Combat Arena
    5. Outdoor Environment
    6. Hybrid Interior/Exterior Environment
    """
    grid = GridProfile()

    environments = [
        ("Env_Golden_Room", "MODULAR_ROOM", ProceduralEnvironmentFabricator.build_modular_room),
        ("Env_Golden_Building", "MULTI_ROOM_BUILDING", ProceduralEnvironmentFabricator.build_multi_room_building),
        ("Env_Golden_Facility", "MULTI_FLOOR_FACILITY", ProceduralEnvironmentFabricator.build_multi_floor_facility),
        ("Env_Golden_Arena", "COMBAT_ARENA", ProceduralEnvironmentFabricator.build_combat_arena),
        ("Env_Golden_Outdoor", "OUTDOOR_ENVIRONMENT", ProceduralEnvironmentFabricator.build_outdoor_environment),
        ("Env_Golden_Hybrid", "HYBRID_ENVIRONMENT", ProceduralEnvironmentFabricator.build_hybrid_environment),
    ]

    for asset_id, env_type, builder_fn in environments:
        graph, pieces = builder_fn(asset_id)
        report = EnvironmentValidator.validate_environment(graph, pieces, grid)

        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.80

        pkg = EnvironmentPackage(
            asset_id=asset_id,
            environment_type=env_type,
            facility_graph=graph,
            grid_profile=grid,
            pieces=pieces,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_203_204():
    """
    Acceptance Test Sections 203 & 204:
    Non-negotiable requirements:
    1. Section 203: Invalid scale or missing collision shape on modular piece strictly fails.
    2. Section 204: Disconnected rooms (failed BFS reachability) strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    grid = GridProfile()

    # 1. Section 204 violation: Disconnected facility rooms
    disc_graph = BuildingFacilityGraph("Facility_Disconnected")
    disc_graph.add_room(RoomNode("R_A", RoomType.HALL))
    disc_graph.add_room(RoomNode("R_B", RoomType.LAB))  # Isolated room!

    rep_disc = EnvironmentValidator.validate_environment(disc_graph, grid=grid)
    assert rep_disc.is_valid is False
    assert rep_disc.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("disconnected rooms" in iss for iss in rep_disc.issues)

    # 2. Section 203 violation: Piece with missing collision or non-positive dimension
    valid_graph = BuildingFacilityGraph("Facility_Valid")
    valid_graph.add_room(RoomNode("R_Main", RoomType.ARENA))

    flawed_piece = ModularPiece(
        piece_id="P_Defective",
        module_type="WALL",
        dimensions=[-2.0, 0.2, 3.0],  # VIOLATION: Negative scale
        collision_shape="",           # VIOLATION: Missing collision
    )

    rep_piece = EnvironmentValidator.validate_environment(valid_graph, pieces=[flawed_piece], grid=grid)
    assert rep_piece.is_valid is False
    assert rep_piece.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("non-positive dimensions" in iss for iss in rep_piece.issues)
    assert any("lacks collision shape" in iss for iss in rep_piece.issues)
