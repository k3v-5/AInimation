"""
Tests for Terrain World Fabricator, Validator, and Package.
UAF-81.48 Sections 126, 140, 142.
"""

from uaf.terrain_world.engine.terrain_world_fabricator import TerrainWorldFabricationPlatform
from uaf.terrain_world.validation.terrain_world_validator import TerrainWorldValidator
from uaf.terrain_world.package.terrain_world_package import TerrainWorldPackage


def test_terrain_world_fabrication_all_five_golden_worlds():
    builders = [
        TerrainWorldFabricationPlatform.build_golden_desert_world,
        TerrainWorldFabricationPlatform.build_golden_forest_world,
        TerrainWorldFabricationPlatform.build_golden_mountain_world,
        TerrainWorldFabricationPlatform.build_golden_industrial_world,
        TerrainWorldFabricationPlatform.build_golden_sci_fi_world,
    ]

    for builder in builders:
        spec, land_path, part_path, nav_path = builder()
        assert spec.is_valid_world is True
        assert land_path.startswith("/Game/Worlds/Terrain/")
        assert part_path.startswith("/Game/Worlds/Terrain/")
        assert nav_path.startswith("/Game/Worlds/Terrain/")


def test_terrain_world_package_validation_and_serialization():
    spec, land_path, part_path, nav_path = TerrainWorldFabricationPlatform.build_golden_desert_world("World_PkgDesert")

    report = TerrainWorldValidator.validate_terrain_world(spec, land_path, part_path, nav_path)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = TerrainWorldPackage(
        world_id="World_PkgDesert",
        spec=spec,
        landscape_asset_path=land_path,
        world_partition_path=part_path,
        navmesh_path=nav_path,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["world_id"] == "World_PkgDesert"
    assert data["spec"]["biome"] == "DESERT"
    assert data["validation_report"]["review_status"] == "PASSED"
