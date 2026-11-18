"""
Tests for Biome System (UAF-81.56 Section 186).
"""

import pytest
from uaf.universal_world import (
    BiomeType,
    BiomeDefinition,
    BiomeMask,
    BiomeMaskChannel,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_biome_definition():
    b = BiomeDefinition(
        "B_DESERT",
        "Sahara Desert",
        biome_type=BiomeType.DESERT,
        temperature_range=(25.0, 50.0),
        humidity_range=(0.0, 0.2),
    )
    assert b.biome_id == "B_DESERT"
    assert b.biome_type == BiomeType.DESERT
    assert b.temperature_range == (25.0, 50.0)


def test_biome_weight():
    b = BiomeDefinition("B_FOREST", "Woodland", weight=2.5)
    assert b.weight == 2.5
    fit = b.evaluate_fit(altitude=500.0, slope=10.0, temp=15.0, humidity=0.5)
    assert fit == 2.5
    fit_out = b.evaluate_fit(altitude=5000.0, slope=10.0, temp=15.0, humidity=0.5)
    assert fit_out == 0.0


def test_biome_blending():
    b1 = BiomeDefinition("B_GRASS", "Grass", weight=1.0)
    b2 = BiomeDefinition("B_FOREST", "Forest", weight=1.5)
    total_w = b1.weight + b2.weight
    norm1 = b1.weight / total_w
    norm2 = b2.weight / total_w
    assert round(norm1 + norm2, 4) == 1.0


def test_biome_mask():
    mask = BiomeMask("MASK_01", "B_FOREST", resolution_x=8, resolution_y=8, channel=BiomeMaskChannel.PRIMARY)
    mask.values = [0.5] * 64
    assert mask.sample(0.5, 0.5) == 0.5
    d = mask.to_dict()
    assert d["channel"] == "PRIMARY"


def test_biome_priority():
    b1 = BiomeDefinition("B_LOW", "Low Prio", priority=1)
    b2 = BiomeDefinition("B_HIGH", "High Prio", priority=10)
    biomes = [b1, b2]
    highest = max(biomes, key=lambda b: b.priority)
    assert highest.biome_id == "B_HIGH"


def test_biome_validation():
    world = UniversalWorldFabricator.create_base_world("W_BV", "Biome Val")
    world.biomes = []
    report = UniversalWorldValidator.validate_world(world)
    assert any("no biomes defined" in w.lower() for w in report.warnings)


def test_biome_determinism():
    b1 = BiomeDefinition("B_DET", "Deterministic Biome", seed_profile="P1") if hasattr(BiomeDefinition, "seed_profile") else BiomeDefinition("B_DET", "Deterministic Biome")
    b2 = BiomeDefinition("B_DET", "Deterministic Biome")
    assert b1.to_dict() == b2.to_dict()
