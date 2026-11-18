"""
UAF-81.24 Acceptance Tests (Sections 149, 14, 141, 148, 173).
Verifies:
- Section 149: Final Acceptance Criteria (Generates and validates all 9 canonical reference worlds:
  Small Interior, Modular Building, Industrial Complex, Outdoor Area, Forest, Desert,
  Urban Block, Multi-Level, Combat Arena).
- Sections 14, 141, 148, 173: Non-Negotiable Requirements Test (Zero tolerance for invalid bounds,
  disconnected layouts, broken critical paths, or absolute paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.world_architecture.engine.architecture_fabricator import WorldArchitectureFabricationPlatform
from uaf.world_architecture.validation.architecture_validator import WorldArchitectureValidator
from uaf.world_architecture.models.definition import WorldDefinition24, WorldBoundaryBounds, BiomeType24
from uaf.world_architecture.models.graph import ArchitecturalWorldGraph, ArchitecturalRoomNode, ArchitecturalZoneType
from uaf.world_architecture.package.architecture_package import WorldArchitecturePackage


def test_final_world_architecture_acceptance_section_149():
    """
    Acceptance Test Section 149:
    Synthesizes and validates all 9 reference worlds.
    """
    builders = [
        ("World_Gold_SmallInterior", WorldArchitectureFabricationPlatform.build_small_interior_world),
        ("World_Gold_ModularBuilding", WorldArchitectureFabricationPlatform.build_modular_building_world),
        ("World_Gold_Industrial", WorldArchitectureFabricationPlatform.build_industrial_complex_world),
        ("World_Gold_OutdoorArea", WorldArchitectureFabricationPlatform.build_outdoor_area_world),
        ("World_Gold_Forest", WorldArchitectureFabricationPlatform.build_forest_world),
        ("World_Gold_Desert", WorldArchitectureFabricationPlatform.build_desert_world),
        ("World_Gold_UrbanBlock", WorldArchitectureFabricationPlatform.build_urban_block_world),
        ("World_Gold_MultiLevel", WorldArchitectureFabricationPlatform.build_multi_level_world),
        ("World_Gold_CombatArena", WorldArchitectureFabricationPlatform.build_combat_arena_world),
    ]

    for asset_id, builder_fn in builders:
        w_def, graph, grid_cells, landmarks = builder_fn(asset_id)
        assert w_def.bounds.is_valid is True
        assert graph.is_fully_connected() is True
        assert graph.is_critical_path_valid() is True

        report = WorldArchitectureValidator.validate_world(w_def, graph, landmarks)
        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = WorldArchitecturePackage(
            asset_id=asset_id,
            world_def=w_def,
            graph=graph,
            grid_cells=grid_cells,
            landmarks=landmarks,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_14_141_148_173():
    """
    Acceptance Test Sections 14, 141, 148, 173:
    Non-negotiable requirements:
    1. Section 14: World boundary bounds with max <= min strictly fails.
    2. Section 148 & 173: Broken critical path strictly fails.
    3. Section 141: Absolute machine-dependent reference paths strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    w_def, graph, grid_cells, landmarks = WorldArchitectureFabricationPlatform.build_small_interior_world("World_Fault_Test")

    # 1. Section 14 violation: Inverted boundaries (max_x <= min_x)
    bad_bounds = WorldBoundaryBounds(min_x=1000.0, max_x=-1000.0)
    bad_wdef = WorldDefinition24("World_Inverted", bad_bounds)
    rep_bounds = WorldArchitectureValidator.validate_world(bad_wdef, graph, landmarks)
    assert rep_bounds.is_valid is False
    assert rep_bounds.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Invalid world boundaries" in iss for iss in rep_bounds.issues)

    # 2. Section 148 & 173 violation: Broken critical path (disconnected critical room)
    broken_graph = ArchitecturalWorldGraph()
    broken_graph.add_room(ArchitecturalRoomNode("Crit_A", ArchitecturalZoneType.CRITICAL_PATH))
    broken_graph.add_room(ArchitecturalRoomNode("Crit_Isolated", ArchitecturalZoneType.CRITICAL_PATH))
    # No connection added between Crit_A and Crit_Isolated!
    rep_path = WorldArchitectureValidator.validate_world(w_def, broken_graph, landmarks)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Broken or disconnected critical path" in iss for iss in rep_path.issues)

    # 3. Section 141 violation: Absolute machine path in landmark ID
    bad_landmarks = ["D:\\UnrealProjects\\Maps\\Landmarks\\LM_Tower.uasset"]
    rep_lm = WorldArchitectureValidator.validate_world(w_def, graph, bad_landmarks)
    assert rep_lm.is_valid is False
    assert rep_lm.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_lm.issues)
