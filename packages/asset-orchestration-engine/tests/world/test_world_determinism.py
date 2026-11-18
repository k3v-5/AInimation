"""
Tests for World Determinism (UAF-81.56 Section 208 - 26 Determinism Tests).
"""

import pytest
from uaf.universal_world import (
    TerrainGeneratorType,
    NoiseDefinition,
    ErosionProfile,
    WaterType,
    BuildingType,
    RoadType,
    WorldQuery,
    WorldQueryType,
    WorldCacheKey,
    ProductionReadyWorld,
    UniversalWorldFabricator,
)


def test_det_world_generation():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert w1.world_hash == w2.world_hash


def test_det_region_generation():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [r.to_dict() for r in w1.regions] == [r.to_dict() for r in w2.regions]


def test_det_cell_generation():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [c.to_dict() for c in w1.cells] == [c.to_dict() for c in w2.cells]


def test_det_biome_assignment():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [b.to_dict() for b in w1.biomes] == [b.to_dict() for b in w2.biomes]


def test_det_noise():
    n1 = NoiseDefinition(seed=12345)
    n2 = NoiseDefinition(seed=12345)
    assert n1.sample_2d(2.5, 8.1) == n2.sample_2d(2.5, 8.1)


def test_det_terrain():
    t1 = UniversalWorldFabricator.generate_terrain("T1", TerrainGeneratorType.HILLS, seed=999, resolution=16)
    t2 = UniversalWorldFabricator.generate_terrain("T1", TerrainGeneratorType.HILLS, seed=999, resolution=16)
    assert t1.samples == t2.samples


def test_det_erosion():
    t1 = UniversalWorldFabricator.generate_terrain("T1", TerrainGeneratorType.HILLS, seed=333, resolution=16)
    t2 = UniversalWorldFabricator.generate_terrain("T1", TerrainGeneratorType.HILLS, seed=333, resolution=16)
    ep1 = ErosionProfile(seed=333, iterations=2)
    ep2 = ErosionProfile(seed=333, iterations=2)
    UniversalWorldFabricator.apply_erosion(t1, ep1)
    UniversalWorldFabricator.apply_erosion(t2, ep2)
    assert t1.samples == t2.samples


def test_det_water():
    w1 = UniversalWorldFabricator.generate_water("W1", WaterType.LAKE)
    w2 = UniversalWorldFabricator.generate_water("W1", WaterType.LAKE)
    assert w1.to_dict() == w2.to_dict()


def test_det_vegetation_scatter():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [i.to_dict() for i in w1.scatter_instances] == [i.to_dict() for i in w2.scatter_instances]


def test_det_rock_scatter():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [r.to_dict() for r in w1.rocks] == [r.to_dict() for r in w2.rocks]


def test_det_prop_scatter():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [p.to_dict() for p in w1.props] == [p.to_dict() for p in w2.props]


def test_det_building_generation():
    b1 = UniversalWorldFabricator.generate_building("B1", BuildingType.HOUSE, floors=2)
    b2 = UniversalWorldFabricator.generate_building("B1", BuildingType.HOUSE, floors=2)
    assert b1.to_dict() == b2.to_dict()


def test_det_road_generation():
    r1 = UniversalWorldFabricator.generate_road("R1", RoadType.ROAD)
    r2 = UniversalWorldFabricator.generate_road("R1", RoadType.ROAD)
    assert r1.to_dict() == r2.to_dict()


def test_det_navigation():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert w1.navigation.to_dict() == w2.navigation.to_dict()


def test_det_hlod():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert w1.hlod.to_dict() == w2.hlod.to_dict()


def test_det_impostors():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [i.to_dict() for i in w1.impostors] == [i.to_dict() for i in w2.impostors]


def test_det_spawn():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert w1.spawn.to_dict() == w2.spawn.to_dict()


def test_det_landmarks():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert [lm.to_dict() for lm in w1.landmarks] == [lm.to_dict() for lm in w2.landmarks]


def test_det_world_queries():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    q = WorldQuery(WorldQueryType.HEIGHT_AT, position=(100.0, 200.0, 0.0))
    res1 = UniversalWorldFabricator.solve_query(w1, q)
    res2 = UniversalWorldFabricator.solve_query(w2, q)
    assert res1 == res2


def test_det_partial_regeneration():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    snap1 = UniversalWorldFabricator.create_snapshot(w1)
    snap2 = UniversalWorldFabricator.create_snapshot(w2)
    diff = UniversalWorldFabricator.compute_diff(snap1, snap2)
    assert len(diff.changes) == 0


def test_det_cache_keys():
    k1 = WorldCacheKey("HASH_A", "CELL_0_0")
    k2 = WorldCacheKey("HASH_A", "CELL_0_0")
    assert k1 == k2


def test_det_export_metadata():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    sg1 = UniversalWorldFabricator.build_scene_graph(w1)
    sg2 = UniversalWorldFabricator.build_scene_graph(w2)
    pkg1 = ProductionReadyWorld(w1, sg1)
    pkg2 = ProductionReadyWorld(w2, sg2)
    assert pkg1.canonical_hash == pkg2.canonical_hash


def test_det_scene_graph():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    sg1 = UniversalWorldFabricator.build_scene_graph(w1)
    sg2 = UniversalWorldFabricator.build_scene_graph(w2)
    assert sg1.to_dict() == sg2.to_dict()


def test_det_splatmap():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert w1.terrain.splatmap.to_dict() == w2.terrain.splatmap.to_dict()


def test_det_slope_field():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    assert w1.terrain.slope_field.values == w2.terrain.slope_field.values


def test_det_canonical_hash():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Det World", seed=777)
    sg1 = UniversalWorldFabricator.build_scene_graph(w1)
    sg2 = UniversalWorldFabricator.build_scene_graph(w2)
    pkg1 = ProductionReadyWorld(w1, sg1)
    pkg2 = ProductionReadyWorld(w2, sg2)
    rb1 = pkg1.verify_readback()
    rb2 = pkg2.verify_readback()
    assert rb1 == rb2
