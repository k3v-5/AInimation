"""
BlockoutZoneNode and BlockoutWorldGraph models.
UAF-81.28 Sections 25, 26, 27, 40, 41, 42, 43, 124.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from collections import deque


@dataclass
class BlockoutZoneNode:
    zone_id: str
    zone_name: str
    dimensions_xyz: List[float] = field(default_factory=lambda: [1200.0, 1200.0, 400.0])  # cm
    is_critical_path: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "dimensions_xyz": self.dimensions_xyz,
            "is_critical_path": self.is_critical_path,
        }


@dataclass
class BlockoutWorldGraph:
    zones: Dict[str, BlockoutZoneNode] = field(default_factory=dict)
    connections: List[Tuple[str, str, str]] = field(default_factory=list)  # (from_zone, to_zone, connection_type)

    def add_zone(self, zone: BlockoutZoneNode) -> None:
        self.zones[zone.zone_id] = zone

    def add_connection(self, from_id: str, to_id: str, conn_type: str = "CORRIDOR") -> None:
        self.connections.append((from_id, to_id, conn_type))

    def _build_adj_list(self) -> Dict[str, List[str]]:
        adj: Dict[str, List[str]] = {z: [] for z in self.zones}
        for u, v, _ in self.connections:
            if u in adj and v in adj:
                adj[u].append(v)
                adj[v].append(u)
        return adj

    def is_fully_connected(self) -> bool:
        if not self.zones:
            return True
        if len(self.zones) == 1:
            return True

        adj = self._build_adj_list()
        start = next(iter(self.zones))
        visited = set([start])
        queue = deque([start])

        while queue:
            curr = queue.popleft()
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == len(self.zones)

    def is_critical_path_connected(self) -> bool:
        crit_zones = [z for z, node in self.zones.items() if node.is_critical_path]
        if not crit_zones:
            return True
        if len(crit_zones) == 1:
            return True

        adj = self._build_adj_list()
        start = crit_zones[0]
        visited = set([start])
        queue = deque([start])

        while queue:
            curr = queue.popleft()
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return all(z in visited for z in crit_zones)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zones": {k: v.to_dict() for k, v in sorted(self.zones.items())},
            "connections": [{"from": u, "to": v, "type": t} for u, v, t in self.connections],
            "is_fully_connected": self.is_fully_connected(),
            "is_critical_path_connected": self.is_critical_path_connected(),
        }
