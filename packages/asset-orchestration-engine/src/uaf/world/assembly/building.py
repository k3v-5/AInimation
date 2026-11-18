"""
BuildingDefinition models multi-floor structures and vertical traversal networks.
UAF-81.6 Sections 23, 24, 25.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .room import RoomDefinition


@dataclass
class BuildingDefinition:
    building_id: str
    footprint: List[float] = field(default_factory=lambda: [20.0, 20.0])  # Width, Depth
    floors_count: int = 2
    floor_height_meters: float = 3.0
    rooms: List[RoomDefinition] = field(default_factory=list)
    stair_instances: List[str] = field(default_factory=list)
    entrance_positions: List[List[float]] = field(default_factory=list)

    @property
    def total_height_meters(self) -> float:
        return self.floors_count * self.floor_height_meters

    def get_rooms_on_floor(self, floor_index: int) -> List[RoomDefinition]:
        min_z = floor_index * self.floor_height_meters
        max_z = (floor_index + 1) * self.floor_height_meters
        return [r for r in self.rooms if min_z <= r.center_position[2] < max_z]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "building_id": self.building_id,
            "footprint": self.footprint,
            "floors_count": self.floors_count,
            "floor_height_meters": self.floor_height_meters,
            "total_height_meters": self.total_height_meters,
            "rooms": [r.to_dict() for r in self.rooms],
            "stair_instances": self.stair_instances,
            "entrance_positions": self.entrance_positions,
        }
