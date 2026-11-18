"""
Tests for Terrain Erosion (UAF-81.56 Section 188).
"""

import pytest
from uaf.universal_world import (
    TerrainGeneratorType,
    ErosionProfile,
    ErosionType,
    UniversalWorldFabricator,
)


def test_hydraulic_erosion():
    t = UniversalWorldFabricator.generate_terrain("T_ER_HYD", TerrainGeneratorType.HILLS, resolution=16)
    ep = ErosionProfile(erosion_type=ErosionType.HYDRAULIC, iterations=3, solubility=0.05)
    orig_sum = sum(t.samples)
    UniversalWorldFabricator.apply_erosion(t, ep)
    assert sum(t.samples) < orig_sum
    assert len(t.layers) == 2


def test_thermal_erosion():
    t = UniversalWorldFabricator.generate_terrain("T_ER_THERM", TerrainGeneratorType.MOUNTAIN, resolution=16)
    ep = ErosionProfile(erosion_type=ErosionType.THERMAL, iterations=2)
    UniversalWorldFabricator.apply_erosion(t, ep)
    assert t.erosion_profile.erosion_type == ErosionType.THERMAL


def test_wind_erosion():
    t = UniversalWorldFabricator.generate_terrain("T_ER_WIND", TerrainGeneratorType.HILLS, resolution=16)
    ep = ErosionProfile(erosion_type=ErosionType.WIND, iterations=2)
    UniversalWorldFabricator.apply_erosion(t, ep)
    assert t.erosion_profile.erosion_type == ErosionType.WIND


def test_erosion_determinism():
    t1 = UniversalWorldFabricator.generate_terrain("T1", TerrainGeneratorType.HILLS, seed=555, resolution=16)
    t2 = UniversalWorldFabricator.generate_terrain("T2", TerrainGeneratorType.HILLS, seed=555, resolution=16)
    ep1 = ErosionProfile(seed=555, iterations=3)
    ep2 = ErosionProfile(seed=555, iterations=3)
    UniversalWorldFabricator.apply_erosion(t1, ep1)
    UniversalWorldFabricator.apply_erosion(t2, ep2)
    assert t1.samples == t2.samples


def test_erosion_validation():
    ep = ErosionProfile(iterations=5, rain_amount=0.01)
    d = ep.to_dict()
    assert d["iterations"] == 5
    assert d["erosion_type"] == "HYDRAULIC"
