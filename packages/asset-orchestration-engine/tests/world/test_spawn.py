"""
Tests for World Spawn System (UAF-81.56 Section 201).
"""

import pytest
from uaf.universal_world import (
    SpawnProfile,
    UniversalWorldFabricator,
)


def test_spawn_profile():
    sp = SpawnProfile("SP_HERO", height_range=(100.0, 500.0), slope_range=(0.0, 15.0))
    assert sp.spawn_id == "SP_HERO"
    assert sp.height_range == (100.0, 500.0)
    assert sp.slope_range == (0.0, 15.0)


def test_spawn_rules():
    sp = SpawnProfile("SP_ENEMY", biome_rules=["DESERT", "SAVANNA"])
    assert "DESERT" in sp.biome_rules
    assert "SAVANNA" in sp.biome_rules


def test_spawn_exclusion():
    sp = SpawnProfile("SP_EXCL", distance_rules=1500.0)
    assert sp.distance_rules == 1500.0


def test_spawn_determinism():
    sp1 = SpawnProfile(seed=1234)
    sp2 = SpawnProfile(seed=1234)
    assert sp1.to_dict() == sp2.to_dict()
