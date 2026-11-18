"""
Tests for 10 Canonical Golden Worlds (UAF-81.56 Section 209-210).
"""

import pytest
from uaf.universal_world import (
    BiomeType,
    TerrainGeneratorType,
    WaterType,
    ProductionReadyWorld,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def _validate_golden(world_def):
    sg = UniversalWorldFabricator.build_scene_graph(world_def)
    report = UniversalWorldValidator.validate_world(world_def, sg)
    assert report.is_valid is True
    pkg = ProductionReadyWorld(world_def, sg, report)
    rb = pkg.verify_readback()
    assert rb["readback_status"] == "VERIFIED"
    assert len(pkg.canonical_hash) == 64
    return pkg


def test_golden_flat_world():
    w = UniversalWorldFabricator.create_golden_flat_world()
    assert w.world_id == "GOLDEN_FLAT_WORLD"
    assert w.biomes[0].biome_type == BiomeType.GRASSLAND
    _validate_golden(w)


def test_golden_desert():
    w = UniversalWorldFabricator.create_golden_desert()
    assert w.world_id == "GOLDEN_DESERT"
    assert w.biomes[0].biome_type == BiomeType.DESERT
    _validate_golden(w)


def test_golden_grassland():
    w = UniversalWorldFabricator.create_golden_grassland()
    assert w.world_id == "GOLDEN_GRASSLAND"
    assert w.biomes[0].biome_type == BiomeType.GRASSLAND
    _validate_golden(w)


def test_golden_forest():
    w = UniversalWorldFabricator.create_golden_forest()
    assert w.world_id == "GOLDEN_FOREST"
    assert w.biomes[0].biome_type == BiomeType.FOREST
    _validate_golden(w)


def test_golden_mountain():
    w = UniversalWorldFabricator.create_golden_mountain()
    assert w.world_id == "GOLDEN_MOUNTAIN"
    assert w.biomes[0].biome_type == BiomeType.MOUNTAIN
    _validate_golden(w)


def test_golden_snow():
    w = UniversalWorldFabricator.create_golden_snow()
    assert w.world_id == "GOLDEN_SNOW"
    assert w.biomes[0].biome_type == BiomeType.SNOW
    _validate_golden(w)


def test_golden_coast():
    w = UniversalWorldFabricator.create_golden_coast()
    assert w.world_id == "GOLDEN_COAST"
    assert w.biomes[0].biome_type == BiomeType.COAST
    _validate_golden(w)


def test_golden_river_valley():
    w = UniversalWorldFabricator.create_golden_river_valley()
    assert w.world_id == "GOLDEN_RIVER_VALLEY"
    _validate_golden(w)


def test_golden_urban():
    w = UniversalWorldFabricator.create_golden_urban()
    assert w.world_id == "GOLDEN_URBAN"
    assert len(w.structures) >= 5
    _validate_golden(w)


def test_golden_hybrid_world():
    w = UniversalWorldFabricator.create_golden_hybrid_world()
    assert w.world_id == "GOLDEN_HYBRID_WORLD"
    assert len(w.biomes) >= 3
    _validate_golden(w)
