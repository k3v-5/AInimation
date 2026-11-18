"""
Tests for World HLOD Profile & Aggregation (UAF-81.56 Section 198).
"""

import pytest
from uaf.universal_world import (
    WorldHLODProfile,
    HLODLevel,
    HLODGroupingMode,
    TriangleBudget,
    UniversalWorldFabricator,
)


def test_hlod_profile():
    hlod = WorldHLODProfile()
    assert len(hlod.levels) == 3
    assert HLODLevel.HLOD0 in hlod.levels
    assert hlod.reduction_per_level == 0.5


def test_hlod_grouping():
    hlod = WorldHLODProfile(grouping_mode=HLODGroupingMode.CELL)
    assert hlod.grouping_mode == HLODGroupingMode.CELL


def test_hlod_generation():
    world = UniversalWorldFabricator.create_base_world("W_HLOD", "HLOD World")
    assert world.hlod is not None
    assert world.hlod.max_draw_distance == 50000.0


def test_hlod_bounds():
    world = UniversalWorldFabricator.create_base_world("W_HLOD_B", "HLOD Bounds")
    assert world.bounds.size_x > 0.0


def test_hlod_materials():
    hlod = WorldHLODProfile(grouping_mode=HLODGroupingMode.MATERIAL)
    assert hlod.grouping_mode == HLODGroupingMode.MATERIAL


def test_hlod_transition():
    hlod = WorldHLODProfile(max_draw_distance=60000.0)
    assert hlod.max_draw_distance == 60000.0


def test_hlod_budget():
    tb = TriangleBudget(hlod=500000)
    assert tb.hlod == 500000
