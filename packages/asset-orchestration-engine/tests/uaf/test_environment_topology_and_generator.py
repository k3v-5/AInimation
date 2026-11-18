"""
Tests for Facility Graph, Environment Fabricator, Validation, and Package.
UAF-81.12 Sections 22, 27, 174, 201, 202.
"""

from uaf.environment.topology.facility_graph import (
    RoomType,
    RoomNode,
    BuildingFacilityGraph,
)
from uaf.environment.generator.environment_fabricator import ProceduralEnvironmentFabricator
from uaf.environment.validation.environment_validator import EnvironmentValidator
from uaf.environment.spatial.grid import GridProfile
from uaf.environment.package.environment_package import EnvironmentPackage


def test_building_facility_graph_reachability_bfs():
    graph = BuildingFacilityGraph("Facility_Alpha")
    graph.add_room(RoomNode("R_Entry", RoomType.HALL))
    graph.add_room(RoomNode("R_Lab", RoomType.LAB))
    graph.add_room(RoomNode("R_Storage", RoomType.STORAGE))

    # Not fully connected initially
    assert graph.is_fully_connected() is False

    # Connect them into a spanning tree
    graph.connect_rooms("R_Entry", "R_Lab")
    graph.connect_rooms("R_Lab", "R_Storage")
    assert graph.is_fully_connected() is True


def test_environment_fabricator_canonical_archetypes():
    # 1. Modular room
    g_room, p_room = ProceduralEnvironmentFabricator.build_modular_room("Env_Room")
    assert len(g_room.rooms) == 1

    # 2. Multi-room
    g_multi, p_multi = ProceduralEnvironmentFabricator.build_multi_room_building("Env_Multi")
    assert len(g_multi.rooms) == 3
    assert g_multi.is_fully_connected() is True

    # 3. Multi-floor
    g_fac, p_fac = ProceduralEnvironmentFabricator.build_multi_floor_facility("Env_Fac")
    assert g_fac.floors_count == 3
    assert len(g_fac.vertical_connections) == 2

    # 4. Arena
    g_arena, p_arena = ProceduralEnvironmentFabricator.build_combat_arena("Env_Arena")
    assert "arena_center" in g_arena.rooms

    # 5. Outdoor
    g_out, p_out = ProceduralEnvironmentFabricator.build_outdoor_environment("Env_Outdoor")
    assert any(p.module_type == "TERRAIN" for p in p_out)

    # 6. Hybrid
    g_hyb, p_hyb = ProceduralEnvironmentFabricator.build_hybrid_environment("Env_Hybrid")
    assert g_hyb.floors_count == 2


def test_environment_package_validation_and_serialization():
    graph, pieces = ProceduralEnvironmentFabricator.build_multi_floor_facility("Env_TechFacility")
    grid = GridProfile()

    report = EnvironmentValidator.validate_environment(graph, pieces, grid)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.80

    pkg = EnvironmentPackage(
        asset_id="Env_TechFacility_Package",
        environment_type="MULTI_FLOOR_FACILITY",
        facility_graph=graph,
        grid_profile=grid,
        pieces=pieces,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["environment_type"] == "MULTI_FLOOR_FACILITY"
    assert data["facility_graph"]["floors_count"] == 3
