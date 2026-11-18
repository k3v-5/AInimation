"""
UAF-81.28 Acceptance Tests (Sections 60 to 77, 5, 114, 119, 124).
Verifies:
- Sections 60 to 77: Final Acceptance Criteria (Generates and validates all 5 canonical scenarios:
  Interior Facility, Urban Block, Industrial Complex, Combat Arena, Dungeon Complex).
- Sections 5, 114, 119, 124: Non-Negotiable Requirements Test (Zero tolerance for invalid grid scaling,
  broken critical paths, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.world_building.engine.building_fabricator import WorldBuildingFabricationPlatform
from uaf.world_building.validation.building_validator import WorldBuildingValidator
from uaf.world_building.models.definition import (
    PlayableWorldDefinition,
    WorldType28,
    ModularBlockDefinition,
    ModularCategory,
    SocketType28,
)
from uaf.world_building.models.graph import BlockoutWorldGraph, BlockoutZoneNode
from uaf.world_building.package.building_package import WorldBuildingPackage


def test_final_world_building_acceptance_sections_60_to_77():
    """
    Acceptance Test Sections 60 to 77:
    Synthesizes and validates all 5 canonical scenarios.
    """
    builders = [
        ("World_Gold_Facility", WorldBuildingFabricationPlatform.build_interior_facility_world),
        ("World_Gold_UrbanBlock", WorldBuildingFabricationPlatform.build_urban_block_world),
        ("World_Gold_Industrial", WorldBuildingFabricationPlatform.build_industrial_complex_world),
        ("World_Gold_CombatArena", WorldBuildingFabricationPlatform.build_combat_arena_world),
        ("World_Gold_Dungeon", WorldBuildingFabricationPlatform.build_dungeon_complex_world),
    ]

    for asset_id, builder_fn in builders:
        w_def, graph, lvl_ref = builder_fn(asset_id)
        assert w_def.is_valid_grid is True
        assert graph.is_fully_connected() is True
        assert graph.is_critical_path_connected() is True

        report = WorldBuildingValidator.validate_world_build(w_def, graph, lvl_ref)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = WorldBuildingPackage(
            asset_id=asset_id,
            world_def=w_def,
            graph=graph,
            level_ref=lvl_ref,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_5_114_119_124():
    """
    Acceptance Test Sections 5, 114, 119, 124:
    Non-negotiable requirements:
    1. Section 5 & 114: Grid size < 100cm strictly fails.
    2. Section 124: Broken critical path strictly fails.
    3. Section 119: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    w_def, graph, lvl_ref = WorldBuildingFabricationPlatform.build_interior_facility_world("World_Fault_Test")

    # 1. Section 5 & 114 violation: Grid size < 100cm
    bad_wdef_grid = PlayableWorldDefinition("World_TinyGrid", WorldType28.FACILITY, grid_size_cm=45.0)
    rep_grid = WorldBuildingValidator.validate_world_build(bad_wdef_grid, graph, lvl_ref)
    assert rep_grid.is_valid is False
    assert rep_grid.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("below minimum 100.0cm threshold" in iss for iss in rep_grid.issues)

    # 2. Section 124 violation: Broken critical path (disconnected critical zone)
    bad_graph = BlockoutWorldGraph()
    bad_graph.add_zone(BlockoutZoneNode("Zone_A", "Alpha Entry", is_critical_path=True))
    bad_graph.add_zone(BlockoutZoneNode("Zone_B_Isolated", "Beta Exit", is_critical_path=True))
    # No connection between Zone_A and Zone_B_Isolated!
    rep_path = WorldBuildingValidator.validate_world_build(w_def, bad_graph, lvl_ref)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Broken critical path" in iss for iss in rep_path.issues)

    # 3. Section 119 violation: Absolute machine path in level reference
    bad_lvl_path = "C:\\UnrealEngine\\Maps\\Levels\\LV_Main.umap"
    rep_lvl = WorldBuildingValidator.validate_world_build(w_def, graph, bad_lvl_path)
    assert rep_lvl.is_valid is False
    assert rep_lvl.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_lvl.issues)
