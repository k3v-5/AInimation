"""
Tests for Natural Ecosystem Models, Dimensions, and Biomes.
UAF-81.51 Sections 5, 6, 17, 21, 135, 142.
"""

from uaf.natural_ecosystem.models.definition import (
    NaturalBiomeType51,
    TerrainType51,
    ErosionModel51,
    NaturalTerrainDimensions51,
    NaturalEcosystemSpecification,
)


def test_natural_terrain_dimensions_and_validity():
    dims_ok = NaturalTerrainDimensions51(width_m=2000.0, length_m=2000.0, height_scale_m=300.0)
    assert dims_ok.is_valid is True

    dims_flat = NaturalTerrainDimensions51(width_m=2000.0, length_m=2000.0, height_scale_m=5.0)  # < 10.0m scale
    assert dims_flat.is_valid is False

    dims_neg = NaturalTerrainDimensions51(width_m=-500.0, length_m=1000.0, height_scale_m=100.0)
    assert dims_neg.is_valid is False


def test_natural_ecosystem_specification_and_hashing():
    spec = NaturalEcosystemSpecification(
        ecosystem_id="Eco_Test_Alpine",
        biome=NaturalBiomeType51.MOUNTAIN,
        terrain_type=TerrainType51.ALPINE,
        dimensions=NaturalTerrainDimensions51(width_m=4000.0, length_m=4000.0, height_scale_m=800.0),
        has_erosion=True,
        has_vegetation=True,
        has_rocks=True,
        has_water=True,
        has_poi=True,
        has_navigation=True,
        has_streaming=True,
        seed=13579,
    )

    assert spec.is_valid_ecosystem is True
    assert len(spec.definition_hash) == 64
    data = spec.to_dict()
    assert data["biome"] == "MOUNTAIN"
    assert data["terrain_type"] == "ALPINE"

    bad_spec_veg = NaturalEcosystemSpecification(
        ecosystem_id="Eco_NoVeg",
        biome=NaturalBiomeType51.FOREST,
        terrain_type=TerrainType51.ROLLING,
        has_vegetation=False,
    )
    assert bad_spec_veg.is_valid_ecosystem is False
