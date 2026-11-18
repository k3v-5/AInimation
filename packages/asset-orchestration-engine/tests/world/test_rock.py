"""
Tests for Rock & Cliff System (UAF-81.56 Section 191).
"""

import pytest
from uaf.universal_world import (
    RockDefinition,
    RockType,
    RockOrientation,
    WorldBounds,
    VegetationScatterProfile,
    UniversalWorldFabricator,
)


def test_rock_definition():
    rk = RockDefinition("RK_CLIFF_01", rock_type=RockType.CLIFF, asset_variants=["/Game/Rocks/SM_Cliff.uasset"])
    assert rk.rock_type == RockType.CLIFF
    assert len(rk.asset_variants) == 1


def test_rock_scatter():
    b = WorldBounds(-2000.0, 2000.0, -2000.0, 2000.0, 0.0, 500.0)
    prof = VegetationScatterProfile(seed=444)
    insts = UniversalWorldFabricator.scatter_assets(b, prof, "SM_Boulder", max_count=10)
    assert len(insts) == 10


def test_rock_orientation():
    rk = RockDefinition("RK_SURF", orientation=RockOrientation.SURFACE_ALIGNED)
    assert rk.orientation == RockOrientation.SURFACE_ALIGNED


def test_cliff_generation():
    rk = RockDefinition("RK_OUTCROP", rock_type=RockType.OUTCROP, scale_range=(2.0, 5.0))
    assert rk.scale_range == (2.0, 5.0)


def test_rock_determinism():
    rk1 = RockDefinition("RK_DET", RockType.PEBBLE)
    rk2 = RockDefinition("RK_DET", RockType.PEBBLE)
    assert rk1.to_dict() == rk2.to_dict()
