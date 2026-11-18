"""
Tests for World Assembly Graph, Rooms, Multi-Floor Buildings, Gameplay Entities, and Navigation.
UAF-81.6 Sections 14, 15, 16, 21, 23, 57, 60, 80.
"""

from uaf.world.assembly.assembly_graph import AssemblyGraph
from uaf.world.assembly.room import RoomType, RoomDefinition
from uaf.world.assembly.building import BuildingDefinition
from uaf.world.gameplay.spatial_gameplay import CoverType, CoverDefinition, SpawnPoint, ObjectiveDefinition
from uaf.world.gameplay.navigation import NavigationMeshMetadata
from uaf.world.partition.world_partition import DataLayer, WorldPartitionCell, HLODMetadata


def test_assembly_graph_and_overlap_detection():
    graph = AssemblyGraph()
    n1 = graph.add_node("inst_floor_01", "Mod_Floor_2x2", [0.0, 0.0, 0.0])
    n2 = graph.add_node("inst_floor_02", "Mod_Floor_2x2", [2.0, 0.0, 0.0])

    graph.connect("inst_floor_01", "conn_east", "inst_floor_02", "conn_west")
    assert graph.node_count == 2
    assert "conn_east" in n1.connected_edges
    assert n1.connected_edges["conn_east"] == ("inst_floor_02", "conn_west")

    # No overlap
    assert len(graph.check_overlaps()) == 0

    # Add coincident overlapping node
    graph.add_node("inst_floor_overlap", "Mod_Floor_2x2", [0.0, 0.0, 0.0])
    overlaps = graph.check_overlaps()
    assert len(overlaps) == 1
    assert ("inst_floor_01", "inst_floor_overlap") in overlaps or ("inst_floor_overlap", "inst_floor_01") in overlaps


def test_multi_floor_building_hierarchy():
    r1 = RoomDefinition("room_ground_01", RoomType.HALL, center_position=[5.0, 5.0, 1.5])
    r2 = RoomDefinition("room_upper_01", RoomType.OFFICE, center_position=[5.0, 5.0, 4.5])

    bld = BuildingDefinition(
        building_id="bld_headquarters",
        footprint=[20.0, 20.0],
        floors_count=2,
        floor_height_meters=3.0,
        rooms=[r1, r2],
        stair_instances=["inst_stair_01"],
    )

    assert bld.total_height_meters == 6.0
    floor_0_rooms = bld.get_rooms_on_floor(0)
    floor_1_rooms = bld.get_rooms_on_floor(1)
    assert len(floor_0_rooms) == 1
    assert floor_0_rooms[0].room_id == "room_ground_01"
    assert len(floor_1_rooms) == 1
    assert floor_1_rooms[0].room_id == "room_upper_01"


def test_navigation_bfs_path_guarantee():
    nav = NavigationMeshMetadata()
    nav.add_waypoint("wp_spawn", [0.0, 0.0, 0.0])
    nav.add_waypoint("wp_corridor", [10.0, 0.0, 0.0])
    nav.add_waypoint("wp_objective", [20.0, 0.0, 0.0])
    nav.add_waypoint("wp_isolated", [50.0, 50.0, 0.0])

    nav.add_edge("wp_spawn", "wp_corridor")
    nav.add_edge("wp_corridor", "wp_objective")

    # Path from spawn to objective exists
    assert nav.has_path("wp_spawn", "wp_objective") is True
    # Path to isolated room does not exist
    assert nav.has_path("wp_spawn", "wp_isolated") is False


def test_spatial_gameplay_and_partition_cells():
    spawn = SpawnPoint("sp_01", team="PLAYER", position=[0.0, 0.0, 0.0])
    cover = CoverDefinition("cov_01", CoverType.LOW, position=[5.0, 2.0, 0.0], height_meters=1.1)
    obj = ObjectiveDefinition("obj_01", "EXTRACT", position=[20.0, 0.0, 0.0])

    assert spawn.is_safe is True
    assert cover.cover_type == CoverType.LOW

    cell = WorldPartitionCell("cell_0_0", min_point=[0.0, 0.0, 0.0], max_point=[32.0, 32.0, 30.0], actor_instance_ids=["inst_floor_01"])
    assert cell.is_spatially_loaded is True

    hlod = HLODMetadata("hlod_cluster_01", cell_ids=["cell_0_0"], draw_distance_meters=200.0)
    assert hlod.draw_distance_meters == 200.0
