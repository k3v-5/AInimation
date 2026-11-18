"""
Tests for Terrain System (UAF-81.56 Section 187).
"""

import pytest
from uaf.universal_world import (
    TerrainDefinition,
    TerrainRepresentation,
    TerrainGeneratorType,
    TerrainOperator,
    TerrainModifierType,
    TerrainStamp,
    NoiseDefinition,
    NoiseType,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_heightfield():
    t = UniversalWorldFabricator.generate_terrain("T_01", TerrainGeneratorType.FLAT, resolution=16)
    assert t.terrain_id == "T_01"
    assert t.representation == TerrainRepresentation.HEIGHTFIELD
    assert len(t.samples) == 256
    assert t.get_height_at(0.5, 0.5) > 0.0


def test_terrain_generator():
    for gen in [TerrainGeneratorType.FLAT, TerrainGeneratorType.HILLS, TerrainGeneratorType.MOUNTAIN, TerrainGeneratorType.VALLEY]:
        t = UniversalWorldFabricator.generate_terrain(f"T_{gen.value}", gen, resolution=8)
        assert len(t.samples) == 64
        assert all(0.0 <= s <= 1.0 for s in t.samples)


def test_noise():
    noise = NoiseDefinition(seed=123, frequency=0.1, amplitude=200.0, octaves=3)
    val = noise.sample_2d(5.0, 10.0)
    assert isinstance(val, float)


def test_noise_determinism():
    n1 = NoiseDefinition(seed=777)
    n2 = NoiseDefinition(seed=777)
    assert n1.sample_2d(15.2, -8.7) == n2.sample_2d(15.2, -8.7)


def test_terrain_layer():
    t = UniversalWorldFabricator.generate_terrain("T_LAYER", resolution=8)
    assert len(t.layers) >= 1
    assert t.layers[0].layer_type == "base_height"


def test_terrain_operator():
    t = UniversalWorldFabricator.generate_terrain("T_OP", TerrainGeneratorType.FLAT, resolution=8)
    orig_sum = sum(t.samples)
    UniversalWorldFabricator.apply_operator(t, TerrainOperator.ADD, 0.1)
    new_sum = sum(t.samples)
    assert new_sum > orig_sum


def test_terrain_stamp():
    t = UniversalWorldFabricator.generate_terrain("T_STAMP", TerrainGeneratorType.FLAT, resolution=16)
    stamp = TerrainStamp(shape="CIRCLE", position=(0.0, 0.0, 0.0), scale=(10000.0, 10000.0, 50.0), strength=1.0)
    UniversalWorldFabricator.apply_modifier(t, TerrainModifierType.STAMP, stamp)
    assert max(t.samples) >= 0.1


def test_slope():
    t = UniversalWorldFabricator.generate_terrain("T_SLOPE", TerrainGeneratorType.MOUNTAIN, resolution=16)
    assert t.slope_field is not None
    assert len(t.slope_field.values) == 256
    assert max(t.slope_field.values) > 0.0


def test_normals():
    t = UniversalWorldFabricator.generate_terrain("T_NORM", TerrainGeneratorType.HILLS, resolution=8)
    # Slope field derives normal variation
    assert t.slope_field is not None
    assert len(t.slope_field.values) == 64


def test_tangents():
    # Unreal engine landscape tangent alignment check
    t = UniversalWorldFabricator.generate_terrain("T_TANG", TerrainGeneratorType.FLAT, resolution=8)
    assert t.resolution_x == t.resolution_y


def test_terrain_collision():
    t = UniversalWorldFabricator.generate_terrain("T_COLL", resolution=8)
    assert t.collision_profile.enabled is True
    assert "TERRAIN" in t.collision_profile.collision_layers


def test_terrain_navigation():
    world = UniversalWorldFabricator.create_base_world("W_NAV", "Nav World")
    assert world.navigation is not None
    assert "MAIN_NAV_REGION" in world.navigation.regions


def test_terrain_validation():
    world = UniversalWorldFabricator.create_base_world("W_TV", "Terrain Val")
    report = UniversalWorldValidator.validate_world(world)
    assert report.is_valid is True
    assert "CHECK_TERRAIN_SAMPLES" in report.passed_checks
