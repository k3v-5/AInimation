"""
UAF-81.90: Level Topology Graph, Connectivity Topologies, and Pathfinding.
Extracts mathematical graph models from modular tile layouts, verifies critical paths (A*/BFS),
and identifies circulation loops and bottlenecks.
"""

from __future__ import annotations

import heapq
from collections import deque
from typing import Dict, List, Optional, Set, Tuple, Any

from uaf.level_design.core.contracts import (
    Direction2D,
    Direction3D,
    DIR_OFFSETS_2D,
    DIR_OFFSETS_3D,
    SocketType,
    RoomType,
    PlacedTile,
    ModularTileDefinition,
)


class TopologyNode:
    """Represents a discrete tile node in the level topology graph."""

    def __init__(
        self,
        coord: Tuple[int, ...],
        tile: PlacedTile,
        tile_def: Optional[ModularTileDefinition] = None,
    ):
        self.coord = coord
        self.tile = tile
        self.tile_def = tile_def
        self.room_type = tile.room_type
        self.neighbors: Set[Tuple[int, ...]] = set()

    def __repr__(self) -> str:
        return f"TopologyNode({self.coord}, type={self.room_type.value})"


class LevelTopologyGraph:
    """
    Graph representation of a level's walkable topology.
    Handles connectivity analysis, critical path computation (BFS/A*),
    and cycle/loop detection.
    """

    PASSABLE_SOCKETS: Set[SocketType] = {
        SocketType.CORRIDOR,
        SocketType.DOOR,
        SocketType.OPEN,
        SocketType.VENT,
    }

    def __init__(self):
        self.nodes: Dict[Tuple[int, ...], TopologyNode] = {}

    @classmethod
    def from_placed_tiles_2d(
        cls,
        tiles: Dict[Tuple[int, int], PlacedTile],
        tile_catalog: Dict[str, ModularTileDefinition],
    ) -> LevelTopologyGraph:
        """Constructs a topology graph from 2D placed tiles and catalog definitions."""
        graph = cls()

        # 1. Create nodes for all placed tiles
        for coord, tile in tiles.items():
            tile_def = tile_catalog.get(tile.tile_id)
            # Only index tiles that are not purely solid wall/void
            graph.nodes[coord] = TopologyNode(coord=coord, tile=tile, tile_def=tile_def)

        # 2. Connect adjacent nodes if both faces have passable sockets
        for (x, y), node in graph.nodes.items():
            if not node.tile_def:
                continue

            for d in Direction2D:
                sock_a = node.tile_def.get_socket_2d(d)
                if sock_a not in cls.PASSABLE_SOCKETS:
                    continue

                dx, dy = DIR_OFFSETS_2D[d]
                neighbor_coord = (x + dx, y + dy)

                if neighbor_coord not in graph.nodes:
                    continue

                neighbor_node = graph.nodes[neighbor_coord]
                if not neighbor_node.tile_def:
                    continue

                from uaf.level_design.core.contracts import OPPOSITE_DIR_2D
                opp_d = OPPOSITE_DIR_2D[d]
                sock_b = neighbor_node.tile_def.get_socket_2d(opp_d)

                if sock_b in cls.PASSABLE_SOCKETS:
                    node.neighbors.add(neighbor_coord)

        return graph

    @classmethod
    def from_placed_tiles_3d(
        cls,
        tiles: Dict[Tuple[int, int, int], PlacedTile],
        tile_catalog: Dict[str, ModularTileDefinition],
    ) -> LevelTopologyGraph:
        """Constructs a topology graph from 3D placed tiles and catalog definitions."""
        graph = cls()

        for coord, tile in tiles.items():
            tile_def = tile_catalog.get(tile.tile_id)
            graph.nodes[coord] = TopologyNode(coord=coord, tile=tile, tile_def=tile_def)

        for (x, y, z), node in graph.nodes.items():
            if not node.tile_def:
                continue

            for d in Direction3D:
                sock_a = node.tile_def.get_socket_3d(d)
                if sock_a not in cls.PASSABLE_SOCKETS:
                    continue

                dx, dy, dz = DIR_OFFSETS_3D[d]
                neighbor_coord = (x + dx, y + dy, z + dz)

                if neighbor_coord not in graph.nodes:
                    continue

                neighbor_node = graph.nodes[neighbor_coord]
                if not neighbor_node.tile_def:
                    continue

                from uaf.level_design.core.contracts import OPPOSITE_DIR_3D
                opp_d = OPPOSITE_DIR_3D[d]
                sock_b = neighbor_node.tile_def.get_socket_3d(opp_d)

                if sock_b in cls.PASSABLE_SOCKETS:
                    node.neighbors.add(neighbor_coord)

        return graph

    def get_connected_components(self) -> List[Set[Tuple[int, ...]]]:
        """Finds all connected walkable components in the topology."""
        visited: Set[Tuple[int, ...]] = set()
        components: List[Set[Tuple[int, ...]]] = []

        for coord in self.nodes:
            # Skip isolated non-walkable solid blocks (0 neighbors)
            if coord in visited:
                continue

            component: Set[Tuple[int, ...]] = set()
            queue = deque([coord])
            visited.add(coord)

            while queue:
                current = queue.popleft()
                component.add(current)
                for neighbor in self.nodes[current].neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

        return components

    def find_nodes_by_type(self, room_type: RoomType) -> List[Tuple[int, ...]]:
        """Returns all node coordinates of a specific RoomType."""
        return [coord for coord, node in self.nodes.items() if node.room_type == room_type]

    def shortest_path_bfs(
        self,
        start: Tuple[int, ...],
        target: Tuple[int, ...],
        blocked_nodes: Optional[Set[Tuple[int, ...]]] = None,
    ) -> Optional[List[Tuple[int, ...]]]:
        """
        Computes the shortest path using Breadth-First Search.
        Returns ordered list of coordinates from start to target, or None if unreachable.
        """
        if start not in self.nodes or target not in self.nodes:
            return None
        if start == target:
            return [start]

        blocked = blocked_nodes or set()
        if start in blocked or target in blocked:
            return None

        queue = deque([(start, [start])])
        visited: Set[Tuple[int, ...]] = {start}

        while queue:
            current, path = queue.popleft()
            if current == target:
                return path

            for neighbor in self.nodes[current].neighbors:
                if neighbor not in visited and neighbor not in blocked:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def shortest_path_astar(
        self,
        start: Tuple[int, ...],
        target: Tuple[int, ...],
        blocked_nodes: Optional[Set[Tuple[int, ...]]] = None,
    ) -> Optional[List[Tuple[int, ...]]]:
        """
        Computes shortest path using A* search with Manhattan distance heuristic.
        """
        if start not in self.nodes or target not in self.nodes:
            return None
        if start == target:
            return [start]

        blocked = blocked_nodes or set()
        if start in blocked or target in blocked:
            return None

        def heuristic(a: Tuple[int, ...], b: Tuple[int, ...]) -> float:
            return sum(abs(v1 - v2) for v1, v2 in zip(a, b))

        # Priority queue stores (f_score, counter, coord, path)
        counter = 0
        frontier: List[Tuple[float, int, Tuple[int, ...], List[Tuple[int, ...]]]] = []
        heapq.heappush(frontier, (0.0, counter, start, [start]))

        g_scores: Dict[Tuple[int, ...], float] = {start: 0.0}

        while frontier:
            f_score, _, current, path = heapq.heappop(frontier)

            if current == target:
                return path

            for neighbor in self.nodes[current].neighbors:
                if neighbor in blocked:
                    continue

                tentative_g = g_scores[current] + 1.0
                if tentative_g < g_scores.get(neighbor, float("inf")):
                    g_scores[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, target)
                    counter += 1
                    heapq.heappush(frontier, (f, counter, neighbor, path + [neighbor]))

        return None

    def detect_cycles(self) -> List[List[Tuple[int, ...]]]:
        """
        Detects circulation loops / cycles in the walkable topology.
        Returns a list of cycle paths (loops) indicating alternate routes and flanks.
        """
        cycles: List[List[Tuple[int, ...]]] = []
        visited: Set[Tuple[int, ...]] = set()

        for start_coord in self.nodes:
            if start_coord in visited:
                continue

            # BFS with parent tracking to detect back edges
            parent_map: Dict[Tuple[int, ...], Optional[Tuple[int, ...]]] = {start_coord: None}
            queue = deque([start_coord])
            visited.add(start_coord)

            while queue:
                u = queue.popleft()
                for v in self.nodes[u].neighbors:
                    if v not in visited:
                        visited.add(v)
                        parent_map[v] = u
                        queue.append(v)
                    elif parent_map[u] != v:
                        # Found a loop! Trace back from u and v to common ancestor
                        cycle = [u, v]
                        cycles.append(cycle)

        return cycles
