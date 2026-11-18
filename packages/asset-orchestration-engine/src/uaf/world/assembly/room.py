"""
RoomDefinition and RoomType models for structural layout and gameplay zoning.
UAF-81.6 Sections 16, 17, 18.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class RoomType(str, Enum):
    CORRIDOR = "CORRIDOR"
    HALL = "HALL"
    ROOM = "ROOM"
    OFFICE = "OFFICE"
    WAREHOUSE = "WAREHOUSE"
    ARENA = "ARENA"
    BOSS_ROOM = "BOSS_ROOM"
    SPAWN_ROOM = "SPAWN_ROOM"
    OBJECTIVE_ROOM = "OBJECTIVE_ROOM"
    TRANSITION = "TRANSITION"


@dataclass
class RoomDefinition:
    room_id: str
    room_type: RoomType
    dimensions: List[float] = field(default_factory=lambda: [10.0, 10.0, 3.0])  # Width, Depth, Height
    center_position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    entrances: List[str] = field(default_factory=list)
    exits: List[str] = field(default_factory=list)
    module_instances: List[str] = field(default_factory=list)
    gameplay_role: str = "COMBAT"  # "SPAWN", "COMBAT", "OBJECTIVE", "TRANSITION"
    connected_rooms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "room_type": self.room_type.value,
            "dimensions": self.dimensions,
            "center_position": self.center_position,
            "entrances": self.entrances,
            "exits": self.exits,
            "module_instances": self.module_instances,
            "gameplay_role": self.gameplay_role,
            "connected_rooms": self.connected_rooms,
        }
