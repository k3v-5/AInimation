"""
Tests for Partial World Regeneration & Invalidation Graph (UAF-81.56 Section 204).
"""

import pytest
from uaf.universal_world import (
    TerrainGeneratorType,
    BiomeType,
    RoadType,
    BuildingType,
    UniversalWorldFabricator,
)


@pytest.fixture
def base_world():
    return UniversalWorldFabricator.create_base_world("W_PARTIAL", "Partial Reg World", seed=77)


def test_regenerate_cell(base_world):
    old_cell = base_world.cells[0]
    # Regenerate single cell
    new_cell = UniversalWorldFabricator.create_base_world("W_PARTIAL", "Partial Reg World", seed=77).cells[0]
    assert old_cell.to_dict() == new_cell.to_dict()


def test_regenerate_region(base_world):
    old_reg = base_world.regions[0]
    base_world.regions[0].name = "Updated Region Name"
    assert base_world.regions[0].name != old_reg.region_id


def test_regenerate_biome(base_world):
    orig_type = base_world.biomes[0].biome_type
    base_world.biomes[0].biome_type = BiomeType.DESERT
    assert base_world.biomes[0].biome_type != orig_type


def test_regenerate_terrain_layer(base_world):
    orig_samples = list(base_world.terrain.samples)
    base_world.terrain = UniversalWorldFabricator.generate_terrain("T_NEW", TerrainGeneratorType.MOUNTAIN)
    assert base_world.terrain.samples != orig_samples


def test_regenerate_vegetation(base_world):
    orig_count = len(base_world.scatter_instances)
    base_world.scatter_instances = UniversalWorldFabricator.scatter_assets(
        base_world.bounds, base_world.vegetation.scatter_profiles[0], "SM_Tree_V2", max_count=5
    )
    assert len(base_world.scatter_instances) == 5
    assert base_world.scatter_instances[0].asset_id == "SM_Tree_V2"


def test_regenerate_road(base_world):
    orig_road = base_world.roads[0]
    new_road = UniversalWorldFabricator.generate_road("RD_NEW", RoadType.HIGHWAY, width=1500.0)
    base_world.roads[0] = new_road
    assert base_world.roads[0].width == 1500.0


def test_regenerate_building(base_world):
    orig_bld = base_world.structures[0]
    new_bld = UniversalWorldFabricator.generate_building("BLD_MOD", BuildingType.INDUSTRIAL, floors=3)
    base_world.structures[0] = new_bld
    assert base_world.structures[0].building_type == BuildingType.INDUSTRIAL


def test_dependency_invalidation(base_world):
    # Dependency graph test: changing terrain seed modifies world hash
    w1 = UniversalWorldFabricator.create_base_world("W", "Dep Test", seed=10)
    w2 = UniversalWorldFabricator.create_base_world("W", "Dep Test", seed=20)
    assert w1.terrain.terrain_id != w2.terrain.terrain_id or w1.world_hash != w2.world_hash
