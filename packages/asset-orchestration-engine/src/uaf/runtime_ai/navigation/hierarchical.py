"""
UAF-81.82: Hierarchical Pathfinding (HPA*) for Large-Scale Worlds.
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Set, Tuple

from ..models.definition import (
    NavigationProfile,
    PathResult,
    PathStatus,
    Vec3,
    vec3_distance,
)
from .astar import AStarPathfinder
from .funnel import FunnelAlgorithm
from .mesh import NavMesh
from .tile import NavTile


class HierarchicalPathfinder:
    """
    Hierarchical path planning across spatial clusters / navigation tiles.
    Abstract graph search finds the cluster corridor; local A* and Funnel resolve
    the detailed geometry within active tiles.
    """

    def __init__(self):
        self._tile_connections: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}

    def connect_tiles(self, tile_a: Tuple[int, int], tile_b: Tuple[int, int]) -> None:
        """Register bidirectional connectivity between two spatial navigation tiles."""
        self._tile_connections.setdefault(tile_a, set()).add(tile_b)
        self._tile_connections.setdefault(tile_b, set()).add(tile_a)

    def find_abstract_path(
        self,
        start_tile: Tuple[int, int],
        goal_tile: Tuple[int, int],
    ) -> Optional[List[Tuple[int, int]]]:
        """A* on abstract tile connectivity graph."""
        if start_tile == goal_tile:
            return [start_tile]

        open_heap: List[Tuple[float, float, Tuple[int, int]]] = []
        h_start = math_manhattan_dist(start_tile, goal_tile)
        heapq.heappush(open_heap, (h_start, 0.0, start_tile))

        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_scores: Dict[Tuple[int, int], float] = {start_tile: 0.0}
        closed_set: Set[Tuple[int, int]] = set()

        found = False
        while open_heap:
            f, g, curr = heapq.heappop(open_heap)
            if curr in closed_set:
                continue
            closed_set.add(curr)

            if curr == goal_tile:
                found = True
                break

            neighbors = sorted(self._tile_connections.get(curr, set()))
            for n in neighbors:
                if n in closed_set:
                    continue
                step_cost = 1.0
                tentative_g = g + step_cost
                if tentative_g < g_scores.get(n, float("inf")):
                    came_from[n] = curr
                    g_scores[n] = tentative_g
                    h = math_manhattan_dist(n, goal_tile)
                    heapq.heappush(open_heap, (tentative_g + h, tentative_g, n))

        if not found:
            return None

        path = []
        curr = goal_tile
        while curr in came_from:
            path.append(curr)
            curr = came_from[curr]
        path.append(start_tile)
        path.reverse()
        return path


def math_manhattan_dist(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))
