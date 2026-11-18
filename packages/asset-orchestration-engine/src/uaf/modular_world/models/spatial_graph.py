"""
RoomPurpose, EnvironmentRoom, SpatialConnection, and SpatialLayoutGraph models.
UAF-81.19 Sections 22, 23, 24, 25, 26, 27, 28, 29, 32, 163, 164.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from collections import deque


class RoomPurpose(str, Enum):
    COMBAT = "COMBAT"
    LOOT = "LOOT"
    TRANSITION = "TRANSITION"
    STORAGE = "STORAGE"
    OBJECTIVE = "OBJECTIVE"
    SPAWN = "SPAWN"
    BOSS = "BOSS"
    PUZZLE = "PUZZLE"
    SAFE = "SAFE"
    CINEMATIC = "CINEMATIC"


@dataclass
class EnvironmentRoom:
    room_id: str
    purpose: RoomPurpose
    dimensions_xyz: List[float] = field(default_factory=lambda: [800.0, 800.0, 300.0])  # cm
    floor_level: int = 0
    is_accessible: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "purpose": self.purpose.value,
            "dimensions_xyz": self.dimensions_xyz,
            "floor_level": self.floor_level,
            "is_accessible": self.is_accessible,
        }


@dataclass
class SpatialConnection:
    from_room: str
    to_room: str
    connection_type: str = "CORRIDOR"  # "CORRIDOR", "DOORWAY", "STAIR", "ELEVATOR"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_room": self.from_room,
            "to_room": self.to_room,
            "connection_type": self.connection_type,
        }


@dataclass
class SpatialLayoutGraph:
    rooms: Dict[str, EnvironmentRoom] = field(default_factory=dict)
    connections: List[SpatialConnection] = field(default_factory=list)

    def add_room(self, room: EnvironmentRoom) -> None:
        self.rooms[room.room_id] = room

    def add_connection(self, from_id: str, to_id: str, conn_type: str = "CORRIDOR") -> None:
        self.connections.append(SpatialConnection(from_id, to_id, conn_type))

    def is_fully_connected(self) -> bool:
        """Verifies using BFS that all registered rooms can be reached from the first room."""
        if not self.rooms:
            return True
        if len(self.rooms) == 1:
            return True

        adj: Dict[str, List[str]] = {r: [] for r in self.rooms}
        for conn in self.connections:
            if conn.from_room in adj and conn.to_room in adj:
                adj[conn.from_room].append(conn.to_room)
                adj[conn.to_room].append(conn.from_room)

        start_room = next(iter(self.rooms))
        visited = set([start_room])
        queue = deque([start_room])

        while queue:
            curr = queue.popleft()
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == len(self.rooms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rooms": {k: v.to_dict() for k, v in sorted(self.rooms.items())},
            "connections": [c.to_dict() for c in self.connections],
            "is_fully_connected": self.is_fully_connected(),
        }
