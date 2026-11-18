"""
Tests for Terrain Biome Models, Bounds, and Ecology.
UAF-81.36 Sections 4, 14, 16, 20, 21, 27, 28, 123.
"""

from uaf.terrain_biome.models.definition import (
    BiomeType36,
    VegetationCategory36,
    SlopeClassification36,
    TerrainBounds36,
    TerrainBiomeSpecification,
)


def test_terrain_bounds_and_validity():
    bounds_ok = TerrainBounds36(0.0, 200.0, 1000.0, 1000.0)
    assert bounds_ok.is_valid is True

    bounds_flat = TerrainBounds36(100.0, 105.0, 1000.0, 1000.0)  # span 5m < 10m
    assert bounds_flat.is_valid is False

    bounds_neg_dim = TerrainBounds36(0.0, 200.0, -1000.0, 1000.0)
    assert bounds_neg_dim.is_valid is False


def test_terrain_biome_specification_and_hashing():
    spec = TerrainBiomeSpecification(
        terrain_id="Terrain_Test_Tundra",
        primary_biome=BiomeType36.TUNDRA,
        bounds=TerrainBounds36(100.0, 500.0, 2000.0, 2000.0),
        vegetation_categories=[VegetationCategory36.BUSH, VegetationCategory36.GRASS],
        water_body_count=1,
        road_segments_count=1,
        seed=998877,
    )

    assert spec.is_valid_scale is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["primary_biome"] == "TUNDRA"
    assert data["water_body_count"] == 1

    bad_spec = TerrainBiomeSpecification(
        terrain_id="Terrain_BadBounds",
        primary_biome=BiomeType36.TUNDRA,
        bounds=TerrainBounds36(50.0, 50.0, 1000.0, 1000.0),
    )
    assert bad_spec.is_valid_scale is False
