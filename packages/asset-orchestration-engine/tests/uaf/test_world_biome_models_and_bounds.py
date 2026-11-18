"""
Tests for World Biome Models and Bounds.
UAF-81.32 Sections 3, 4, 8, 9, 11, 28, 29.
"""

from uaf.world_biome.models.definition import (
    WorldType32,
    BiomeType32,
    WorldBounds32,
    BiomeDefinition32,
    BiomeWorldDefinition,
)


def test_world_bounds_and_validity():
    bounds_ok = WorldBounds32(-5000.0, 5000.0, -5000.0, 5000.0, 0.0, 2000.0)
    assert bounds_ok.is_valid is True

    bounds_inverted = WorldBounds32(5000.0, -5000.0, -5000.0, 5000.0, 0.0, 2000.0)
    assert bounds_inverted.is_valid is False

    bounds_flat = WorldBounds32(-50.0, 0.0, -50.0, 0.0, 0.0, 50.0)
    assert bounds_flat.is_valid is False  # span < 100cm


def test_biome_definition_and_hashing():
    biome = BiomeDefinition32("Biome_Taiga", BiomeType32.ARCTIC_TUNDRA, temperature=0.2, humidity=0.5, altitude_range=[500.0, 2500.0])
    assert biome.is_valid is True

    w_def = BiomeWorldDefinition(
        world_id="World_Spec_Northlands",
        world_type=WorldType32.OPEN_WORLD,
        bounds=WorldBounds32(-10000.0, 10000.0, -10000.0, 10000.0, 0.0, 3000.0),
        biomes=[biome],
        seed=889900,
    )

    assert len(w_def.definition_hash) == 64
    data = w_def.to_dict()
    assert data["world_type"] == "OPEN_WORLD"
    assert len(data["biomes"]) == 1

    bad_biome = BiomeDefinition32("Biome_Bad", BiomeType32.ARID_DESERT, temperature=1.5)
    assert bad_biome.is_valid is False
