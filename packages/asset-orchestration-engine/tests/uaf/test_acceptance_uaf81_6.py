"""
UAF-81.6 Acceptance Tests (Sections 109, 120, 121).
Verifies:
- Section 109: Golden Map Acceptance Test (Multi-room multi-floor facility with stairs, doors,
  covers, spawns, objectives, navigation, streaming partition cells, HLOD, and Unreal packaging).
- Section 121: Non-Negotiable Rule Test (Path reachability failure or colliding module overlap
  strictly triggers MANUAL_REVIEW_REQUIRED).
"""

from uaf.world.spatial.world_grid import WorldGrid
from uaf.world.spatial.world_specification import WorldSpecification
from uaf.world.modular.modular_kit import ModularKitDefinition
from uaf.world.assembly.assembly_graph import AssemblyGraph
from uaf.world.assembly.room import RoomType, RoomDefinition
from uaf.world.assembly.building import BuildingDefinition
from uaf.world.gameplay.spatial_gameplay import CoverType, CoverDefinition, SpawnPoint, ObjectiveDefinition
from uaf.world.gameplay.navigation import NavigationMeshMetadata
from uaf.world.partition.world_partition import WorldPartitionCell, HLODMetadata
from uaf.world.validation.world_validator import WorldValidator
from uaf.world.package.world_package import WorldPackage


def test_golden_map_acceptance_section_109():
    """
    Acceptance Test Section 109:
    Golden Map end-to-end level fabrication:
    - Multi-room, 2-floor building with stairs and doors
    - Tactical cover, player spawns, mission objective
    - Navigation mesh with verified critical path
    - Streaming cells and HLOD metadata
    - Quality score >= 0.80 and WorldPackage export
    """
    # 1. World Spec & Kit
    spec = WorldSpecification(
        world_id="golden_sector_alpha",
        seed=9999,
        theme="SCI_FI_FACILITY",
        dimensions=[64.0, 64.0, 20.0],
    )
    kit = ModularKitDefinition.create_standard_scifi_kit()

    # 2. Assembly Graph
    assembly = AssemblyGraph()
    # Floor 0: Spawn room and Corridor
    assembly.add_node("mod_f0_floor_01", "Mod_Floor_2x2", [0.0, 0.0, 0.0])
    assembly.add_node("mod_f0_door_01", "Mod_Door_2x3", [0.0, 2.0, 0.0])
    assembly.add_node("mod_f0_corridor_01", "Mod_Floor_2x2", [0.0, 4.0, 0.0])

    # Stairs to Floor 1
    assembly.add_node("mod_stair_01", "Mod_Stair_2x3", [0.0, 6.0, 0.0])

    # Floor 1: Objective room
    assembly.add_node("mod_f1_floor_01", "Mod_Floor_2x2", [0.0, 8.0, 3.0])

    # 3. Rooms and Building
    r_spawn = RoomDefinition("room_spawn", RoomType.SPAWN_ROOM, center_position=[0.0, 0.0, 1.5], gameplay_role="SPAWN")
    r_obj = RoomDefinition("room_objective", RoomType.OBJECTIVE_ROOM, center_position=[0.0, 8.0, 4.5], gameplay_role="OBJECTIVE")

    building = BuildingDefinition(
        building_id="bld_command_center",
        footprint=[16.0, 16.0],
        floors_count=2,
        floor_height_meters=3.0,
        rooms=[r_spawn, r_obj],
        stair_instances=["mod_stair_01"],
    )

    # 4. Gameplay Entities
    spawn = SpawnPoint("sp_player_01", team="PLAYER", position=[0.0, 0.0, 0.0])
    cover = CoverDefinition("cov_tactical_01", CoverType.LOW, position=[0.0, 4.0, 0.0], height_meters=1.0)
    obj = ObjectiveDefinition("obj_terminal", "EXTRACT", position=[0.0, 8.0, 3.0])

    # 5. Navigation & Critical Path
    nav = NavigationMeshMetadata()
    nav.add_waypoint("wp_spawn", [0.0, 0.0, 0.0])
    nav.add_waypoint("wp_door", [0.0, 2.0, 0.0])
    nav.add_waypoint("wp_stair_base", [0.0, 6.0, 0.0])
    nav.add_waypoint("wp_stair_top", [0.0, 8.0, 3.0])
    nav.add_waypoint("wp_objective", [0.0, 8.0, 3.0])

    nav.add_edge("wp_spawn", "wp_door")
    nav.add_edge("wp_door", "wp_stair_base")
    nav.add_edge("wp_stair_base", "wp_stair_top")
    nav.add_edge("wp_stair_top", "wp_objective")

    # 6. Streaming & HLOD
    cell_f0 = WorldPartitionCell("cell_f0", [0.0, 0.0, 0.0], [32.0, 32.0, 3.0], ["mod_f0_floor_01", "mod_f0_door_01"])
    cell_f1 = WorldPartitionCell("cell_f1", [0.0, 0.0, 3.0], [32.0, 32.0, 6.0], ["mod_f1_floor_01"])
    hlod = HLODMetadata("hlod_building", ["cell_f0", "cell_f1"], draw_distance_meters=200.0)

    # 7. Automated Validation
    val_report = WorldValidator.validate_world(
        assembly=assembly,
        navigation=nav,
        spawns=[spawn],
        objectives=[obj],
        spawn_wp="wp_spawn",
        objective_wp="wp_objective",
        max_actor_budget=5000,
    )
    assert val_report.is_valid is True
    assert val_report.review_status == "PASSED"
    assert val_report.quality_score.aggregate_score >= 0.80

    # 8. Package Level
    package = WorldPackage(
        world_id=spec.world_id,
        specification=spec,
        kit=kit,
        assembly=assembly,
        rooms=[r_spawn, r_obj],
        buildings=[building],
        spawns=[spawn],
        covers=[cover],
        objectives=[obj],
        navigation=nav,
        partition_cells=[cell_f0, cell_f1],
        hlod=hlod,
        validation_report=val_report,
    )

    assert len(package.build_hash) == 64
    pkg_data = package.to_dict()
    assert pkg_data["world_id"] == "golden_sector_alpha"
    assert len(pkg_data["buildings"]) == 1
    assert pkg_data["validation_report"]["review_status"] == "PASSED"


def test_non_negotiable_rule_section_121():
    """
    Acceptance Test Section 121:
    Non-negotiable rule:
    If a required critical path is broken, or modules overlap in collision,
    status must be strictly MANUAL_REVIEW_REQUIRED.
    """
    assembly = AssemblyGraph()
    # Add two coincident colliding modules
    assembly.add_node("inst_a", "Mod_Floor_2x2", [0.0, 0.0, 0.0])
    assembly.add_node("inst_b", "Mod_Floor_2x2", [0.0, 0.0, 0.0])

    nav = NavigationMeshMetadata()
    nav.add_waypoint("wp_spawn", [0.0, 0.0, 0.0])
    nav.add_waypoint("wp_obj", [50.0, 0.0, 0.0])
    # No edge connecting spawn to obj (unreachable!)

    spawn = SpawnPoint("sp_01", position=[0.0, 0.0, 0.0])
    obj = ObjectiveDefinition("obj_01", "CAPTURE", position=[50.0, 0.0, 0.0])

    val = WorldValidator.validate_world(
        assembly=assembly,
        navigation=nav,
        spawns=[spawn],
        objectives=[obj],
        spawn_wp="wp_spawn",
        objective_wp="wp_obj",
    )

    assert val.is_valid is False
    assert val.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("overlap collision" in iss for iss in val.issues)
    assert any("Path guarantee violation" in iss for iss in val.issues)
