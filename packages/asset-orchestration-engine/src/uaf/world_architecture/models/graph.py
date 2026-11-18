"""
ArchitecturalZoneType, ArchitecturalRoomNode, and ArchitecturalWorldGraph models.
UAF-81.24 Sections 70, 71, 72, 73, 74, 171, 172, 173.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from collections import deque


class ArchitecturalZoneType(str, Enum):
    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"
    CORRIDOR = "CORRIDOR"
    ARENA = "ARENA"
    PLAZA = "PLAZA"
    VERTICAL_TRANSITION = "VERTICAL_TRANSITION"
    CRITICAL_PATH = "CRITICAL_PATH"
    OPTIONAL_ZONE = "OPTIONAL_ZONE"


@dataclass
class ArchitecturalRoomNode:
    room_id: str
    zone_type: ArchitecturalZoneType
    dimensions_xyz: List[float] = field(default_factory=lambda: [1000.0, 1000.0, 400.0])  # cm
    floor_level: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "zone_type": self.zone_type.value,
            "dimensions_xyz": self.dimensions_xyz,
            "floor_level": self.floor_level,
        }


@dataclass
class ArchitecturalWorldGraph:
    rooms: Dict[str, ArchitecturalRoomNode] = field(default_factory=dict)
    connections: List[Tuple[str, str, str]] = field(default_factory=list)  # (from, to, type)

    def add_room(self, room: ArchitecturalRoomNode) -> None:
        self.rooms[room.room_id] = room

    def add_connection(self, from_id: str, to_id: str, conn_type: str = "DOORWAY") -> None:
        self.connections.append((from_id, to_id, conn_type))

    def _build_adj_list(self) -> Dict[str, List[str]]:
        adj: Dict[str, List[str]] = {r: [] for r in self.rooms}
        for u, v, _ in self.connections:
            if u in adj and v in adj:
                adj[u].append(v)
                adj[v].append(u)
        return adj

    def is_fully_connected(self) -> bool:
        if not self.rooms:
            return True
        if len(self.rooms) == 1:
            return True

        adj = self._build_adj_list()
        start = next(iter(self.rooms))
        visited = set([start])
        queue = deque([start])

        while queue:
            curr = queue.popleft()
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == len(self.rooms)

    def is_critical_path_valid(self) -> bool:
        """Verifies that all CRITICAL_PATH rooms are interconnected and accessible."""
        crit_rooms = [r for r, node in self.rooms.items() if node.zone_type == ArchitecturalZoneType.CRITICAL_PATH]
        if not crit_rooms:
            return True
        if len(crit_rooms) == 1:
            return True

        adj = self._build_adj_list()
        start = crit_rooms[0]
        visited = set([start])
        queue = deque([start])

        while queue:
            curr = queue.popleft()
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return all(r in visited for r in crit_rooms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rooms": {k: v.to_dict() for k, v in sorted(self.rooms.items())},
            "connections": [{"from": u, "to": v, "type": t} for u, v, t in self.connections],
            "is_fully_connected": self.is_fully_connected(),
            "critical_path_valid": self.is_critical_path_valid(),
        }
