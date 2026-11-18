"""
NavigationMeshMetadata models walkable graphs and path reachability guarantees.
UAF-81.6 Sections 19, 20, 21, 104.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any


@dataclass
class NavigationMeshMetadata:
    waypoints: Dict[str, List[float]] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    walkable_area_sqm: float = 0.0

    def add_waypoint(self, wp_id: str, position: List[float]) -> None:
        self.waypoints[wp_id] = position

    def add_edge(self, wp_a: str, wp_b: str) -> None:
        if (wp_a, wp_b) not in self.edges and (wp_b, wp_a) not in self.edges:
            self.edges.append((wp_a, wp_b))

    def has_path(self, start_wp: str, target_wp: str) -> bool:
        """
        BFS reachability check.
        CRITICAL INVARIANT (Section 21): Guarantees gameplay paths exist before validation.
        """
        if start_wp not in self.waypoints or target_wp not in self.waypoints:
            return False
        if start_wp == target_wp:
            return True

        # Build adjacency list
        adj: Dict[str, List[str]] = {k: [] for k in self.waypoints}
        for a, b in self.edges:
            if a in adj and b in adj:
                adj[a].append(b)
                adj[b].append(a)

        visited: Set[str] = {start_wp}
        queue = [start_wp]

        while queue:
            curr = queue.pop(0)
            if curr == target_wp:
                return True
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "waypoints": self.waypoints,
            "edges": [list(e) for e in self.edges],
            "walkable_area_sqm": self.walkable_area_sqm,
        }
