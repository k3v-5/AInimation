"""
Tests for Building & Architecture System (UAF-81.56 Section 193).
"""

import pytest
from uaf.universal_world import (
    BuildingDefinition,
    BuildingType,
    UniversalWorldFabricator,
    UniversalWorldValidator,
)


def test_building_definition():
    b = BuildingDefinition("BLD_HOUSE_01", BuildingType.HOUSE, floors=2, height=600.0)
    assert b.building_id == "BLD_HOUSE_01"
    assert b.building_type == BuildingType.HOUSE
    assert b.floors == 2
    assert b.height == 600.0


def test_building_footprint():
    b = UniversalWorldFabricator.generate_building("BLD_FP", BuildingType.WAREHOUSE)
    assert len(b.footprint) >= 3  # Polygon with at least 3 vertices


def test_building_generation():
    b = UniversalWorldFabricator.generate_building("BLD_GEN", BuildingType.OFFICE, floors=5, height_per_floor=350.0)
    assert b.floors == 5
    assert b.height == 1750.0
    assert b.roof_type == "FLAT"


def test_building_variation():
    b1 = BuildingDefinition("B1", variation=1)
    b2 = BuildingDefinition("B2", variation=2)
    assert b1.variation != b2.variation


def test_building_validation():
    world = UniversalWorldFabricator.create_base_world("W_BLD_VAL", "Bld Val")
    # Corrupt building floors
    world.structures[0].floors = 0
    report = UniversalWorldValidator.validate_world(world)
    assert report.is_valid is False
    assert any("floors" in f.lower() for f in report.failed_checks)


def test_building_determinism():
    b1 = UniversalWorldFabricator.generate_building("BLD_DET", BuildingType.HOUSE, floors=3)
    b2 = UniversalWorldFabricator.generate_building("BLD_DET", BuildingType.HOUSE, floors=3)
    assert b1.to_dict() == b2.to_dict()
