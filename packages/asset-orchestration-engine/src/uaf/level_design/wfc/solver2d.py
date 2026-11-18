"""
UAF-81.90: Wave Function Collapse 2D Solver.
Implements quantum-inspired constraint satisfaction with Shannon entropy selection,
AC-3 arc consistency propagation, backtracking stack, and deterministic seeding.
"""

from __future__ import annotations

import copy
import math
import random
from typing import Dict, List, Optional, Set, Tuple

from uaf.level_design.core.contracts import (
    Direction2D,
    OPPOSITE_DIR_2D,
    DIR_OFFSETS_2D,
    SocketType,
    are_sockets_compatible,
    RoomType,
    ModularTileDefinition,
    PlacedTile,
)


class WFCContradictionError(Exception):
    """Raised when WFC reaches an unresolvable contradiction."""
    pass


class WaveFunctionCollapse2D:
    """
    2D Wave Function Collapse solver.
    Operates on a discrete (width x height) grid of modular tiles.
    """

    def __init__(
        self,
        width: int,
        height: int,
        tile_catalog: List[ModularTileDefinition],
        seed: Optional[int] = 42,
        tile_size_meters: float = 4.0,
        max_backtracks: int = 200,
    ):
        if width <= 0 or height <= 0:
            raise ValueError(f"Grid dimensions must be positive, got {width}x{height}")
        if not tile_catalog:
            raise ValueError("tile_catalog cannot be empty")

        self.width = width
        self.height = height
        self.tile_catalog: Dict[str, ModularTileDefinition] = {t.tile_id: t for t in tile_catalog}
        self.seed = seed
        self.rng = random.Random(seed)
        self.tile_size_meters = tile_size_meters
        self.max_backtracks = max_backtracks

        # Precompute socket compatibility index:
        # cache[direction][tile_id] -> set of allowed neighbor tile_ids
        self._allowed_neighbors: Dict[Direction2D, Dict[str, Set[str]]] = {
            d: {tid: set() for tid in self.tile_catalog} for d in Direction2D
        }
        self._precompute_adjacency()

        # Grid state: (x, y) -> Set[str] of candidate tile_ids
        self.grid: Dict[Tuple[int, int], Set[str]] = {}
        self._init_grid()

    def _precompute_adjacency(self) -> None:
        """Precomputes compatible neighbor tile sets for each direction."""
        for d in Direction2D:
            opp_d = OPPOSITE_DIR_2D[d]
            for tid_a, tile_a in self.tile_catalog.items():
                sock_a = tile_a.get_socket_2d(d)
                for tid_b, tile_b in self.tile_catalog.items():
                    sock_b = tile_b.get_socket_2d(opp_d)
                    if are_sockets_compatible(sock_a, sock_b):
                        self._allowed_neighbors[d][tid_a].add(tid_b)

    def _init_grid(self) -> None:
        """Initializes all grid cells with all tile candidates."""
        all_tile_ids = set(self.tile_catalog.keys())
        self.grid = {(x, y): set(all_tile_ids) for x in range(self.width) for y in range(self.height)}

    def constrain_cell(self, x: int, y: int, allowed_tile_ids: Set[str]) -> bool:
        """
        Manually constrains a cell to a subset of tile IDs (e.g. for fixed entrance/exit or boundary).
        Propagates constraints immediately.
        """
        if (x, y) not in self.grid:
            raise IndexError(f"Cell ({x}, {y}) out of grid bounds")

        current = self.grid[(x, y)]
        narrowed = current.intersection(allowed_tile_ids)
        if not narrowed:
            return False

        if narrowed != current:
            self.grid[(x, y)] = narrowed
            return self._propagate([(x, y)])
        return True

    def constrain_boundaries(self, required_socket: SocketType = SocketType.WALL) -> bool:
        """
        Constrains outer edges of the grid so that outer-facing sockets must match required_socket (default: WALL).
        """
        queue: List[Tuple[int, int]] = []
        for x in range(self.width):
            for y in range(self.height):
                valid_candidates = set(self.grid[(x, y)])
                # Check North boundary (y == height - 1)
                if y == self.height - 1:
                    valid_candidates = {tid for tid in valid_candidates if self.tile_catalog[tid].get_socket_2d(Direction2D.NORTH) == required_socket}
                # Check South boundary (y == 0)
                if y == 0:
                    valid_candidates = {tid for tid in valid_candidates if self.tile_catalog[tid].get_socket_2d(Direction2D.SOUTH) == required_socket}
                # Check West boundary (x == 0)
                if x == 0:
                    valid_candidates = {tid for tid in valid_candidates if self.tile_catalog[tid].get_socket_2d(Direction2D.WEST) == required_socket}
                # Check East boundary (x == width - 1)
                if x == self.width - 1:
                    valid_candidates = {tid for tid in valid_candidates if self.tile_catalog[tid].get_socket_2d(Direction2D.EAST) == required_socket}

                if len(valid_candidates) < len(self.grid[(x, y)]):
                    if not valid_candidates:
                        return False
                    self.grid[(x, y)] = valid_candidates
                    queue.append((x, y))

        return self._propagate(queue)

    def _compute_entropy(self, candidates: Set[str]) -> float:
        """
        Computes Shannon entropy:
        H = log(sum(w)) - (sum(w * log(w)) / sum(w))
        Adds a slight deterministic jitter based on tile IDs for consistent tie-breaking.
        """
        if len(candidates) <= 1:
            return 0.0

        total_weight = 0.0
        sum_w_log_w = 0.0
        for tid in candidates:
            w = self.tile_catalog[tid].weight
            total_weight += w
            sum_w_log_w += w * math.log(w)

        if total_weight <= 0:
            return 0.0

        entropy = math.log(total_weight) - (sum_w_log_w / total_weight)
        # Small tie-breaker jitter from RNG
        entropy += self.rng.uniform(1e-6, 1e-4)
        return entropy

    def _find_lowest_entropy_cell(self) -> Optional[Tuple[int, int]]:
        """Finds uncollapsed cell with minimum positive entropy or contradiction (0 candidates)."""
        min_entropy = float("inf")
        best_coord: Optional[Tuple[int, int]] = None

        for coord, candidates in self.grid.items():
            if len(candidates) == 0:
                # Contradiction: must be handled immediately by solve loop
                return coord
            if len(candidates) == 1:
                continue
            entropy = self._compute_entropy(candidates)
            if entropy < min_entropy:
                min_entropy = entropy
                best_coord = coord

        return best_coord

    def _propagate(self, initial_queue: List[Tuple[int, int]]) -> bool:
        """
        AC-3 arc consistency propagation across the grid.
        Returns True if consistent, False if a contradiction (empty candidate set) occurs.
        """
        queue = list(initial_queue)
        in_queue = set(queue)

        while queue:
            x, y = queue.pop(0)
            in_queue.discard((x, y))
            current_candidates = self.grid[(x, y)]

            for d in Direction2D:
                dx, dy = DIR_OFFSETS_2D[d]
                nx, ny = x + dx, y + dy
                neighbor = (nx, ny)

                if neighbor not in self.grid:
                    continue

                neighbor_candidates = self.grid[neighbor]
                if len(neighbor_candidates) <= 1 and (nx, ny) not in in_queue:
                    # Neighbor already collapsed, check compatibility
                    pass

                # Find all neighbor tiles allowed by at least one current candidate
                allowed_for_neighbor: Set[str] = set()
                for tid in current_candidates:
                    allowed_for_neighbor.update(self._allowed_neighbors[d][tid])

                # Narrow neighbor's domain
                new_neighbor_candidates = neighbor_candidates.intersection(allowed_for_neighbor)

                if len(new_neighbor_candidates) != len(neighbor_candidates):
                    if not new_neighbor_candidates:
                        # Contradiction: Neighbor has 0 valid tiles
                        self.grid[neighbor] = set()
                        return False
                    self.grid[neighbor] = new_neighbor_candidates
                    if neighbor not in in_queue:
                        queue.append(neighbor)
                        in_queue.add(neighbor)

        return True

    def _pick_tile_weighted(self, candidates: Set[str]) -> str:
        """Selects a tile from candidates according to their weights."""
        tile_list = sorted(list(candidates))  # Deterministic order
        weights = [self.tile_catalog[t].weight for t in tile_list]
        return self.rng.choices(tile_list, weights=weights, k=1)[0]

    def solve(self) -> Dict[Tuple[int, int], PlacedTile]:
        """
        Solves the WFC grid using entropy selection, AC-3 propagation, and backtracking.
        Returns a mapping of (x, y) coordinates to PlacedTile objects.
        """
        backtrack_stack: List[Tuple[Dict[Tuple[int, int], Set[str]], Tuple[int, int], str]] = []
        backtracks = 0

        # Check for pre-existing contradictions from constraints
        for coord, cands in self.grid.items():
            if len(cands) == 0:
                raise WFCContradictionError(f"Grid contains cell {coord} with 0 candidates prior to solving")

        while True:
            cell = self._find_lowest_entropy_cell()
            if cell is None:
                # All cells collapsed! Check if any cell has 0 tiles
                for coord, candidates in self.grid.items():
                    if len(candidates) != 1:
                        raise WFCContradictionError(f"Cell {coord} has {len(candidates)} candidates upon completion")
                break

            candidates = self.grid[cell]
            if not candidates:
                # Contradiction!
                if not backtrack_stack or backtracks >= self.max_backtracks:
                    raise WFCContradictionError(f"Contradiction at cell {cell} with {backtracks} backtracks")

                # Backtrack
                saved_grid, tried_cell, tried_tile = backtrack_stack.pop()
                backtracks += 1
                self.grid = saved_grid
                # Remove the failed tile from that cell
                self.grid[tried_cell].discard(tried_tile)
                if not self.grid[tried_cell] or not self._propagate([tried_cell]):
                    continue
                continue

            chosen_tile = self._pick_tile_weighted(candidates)

            # Save snapshot for backtracking
            saved_grid = {k: set(v) for k, v in self.grid.items()}
            backtrack_stack.append((saved_grid, cell, chosen_tile))

            # Collapse cell
            self.grid[cell] = {chosen_tile}
            consistent = self._propagate([cell])

            if not consistent:
                # Immediate contradiction upon propagation
                if backtracks >= self.max_backtracks:
                    raise WFCContradictionError(f"Propagation contradiction reached max backtracks ({self.max_backtracks})")

                saved_grid, tried_cell, tried_tile = backtrack_stack.pop()
                backtracks += 1
                self.grid = saved_grid
                self.grid[tried_cell].discard(tried_tile)
                self._propagate([tried_cell])

        # Convert collapsed grid to PlacedTile dictionary
        result: Dict[Tuple[int, int], PlacedTile] = {}
        for (x, y), candidates in self.grid.items():
            tile_id = next(iter(candidates))
            tile_def = self.tile_catalog[tile_id]
            world_x = float(x * self.tile_size_meters)
            world_y = float(y * self.tile_size_meters)
            world_z = 0.0

            result[(x, y)] = PlacedTile(
                tile_id=tile_id,
                x=x,
                y=y,
                z=0,
                room_type=tile_def.room_type,
                world_pos=(world_x, world_y, world_z),
                rotation_deg=0.0,
            )

        return result
