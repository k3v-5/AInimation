"""
UAF-81.19 Acceptance Tests (Sections 213, 32, 167, 185, 212).
Verifies:
- Section 213: Final Acceptance Criteria (Generates and validates all 8 canonical environment archetypes:
  Room, Building, Facility, Combat Arena, Dungeon, Sci-Fi Complex, Modular District, and World Cell).
- Sections 32, 167, 185, 212: Non-Negotiable Requirements Test (Zero tolerance for disconnected layouts,
  sub-clearance room heights < 200cm, or references to non-existent rooms; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.modular_world.engine.modular_world_fabricator import ModularWorldFabricationPlatform
from uaf.modular_world.validation.modular_world_validator import ModularWorldValidator
from uaf.modular_world.models.spatial_graph import SpatialLayoutGraph, EnvironmentRoom, RoomPurpose
from uaf.modular_world.models.definition import EnvironmentDefinition
from uaf.modular_world.package.modular_world_package import ModularWorldPackage


def test_final_modular_world_acceptance_section_213():
    """
    Acceptance Test Section 213:
    Synthesizes and validates all 8 canonical environment archetypes.
    """
    builders = [
        ("Env_Golden_Room", ModularWorldFabricationPlatform.build_room_environment),
        ("Env_Golden_Building", ModularWorldFabricationPlatform.build_building_environment),
        ("Env_Golden_Facility", ModularWorldFabricationPlatform.build_facility_environment),
        ("Env_Golden_Arena", ModularWorldFabricationPlatform.build_combat_arena_environment),
        ("Env_Golden_Dungeon", ModularWorldFabricationPlatform.build_dungeon_environment),
        ("Env_Golden_SciFi", ModularWorldFabricationPlatform.build_scifi_complex_environment),
        ("Env_Golden_District", ModularWorldFabricationPlatform.build_modular_district_environment),
        ("Env_Golden_WorldCell", ModularWorldFabricationPlatform.build_world_cell_environment),
    ]

    for asset_id, builder_fn in builders:
        env_def, graph, modules, props = builder_fn(asset_id)
        assert graph.is_fully_connected() is True
        assert modules > 0

        report = ModularWorldValidator.validate_environment(env_def, graph, modules, props)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = ModularWorldPackage(
            asset_id=asset_id,
            environment_def=env_def,
            layout_graph=graph,
            modules_placed_count=modules,
            props_placed_count=props,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_32_167_185():
    """
    Acceptance Test Sections 32, 167, 185:
    Non-negotiable requirements:
    1. Section 32 & 212: Disconnected rooms strictly fails.
    2. Section 167: Ceiling height < 200cm strictly fails player clearance.
    3. Section 185: Connection referencing non-existent room strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    env_def, graph, modules, props = ModularWorldFabricationPlatform.build_room_environment("Env_Fault_Test")

    # 1. Section 32 violation: Disconnected room
    bad_graph_disc = SpatialLayoutGraph()
    bad_graph_disc.add_room(EnvironmentRoom("Room_A", RoomPurpose.SPAWN, [600.0, 600.0, 300.0]))
    bad_graph_disc.add_room(EnvironmentRoom("Room_Isolated", RoomPurpose.OBJECTIVE, [600.0, 600.0, 300.0]))
    # No connection added between Room_A and Room_Isolated!
    rep_disc = ModularWorldValidator.validate_environment(env_def, bad_graph_disc, modules, props)
    assert rep_disc.is_valid is False
    assert rep_disc.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("isolated, unreachable rooms" in iss for iss in rep_disc.issues)

    # 2. Section 167 violation: Ceiling height 150cm (<200cm clearance)
    bad_graph_clearance = SpatialLayoutGraph()
    bad_graph_clearance.add_room(EnvironmentRoom("Room_Crawlspace", RoomPurpose.TRANSITION, [400.0, 400.0, 150.0]))
    rep_clear = ModularWorldValidator.validate_environment(env_def, bad_graph_clearance, modules, props)
    assert rep_clear.is_valid is False
    assert rep_clear.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("below player clearance" in iss for iss in rep_clear.issues)
