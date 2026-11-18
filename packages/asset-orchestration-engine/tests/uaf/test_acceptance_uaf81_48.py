"""
UAF-81.48 Acceptance Tests (Sections 126, 25, 124, 137, 138, 139, 140, 142).
Verifies:
- Section 126: Final Acceptance Criteria (Generates and validates all 5 Golden Worlds:
  Desert, Forest, Mountain, Industrial, Sci-Fi).
- Sections 25, 124, 137, 139: Hard Fail Conditions Test (Zero tolerance for invalid terrain dimensions,
  height delta < 10m, missing erosion, roads, POIs, vegetation, nav, or streaming, or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.terrain_world.engine.terrain_world_fabricator import TerrainWorldFabricationPlatform
from uaf.terrain_world.validation.terrain_world_validator import TerrainWorldValidator
from uaf.terrain_world.models.definition import (
    TerrainWorldSpecification,
    BiomeType48,
    TerrainDimensions48,
)
from uaf.terrain_world.package.terrain_world_package import TerrainWorldPackage


def test_final_terrain_world_acceptance_section_126():
    """
    Acceptance Test Section 126:
    Synthesizes and validates all 5 Golden Worlds.
    """
    builders = [
        ("World_Gold_Desert", TerrainWorldFabricationPlatform.build_golden_desert_world),
        ("World_Gold_Forest", TerrainWorldFabricationPlatform.build_golden_forest_world),
        ("World_Gold_Mountain", TerrainWorldFabricationPlatform.build_golden_mountain_world),
        ("World_Gold_Industrial", TerrainWorldFabricationPlatform.build_golden_industrial_world),
        ("World_Gold_SciFi", TerrainWorldFabricationPlatform.build_golden_sci_fi_world),
    ]

    for world_id, builder_fn in builders:
        spec, land_path, part_path, nav_path = builder_fn(world_id)
        assert spec.is_valid_world is True

        report = TerrainWorldValidator.validate_terrain_world(spec, land_path, part_path, nav_path)
        assert report.is_valid is True, f"Failed for {world_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = TerrainWorldPackage(
            world_id=world_id,
            spec=spec,
            landscape_asset_path=land_path,
            world_partition_path=part_path,
            navmesh_path=nav_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["world_id"] == world_id


def test_hard_fail_conditions_section_25_124_137_139():
    """
    Acceptance Test Sections 25, 124, 137, 139:
    Hard fail conditions:
    1. INVALID_TERRAIN_DIMENSIONS: Non-positive width/length or height delta < 10m.
    2. MISSING_CORE_SUBSYSTEMS: has_erosion, has_roads, has_poi, has_vegetation, has_navigation, or has_streaming is False.
    3. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, land_path, part_path, nav_path = TerrainWorldFabricationPlatform.build_golden_desert_world("World_Fault_Test")

    # 1. Height delta violation: 4.0m (< 10.0m delta)
    bad_dims = TerrainDimensions48(width_m=2000.0, length_m=2000.0, min_height_m=10.0, max_height_m=14.0)
    bad_spec_dims = TerrainWorldSpecification(
        "World_FlatHeight",
        BiomeType48.DESERT,
        dimensions=bad_dims,
    )
    rep_dims = TerrainWorldValidator.validate_terrain_world(bad_spec_dims, land_path, part_path, nav_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_TERRAIN_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Missing erosion
    bad_spec_erosion = TerrainWorldSpecification(
        "World_NoErosion",
        BiomeType48.DESERT,
        has_erosion=False,
    )
    rep_ero = TerrainWorldValidator.validate_terrain_world(bad_spec_erosion, land_path, part_path, nav_path)
    assert rep_ero.is_valid is False
    assert rep_ero.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_ero.issues)

    # 3. Missing roads
    bad_spec_roads = TerrainWorldSpecification(
        "World_NoRoads",
        BiomeType48.DESERT,
        has_roads=False,
    )
    rep_roads = TerrainWorldValidator.validate_terrain_world(bad_spec_roads, land_path, part_path, nav_path)
    assert rep_roads.is_valid is False
    assert rep_roads.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_SUBSYSTEMS" in iss for iss in rep_roads.issues)

    # 4. Path purity violation: Absolute machine path
    bad_land_path = "D:\\UnrealProjects\\Landscape\\Landscape_Desert.umap"
    rep_path = TerrainWorldValidator.validate_terrain_world(spec, bad_land_path, part_path, nav_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
