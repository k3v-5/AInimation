"""
Tests for World Build Fabricator, Validator, and Package.
UAF-81.40 Sections 149, 150, 153, 176.
"""

from uaf.world_build.engine.world_build_fabricator import WorldBuildFabricationPlatform
from uaf.world_build.validation.world_build_validator import WorldBuildValidator
from uaf.world_build.package.world_build_package import WorldBuildPackage


def test_world_build_fabrication_all_eight_golden_worlds():
    builders = [
        WorldBuildFabricationPlatform.build_golden_small_world,
        WorldBuildFabricationPlatform.build_golden_forest_world,
        WorldBuildFabricationPlatform.build_golden_desert_world,
        WorldBuildFabricationPlatform.build_golden_industrial_world,
        WorldBuildFabricationPlatform.build_golden_urban_world,
        WorldBuildFabricationPlatform.build_golden_mountain_world,
        WorldBuildFabricationPlatform.build_golden_sci_fi_world,
        WorldBuildFabricationPlatform.build_golden_combat_world,
    ]

    for builder in builders:
        spec, level_path, part_path = builder()
        assert spec.is_valid_scale is True
        assert level_path.startswith("/Game/Worlds/")
        assert part_path.startswith("/Game/Worlds/")


def test_world_build_package_validation_and_serialization():
    spec, level_path, part_path = WorldBuildFabricationPlatform.build_golden_forest_world("World_PkgForest")

    report = WorldBuildValidator.validate_world_build(spec, level_path, part_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = WorldBuildPackage(
        world_id="World_PkgForest",
        spec=spec,
        level_asset_path=level_path,
        world_partition_data_path=part_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["world_id"] == "World_PkgForest"
    assert data["spec"]["primary_region"] == "FOREST"
    assert data["validation_report"]["review_status"] == "PASSED"
