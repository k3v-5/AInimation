"""
WaterBody, RoadNetwork, WorldDistrict, and GameplayZone models.
UAF-81.16 Sections 39, 40, 175, 176, 177, 235, 236.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class WaterBodyType(str, Enum):
    OCEAN = "OCEAN"
    LAKE = "LAKE"
    RIVER = "RIVER"
    STREAM = "STREAM"
    POND = "POND"
    WATERFALL = "WATERFALL"


@dataclass
class WaterBody:
    body_id: str
    water_type: WaterBodyType
    surface_elevation_m: float = 12.0
    area_m2: float = 50000.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body_id": self.body_id,
            "water_type": self.water_type.value,
            "surface_elevation_m": self.surface_elevation_m,
            "area_m2": self.area_m2,
        }


@dataclass
class RoadNetwork:
    network_id: str
    total_length_m: float = 3500.0
    segment_count: int = 24
    has_bridges: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "network_id": self.network_id,
            "total_length_m": self.total_length_m,
            "segment_count": self.segment_count,
            "has_bridges": self.has_bridges,
        }


class DistrictType(str, Enum):
    ABANDONED = "ABANDONED"
    MILITARY = "MILITARY"
    CIVILIAN = "CIVILIAN"
    INDUSTRIAL = "INDUSTRIAL"
    RITUAL = "RITUAL"
    ALIEN = "ALIEN"


@dataclass
class WorldDistrict:
    district_id: str
    district_type: DistrictType
    building_count: int = 8
    prop_count: int = 64

    def to_dict(self) -> Dict[str, Any]:
        return {
            "district_id": self.district_id,
            "district_type": self.district_type.value,
            "building_count": self.building_count,
            "prop_count": self.prop_count,
        }


@dataclass
class GameplayZone:
    zone_id: str
    player_spawns: int = 1
    objectives: int = 1
    combat_arenas: int = 1
    is_reachable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "player_spawns": self.player_spawns,
            "objectives": self.objectives,
            "combat_arenas": self.combat_arenas,
            "is_reachable": self.is_reachable,
        }
