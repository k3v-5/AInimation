"""
Tests for World Collision System (UAF-81.56 Section 196).
"""

import pytest
from uaf.universal_world import (
    WorldCollisionProfile,
    CollisionLayer,
    CollisionComplexity,
    TerrainCollisionMode,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_world_collision():
    cp = WorldCollisionProfile("CP_01", complexity=CollisionComplexity.HYBRID)
    assert cp.complexity == CollisionComplexity.HYBRID
    assert CollisionLayer.WORLD in cp.layers


def test_terrain_collision():
    world = UniversalWorldFabricator.create_base_world("W_COLL", "Coll World")
    assert world.terrain.collision_profile.mode == TerrainCollisionMode.HEIGHTFIELD
    assert world.terrain.collision_profile.enabled is True


def test_structure_collision():
    cp = WorldCollisionProfile("CP_STRUCT", layers=[CollisionLayer.STRUCTURE])
    assert CollisionLayer.STRUCTURE in cp.layers


def test_water_collision():
    cp = WorldCollisionProfile("CP_WATER", layers=[CollisionLayer.WATER])
    assert CollisionLayer.WATER in cp.layers


def test_collision_layers():
    layers = [CollisionLayer.WORLD, CollisionLayer.TERRAIN, CollisionLayer.VEGETATION, CollisionLayer.ROAD]
    assert len(layers) == 4


def test_collision_validation():
    world = UniversalWorldFabricator.create_base_world("W_CV", "Collision Val")
    report = UniversalWorldValidator.validate_world(world)
    assert report.is_valid is True
