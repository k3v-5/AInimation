"""
Tests for World Query Engine (UAF-81.56 Section 203).
"""

import pytest
from uaf.universal_world import (
    WorldQuery,
    WorldQueryType,
    UniversalWorldFabricator,
)


@pytest.fixture
def sample_world():
    return UniversalWorldFabricator.create_base_world("W_QUERY_TEST", "Query World", seed=123)


def test_height_query(sample_world):
    q = WorldQuery(WorldQueryType.HEIGHT_AT, position=(0.0, 0.0, 0.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "height" in res
    assert isinstance(res["height"], float)


def test_slope_query(sample_world):
    q = WorldQuery(WorldQueryType.SLOPE_AT, position=(100.0, 100.0, 0.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "slope" in res


def test_biome_query(sample_world):
    q = WorldQuery(WorldQueryType.BIOME_AT, position=(0.0, 0.0, 0.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "biome_id" in res
    assert "BIOME" in res["biome_id"]


def test_water_query(sample_world):
    q = WorldQuery(WorldQueryType.WATER_AT, position=(0.0, 0.0, -100.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "in_water" in res


def test_asset_query(sample_world):
    q = WorldQuery(WorldQueryType.ASSET_AT, position=(0.0, 0.0, 0.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert res is not None


def test_navigation_query(sample_world):
    q = WorldQuery(WorldQueryType.NAVIGATION_AT, position=(500.0, 500.0, 50.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "walkable" in res


def test_cell_query(sample_world):
    q = WorldQuery(WorldQueryType.CELL_AT, position=(0.0, 0.0, 0.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "cell_id" in res


def test_nearest_asset(sample_world):
    q = WorldQuery(WorldQueryType.NEAREST_ASSET, position=(0.0, 0.0, 0.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "distance" in res
    assert res["distance"] < float("inf")


def test_nearest_road(sample_world):
    q = WorldQuery(WorldQueryType.NEAREST_ROAD, position=(0.0, 0.0, 0.0))
    res = UniversalWorldFabricator.solve_query(sample_world, q)
    assert "road_id" in res
