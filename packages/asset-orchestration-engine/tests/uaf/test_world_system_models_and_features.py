"""
Tests for World System Models, World Bounds, Water, Roads, and Districts.
UAF-81.16 Sections 3, 4, 8, 39, 40, 175.
"""

from uaf.world_system.models.world_def import WorldBounds, WorldDefinition
from uaf.world_system.models.features import (
    WaterBodyType,
    WaterBody,
    RoadNetwork,
    DistrictType,
    WorldDistrict,
    GameplayZone,
)


def test_world_bounds_and_definition_hash():
    bounds = WorldBounds(min_x=-500.0, max_x=500.0, min_y=-500.0, max_y=500.0, min_z=0.0, max_z=200.0)
    assert bounds.area_m2 == 1000000.0

    w_def = WorldDefinition(world_id="World_Valleys", seed=54321, bounds=bounds)
    assert len(w_def.definition_hash) == 64
    data = w_def.to_dict()
    assert data["bounds"]["area_m2"] == 1000000.0


def test_features_and_zones():
    lake = WaterBody("WB_Lake", WaterBodyType.LAKE, surface_elevation_m=20.0, area_m2=25000.0)
    assert lake.water_type == "LAKE"

    road = RoadNetwork("RN_Main", total_length_m=5000.0, segment_count=20, has_bridges=True)
    assert road.has_bridges is True

    dist = WorldDistrict("Dist_IndustrialZone", DistrictType.INDUSTRIAL, 10, 50)
    assert dist.district_type == "INDUSTRIAL"

    zone = GameplayZone("Zone_Alpha", player_spawns=2, objectives=1, combat_arenas=1, is_reachable=True)
    assert zone.is_reachable is True
