"""
Tests for Road, Path & Bridge System (UAF-81.56 Section 194).
"""

import pytest
from uaf.universal_world import (
    RoadDefinition,
    RoadType,
    RoadCutFillMode,
    BridgeDefinition,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_road_definition():
    rd = RoadDefinition("RD_01", RoadType.HIGHWAY, width=1200.0)
    assert rd.road_id == "RD_01"
    assert rd.road_type == RoadType.HIGHWAY
    assert rd.width == 1200.0


def test_road_path():
    rd = UniversalWorldFabricator.generate_road("RD_PATH", RoadType.ROAD)
    assert len(rd.control_points) >= 3


def test_road_generation():
    rd = UniversalWorldFabricator.generate_road("RD_GEN", RoadType.STREET, width=800.0)
    assert rd.road_type == RoadType.STREET
    assert rd.width == 800.0


def test_road_cut():
    rd = RoadDefinition("RD_CUT", cut_fill_mode=RoadCutFillMode.CUT)
    assert rd.cut_fill_mode == RoadCutFillMode.CUT


def test_road_fill():
    rd = RoadDefinition("RD_FILL", cut_fill_mode=RoadCutFillMode.FILL)
    assert rd.cut_fill_mode == RoadCutFillMode.FILL


def test_bridge():
    br = BridgeDefinition("BR_01", start=(0.0, 0.0, 100.0), end=(2000.0, 0.0, 100.0), span=2000.0)
    assert br.span == 2000.0
    assert br.height == 500.0


def test_road_validation():
    world = UniversalWorldFabricator.create_base_world("W_RD_VAL", "Road Val")
    world.roads[0].slope_limit = 50.0  # Exceeds standard limit
    report = UniversalWorldValidator.validate_world(world)
    assert any("slope limit" in w.lower() for w in report.warnings)


def test_road_determinism():
    rd1 = UniversalWorldFabricator.generate_road("RD_DET")
    rd2 = UniversalWorldFabricator.generate_road("RD_DET")
    assert rd1.to_dict() == rd2.to_dict()
