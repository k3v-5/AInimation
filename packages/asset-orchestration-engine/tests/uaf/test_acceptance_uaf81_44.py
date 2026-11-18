"""
UAF-81.44 Acceptance Tests (Sections 134, 18, 19, 131, 147, 148, 149, 150, 151, 130, 146).
Verifies:
- Section 134: Final Acceptance Criteria (Generates and validates all 6 Golden Worlds:
  Industrial, Sci-Fi Facility, Bunker, Outdoor, Forest, Combat Arena).
- Sections 131, 148, 149, 150, 151: Hard Fail Conditions Test (Zero tolerance for invalid map dimensions,
  cell_size < 10cm, zero pieces, disabled core subsystems, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.map_authoring.engine.map_authoring_fabricator import MapAuthoringFabricationPlatform
from uaf.map_authoring.validation.map_authoring_validator import MapAuthoringValidator
from uaf.map_authoring.models.definition import (
    MapAuthoringSpecification,
    WorldTheme44,
    MapDimensions44,
)
from uaf.map_authoring.package.map_authoring_package import MapAuthoringPackage


def test_final_map_authoring_acceptance_section_134():
    """
    Acceptance Test Section 134:
    Synthesizes and validates all 6 Golden Worlds.
    """
    builders = [
        ("Map_Gold_Industrial", MapAuthoringFabricationPlatform.build_golden_industrial),
        ("Map_Gold_SciFiFacility", MapAuthoringFabricationPlatform.build_golden_sci_fi_facility),
        ("Map_Gold_Bunker", MapAuthoringFabricationPlatform.build_golden_bunker),
        ("Map_Gold_Outdoor", MapAuthoringFabricationPlatform.build_golden_outdoor),
        ("Map_Gold_Forest", MapAuthoringFabricationPlatform.build_golden_forest),
        ("Map_Gold_CombatArena", MapAuthoringFabricationPlatform.build_golden_combat_arena),
    ]

    for map_id, builder_fn in builders:
        spec, level_path, part_path, nav_path = builder_fn(map_id)
        assert spec.is_valid_map is True

        report = MapAuthoringValidator.validate_map_authoring(spec, level_path, part_path, nav_path)
        assert report.is_valid is True, f"Failed for {map_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = MapAuthoringPackage(
            map_id=map_id,
            spec=spec,
            level_asset_path=level_path,
            world_partition_path=part_path,
            navmesh_path=nav_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["map_id"] == map_id


def test_hard_fail_conditions_section_131_148_149_150_151():
    """
    Acceptance Test Sections 131, 148, 149, 150, 151:
    Hard fail conditions:
    1. INVALID_DIMENSIONS: Non-positive width/length or height < 10m.
    2. INVALID_GRID_OR_PIECES: cell_size_cm < 10.0cm or modular_piece_count < 1.
    3. MISSING_CORE_SUBSYSTEMS: has_collision, has_navigation, or has_lighting is False.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, level_path, part_path, nav_path = MapAuthoringFabricationPlatform.build_golden_industrial("Map_Fault_Test")

    # 1. Dimension violation: width_m = -200.0
    bad_dims = MapDimensions44(width_m=-200.0, length_m=1000.0, height_m=100.0)
    bad_spec_dims = MapAuthoringSpecification(
        "Map_BadDims",
        WorldTheme44.INDUSTRIAL,
        dimensions=bad_dims,
    )
    rep_dims = MapAuthoringValidator.validate_map_authoring(bad_spec_dims, level_path, part_path, nav_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Grid violation: cell_size_cm = 5.0 (< 10.0cm)
    bad_spec_grid = MapAuthoringSpecification(
        "Map_SmallGrid",
        WorldTheme44.INDUSTRIAL,
        cell_size_cm=5.0,
    )
    rep_grid = MapAuthoringValidator.validate_map_authoring(bad_spec_grid, level_path, part_path, nav_path)
    assert rep_grid.is_valid is False
    assert rep_grid.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_GRID_OR_PIECES" in iss for iss in rep_grid.issues)

    # 3. Missing navigation subsystem
    bad_spec_nav = MapAuthoringSpecification(
        "Map_NoNav",
        WorldTheme44.INDUSTRIAL,
        has_navigation=False,
    )
    rep_nav = MapAuthoringValidator.validate_map_authoring(bad_spec_nav, level_path, part_path, nav_path)
    assert rep_nav.is_valid is False
    assert rep_nav.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_nav.issues)

    # 4. Path purity violation: Absolute machine path
    bad_lvl_path = "D:\\UnrealProjects\\Maps\\Map_Industrial.umap"
    rep_path = MapAuthoringValidator.validate_map_authoring(spec, bad_lvl_path, part_path, nav_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
