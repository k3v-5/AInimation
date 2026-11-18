"""
Tests for World Partition & Streaming System (UAF-81.56 Section 197).
"""

import pytest
from uaf.universal_world import (
    WorldPartitionProfile,
    WorldPartitionCell,
    LevelStreamingMode,
    StreamingState,
    WorldBounds,
    UniversalWorldFabricator,
)


def test_world_partition():
    wp = WorldPartitionProfile(grid_size=10000.0, streaming_mode=LevelStreamingMode.DISTANCE)
    assert wp.grid_size == 10000.0
    assert wp.streaming_mode == LevelStreamingMode.DISTANCE


def test_cell_assignment():
    world = UniversalWorldFabricator.create_base_world("W_PART", "Partition World", grid_cells=3)
    assert len(world.partition.cells) == 9
    assert world.partition.cells[0].cell_id == "CELL_0_0"


def test_streaming_distance():
    b = WorldBounds()
    cell = WorldPartitionCell("CELL_TEST", b, load_distance=20000.0, unload_distance=25000.0)
    assert cell.load_distance == 20000.0
    assert cell.unload_distance == 25000.0


def test_streaming_priority():
    b = WorldBounds()
    cell = WorldPartitionCell("CELL_PRIO", b, priority=5)
    assert cell.priority == 5


def test_streaming_state():
    b = WorldBounds()
    cell = WorldPartitionCell("CELL_STATE", b, runtime_state=StreamingState.VISIBLE)
    assert cell.runtime_state == StreamingState.VISIBLE


def test_streaming_determinism():
    w1 = UniversalWorldFabricator.create_base_world("W1", "Part Det", seed=888, grid_cells=2)
    w2 = UniversalWorldFabricator.create_base_world("W1", "Part Det", seed=888, grid_cells=2)
    assert w1.partition.to_dict() == w2.partition.to_dict()
