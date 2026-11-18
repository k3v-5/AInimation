"""
RoomType, RoomNode, and BuildingFacilityGraph models.
UAF-81.12 Sections 22, 23, 24, 27, 28, 29.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class RoomType(str, Enum):
    CORRIDOR = "CORRIDOR"
    HALL = "HALL"
    OFFICE = "OFFICE"
    STORAGE = "STORAGE"
    LAB = "LAB"
    WAREHOUSE = "WAREHOUSE"
    ARMORY = "ARMORY"
    CONTROL_ROOM = "CONTROL_ROOM"
    SERVER_ROOM = "SERVER_ROOM"
    LIVING = "LIVING"
    MEDICAL = "MEDICAL"
    SECURITY = "SECURITY"
    UTILITY = "UTILITY"
    BOSS_ROOM = "BOSS_ROOM"
    ARENA = "ARENA"
    OUTDOOR = "OUTDOOR"


@dataclass
class RoomNode:
    room_id: str
    room_type: RoomType
    dimensions: List[float] = field(default_factory=lambda: [10.0, 10.0, 3.0])  # width, length, height
    floor_index: int = 0
    connections: List[str] = field(default_factory=list)  # connected room_ids
    spawns_count: int = 1
    has_objective: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "room_type": self.room_type.value,
            "dimensions": self.dimensions,
            "floor_index": self.floor_index,
            "connections": self.connections,
            "spawns_count": self.spawns_count,
            "has_objective": self.has_objective,
        }


@dataclass
class BuildingFacilityGraph:
    facility_id: str
    floors_count: int = 1
    rooms: Dict[str, RoomNode] = field(default_factory=dict)
    vertical_connections: List[str] = field(default_factory=list)  # e.g. "Stairs_F0_F1"

    def add_room(self, room: RoomNode) -> None:
        self.rooms[room.room_id] = room

    def connect_rooms(self, room_a: str, room_b: str) -> None:
        if room_a in self.rooms and room_b in self.rooms:
            if room_b not in self.rooms[room_a].connections:
                self.rooms[room_a].connections.append(room_b)
            if room_a not in self.rooms[room_b].connections:
                self.rooms[room_b].connections.append(room_a)

    def is_fully_connected(self) -> bool:
        """Verifies reachability of all rooms via Breadth-First Search (Section 204)."""
        if not self.rooms:
            return False
        start = next(iter(self.rooms.keys()))
        visited = set([start])
        queue = [start]
        while queue:
            curr = queue.pop(0)
            for neighbor in self.rooms[curr].connections:
                if neighbor not in visited and neighbor in self.rooms:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return len(visited) == len(self.rooms)

    @property
    def graph_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "facility_id": self.facility_id,
            "floors_count": self.floors_count,
            "rooms": {k: v.to_dict() for k, v in sorted(self.rooms.items())},
            "vertical_connections": self.vertical_connections,
        }
