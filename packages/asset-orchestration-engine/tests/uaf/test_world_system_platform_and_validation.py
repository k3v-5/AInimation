"""
Tests for World Fabrication Platform, Validation, and Package.
UAF-81.16 Sections 214, 226, 235, 236.
"""

from uaf.world_system.platform.world_fabricator import WorldFabricationPlatform
from uaf.world_system.validation.world_validator import WorldValidator
from uaf.world_system.package.world_package import WorldFabricationPackage


def test_fabrication_platform_canonical_and_golden_worlds():
    # 1. Canonical Section 235 World
    w_def, biomes, water, roads, districts, zones = WorldFabricationPlatform.build_canonical_world("World_Test_Canonical")
    assert len(biomes) == 2
    assert len(water) == 2
    assert roads.has_bridges is True
    assert len(districts) == 1
    assert len(zones) == 3

    # 2. Small Forest
    w1, b1, wt1, r1, d1, z1 = WorldFabricationPlatform.build_small_forest_world("W_Forest")
    assert len(b1) == 1

    # 3. Small Desert
    w2, b2, wt2, r2, d2, z2 = WorldFabricationPlatform.build_small_desert_world("W_Desert")
    assert len(wt2) == 0

    # 4. Small Urban
    w3, b3, wt3, r3, d3, z3 = WorldFabricationPlatform.build_small_urban_world("W_Urban")
    assert d3[0].building_count == 12

    # 5. Small Mountain
    w4, b4, wt4, r4, d4, z4 = WorldFabricationPlatform.build_small_mountain_world("W_Mountain")
    assert w4.bounds.max_z == 450.0


def test_world_fabrication_package_validation_and_serialization():
    w_def, biomes, water, roads, districts, zones = WorldFabricationPlatform.build_canonical_world("World_Pkg_Test")

    report = WorldValidator.validate_world(w_def, biomes, water, roads, districts, zones)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = WorldFabricationPackage(
        asset_id="World_Pkg_Test",
        world_definition=w_def,
        biomes=biomes,
        water_bodies=water,
        road_network=roads,
        districts=districts,
        gameplay_zones=zones,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "World_Pkg_Test"
    assert len(data["biomes"]) == 2
    assert data["validation_report"]["review_status"] == "PASSED"
