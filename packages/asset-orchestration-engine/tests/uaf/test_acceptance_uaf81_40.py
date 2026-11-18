"""
UAF-81.40 Acceptance Tests (Sections 153, 148, 171, 7, 9, 149, 150, 176).
Verifies:
- Section 153: Final Acceptance Criteria (Generates and validates all 8 Golden Worlds:
  Small World, Forest World, Desert World, Industrial World, Urban World, Mountain World, Sci-Fi World, Combat World).
- Sections 148, 171: Hard Fail Conditions Test (Zero tolerance for non-positive dimensions, height < 10m,
  zero cells, missing world partition on large worlds, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.world_build.engine.world_build_fabricator import WorldBuildFabricationPlatform
from uaf.world_build.validation.world_build_validator import WorldBuildValidator
from uaf.world_build.models.definition import (
    WorldBuildSpecification,
    WorldScaleProfile40,
    RegionType40,
    WorldDimensions40,
)
from uaf.world_build.package.world_build_package import WorldBuildPackage


def test_final_world_build_acceptance_section_153():
    """
    Acceptance Test Section 153:
    Synthesizes and validates all 8 Golden Worlds.
    """
    builders = [
        ("World_Gold_Small", WorldBuildFabricationPlatform.build_golden_small_world),
        ("World_Gold_Forest", WorldBuildFabricationPlatform.build_golden_forest_world),
        ("World_Gold_Desert", WorldBuildFabricationPlatform.build_golden_desert_world),
        ("World_Gold_Industrial", WorldBuildFabricationPlatform.build_golden_industrial_world),
        ("World_Gold_Urban", WorldBuildFabricationPlatform.build_golden_urban_world),
        ("World_Gold_Mountain", WorldBuildFabricationPlatform.build_golden_mountain_world),
        ("World_Gold_SciFi", WorldBuildFabricationPlatform.build_golden_sci_fi_world),
        ("World_Gold_Combat", WorldBuildFabricationPlatform.build_golden_combat_world),
    ]

    for world_id, builder_fn in builders:
        spec, level_path, part_path = builder_fn(world_id)
        assert spec.is_valid_scale is True

        report = WorldBuildValidator.validate_world_build(spec, level_path, part_path)
        assert report.is_valid is True, f"Failed for {world_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = WorldBuildPackage(
            world_id=world_id,
            spec=spec,
            level_asset_path=level_path,
            world_partition_data_path=part_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["world_id"] == world_id


def test_hard_fail_conditions_section_148_171():
    """
    Acceptance Test Sections 148, 171:
    Hard fail conditions:
    1. INVALID_DIMENSIONS: Non-positive width/length or height < 10m.
    2. INVALID_CELL_COUNT: cell_count < 1.
    3. MISSING_WORLD_PARTITION: World size >= 2000m without World Partition.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, level_path, part_path = WorldBuildFabricationPlatform.build_golden_forest_world("World_Fault_Test")

    # 1. Dimension violation: width_m = -500.0
    bad_dims = WorldDimensions40(width_m=-500.0, length_m=2000.0, height_m=200.0)
    bad_spec_dims = WorldBuildSpecification(
        "World_BadDims",
        WorldScaleProfile40.MEDIUM,
        RegionType40.FOREST,
        dimensions=bad_dims,
    )
    rep_dims = WorldBuildValidator.validate_world_build(bad_spec_dims, level_path, part_path)
    assert rep_dims.is_valid is False
    assert rep_dims.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_DIMENSIONS" in iss for iss in rep_dims.issues)

    # 2. Cell count violation: 0 cells
    bad_spec_cells = WorldBuildSpecification(
        "World_ZeroCells",
        WorldScaleProfile40.MEDIUM,
        RegionType40.FOREST,
        cell_count=0,
    )
    rep_cells = WorldBuildValidator.validate_world_build(bad_spec_cells, level_path, part_path)
    assert rep_cells.is_valid is False
    assert rep_cells.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_CELL_COUNT" in iss for iss in rep_cells.issues)

    # 3. World partition violation: 3000x3000m with has_world_partition=False
    large_dims = WorldDimensions40(width_m=3000.0, length_m=3000.0, height_m=300.0)
    bad_spec_part = WorldBuildSpecification(
        "World_NoPartition",
        WorldScaleProfile40.LARGE,
        RegionType40.DESERT,
        dimensions=large_dims,
        has_world_partition=False,
    )
    rep_part = WorldBuildValidator.validate_world_build(bad_spec_part, level_path, part_path)
    assert rep_part.is_valid is False
    assert rep_part.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_WORLD_PARTITION" in iss for iss in rep_part.issues)

    # 4. Path purity violation: Absolute machine path
    bad_level_path = "D:\\UnrealProjects\\Worlds\\Level_Forest.umap"
    rep_path = WorldBuildValidator.validate_world_build(spec, bad_level_path, part_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
