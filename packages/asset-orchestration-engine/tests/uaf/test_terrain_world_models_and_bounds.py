"""
Tests for Terrain World Models, Dimensions, and Biomes.
UAF-81.48 Sections 4, 10, 11, 15, 23, 126.
"""

from uaf.terrain_world.models.definition import (
    BiomeType48,
    TerrainGenMethod48,
    ErosionType48,
    TerrainDimensions48,
    TerrainWorldSpecification,
)


def test_terrain_dimensions_and_validity():
    dims_ok = TerrainDimensions48(width_m=2000.0, length_m=2000.0, min_height_m=10.0, max_height_m=250.0)
    assert dims_ok.is_valid is True
    assert dims_ok.height_delta_m == 240.0

    dims_neg = TerrainDimensions48(width_m=-100.0, length_m=1000.0)
    assert dims_neg.is_valid is False

    dims_flat = TerrainDimensions48(width_m=1000.0, length_m=1000.0, min_height_m=10.0, max_height_m=15.0)  # delta 5.0m < 10.0m
    assert dims_flat.is_valid is False


def test_terrain_world_specification_and_hashing():
    spec = TerrainWorldSpecification(
        world_id="World_Test_Tundra",
        biome=BiomeType48.TUNDRA,
        method=TerrainGenMethod48.HYBRID,
        dimensions=TerrainDimensions48(width_m=3000.0, length_m=3000.0, min_height_m=5.0, max_height_m=150.0),
        has_erosion=True,
        has_roads=True,
        has_poi=True,
        has_vegetation=True,
        has_navigation=True,
        has_streaming=True,
        seed=987654,
    )

    assert spec.is_valid_world is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["biome"] == "TUNDRA"
    assert data["method"] == "HYBRID"

    bad_spec_erosion = TerrainWorldSpecification(
        world_id="World_NoErosion",
        biome=BiomeType48.TUNDRA,
        has_erosion=False,
    )
    assert bad_spec_erosion.is_valid_world is False
