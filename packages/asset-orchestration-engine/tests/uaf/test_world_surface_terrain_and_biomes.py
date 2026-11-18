"""
Tests for World Surface Territory, Landmarks, and Biomes.
UAF-81.13 Sections 4, 5, 32, 37, 38.
"""

from uaf.world_surface.terrain.territory import TerrainMode, ErosionType, TerritoryModel
from uaf.world_surface.terrain.landmark import LandmarkType, NaturalLandmark
from uaf.world_surface.biomes.biome import BiomeType, BiomeProfile


def test_territory_model_and_hashing():
    terr = TerritoryModel(
        territory_id="Terr_Alpine_01",
        world_width_m=2000.0,
        world_length_m=2000.0,
        min_height_m=0.0,
        max_height_m=350.0,
        terrain_mode=TerrainMode.HYBRID_TERRAIN,
        seed=12345,
    )
    assert terr.world_width_m == 2000.0
    assert terr.terrain_mode == TerrainMode.HYBRID_TERRAIN
    assert len(terr.territory_hash) == 64
    data = terr.to_dict()
    assert data["territory_id"] == "Terr_Alpine_01"


def test_natural_landmark_definition():
    lm = NaturalLandmark(
        landmark_id="LM_Pinnacle",
        landmark_type=LandmarkType.CLIFF,
        position=[100.0, 200.0, 150.0],
        prominence=0.9,
    )
    assert lm.landmark_type == LandmarkType.CLIFF
    assert lm.prominence == 0.9
    data = lm.to_dict()
    assert data["landmark_type"] == "CLIFF"


def test_biome_profiles():
    desert = BiomeProfile.create_desert_profile()
    assert desert.biome_type == BiomeType.DESERT
    assert desert.moisture == 0.05
    assert desert.has_water is False

    forest = BiomeProfile.create_forest_profile()
    assert forest.biome_type == BiomeType.FOREST
    assert forest.moisture == 0.75
    assert forest.has_water is True
