"""
Tests for Water System (UAF-81.56 Section 189).
"""

import pytest
from uaf.universal_world import (
    WaterDefinition,
    WaterBody,
    WaterType,
    RiverDefinition,
    FlowField,
    ShorelineDefinition,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_water_definition():
    w = UniversalWorldFabricator.generate_water("TEST_W", WaterType.LAKE)
    assert len(w.water_bodies) == 1
    assert len(w.rivers) == 1
    assert len(w.flow_fields) == 1
    assert len(w.shorelines) == 1


def test_ocean():
    w = UniversalWorldFabricator.generate_water("OCEAN_01", WaterType.OCEAN, surface_level=0.0)
    assert w.water_bodies[0].water_type == WaterType.OCEAN
    assert w.water_bodies[0].surface_level == 0.0


def test_lake():
    w = UniversalWorldFabricator.generate_water("LAKE_01", WaterType.LAKE, surface_level=500.0)
    assert w.water_bodies[0].water_type == WaterType.LAKE
    assert w.water_bodies[0].surface_level == 500.0


def test_river():
    riv = RiverDefinition("RIV_01", source=(0.0, 0.0, 100.0), destination=(1000.0, 0.0, 0.0), width=400.0)
    assert riv.width == 400.0
    assert riv.source[2] > riv.destination[2]


def test_stream():
    riv = RiverDefinition("STREAM_01", source=(0.0, 0.0, 50.0), destination=(500.0, 0.0, 10.0), width=100.0, flow=0.5)
    assert riv.width == 100.0


def test_waterfall():
    # Steep river segment constitutes waterfall
    riv = RiverDefinition("FALL_01", source=(0.0, 0.0, 1000.0), destination=(10.0, 0.0, 100.0), slope=0.9)
    assert riv.slope > 0.5


def test_flow_field():
    ff = FlowField("FF_01", resolution_x=8, resolution_y=8, vectors=[(0.0, 1.0)] * 64)
    assert len(ff.vectors) == 64
    assert ff.speed == 1.0


def test_shoreline():
    sh = ShorelineDefinition("SHORE_01", "WB_01", points=[(0.0, 0.0, 0.0), (100.0, 100.0, 0.0)], width=150.0)
    assert sh.width == 150.0
    assert len(sh.points) == 2


def test_water_validation():
    world = UniversalWorldFabricator.create_base_world("W_WATER_VAL", "Water Val")
    # Make river flow uphill to trigger hard fail
    world.water.rivers[0].source = (0.0, 0.0, 10.0)
    world.water.rivers[0].destination = (100.0, 0.0, 200.0)
    report = UniversalWorldValidator.validate_world(world)
    assert report.is_valid is False
    assert any("flows uphill" in f.lower() for f in report.failed_checks)
