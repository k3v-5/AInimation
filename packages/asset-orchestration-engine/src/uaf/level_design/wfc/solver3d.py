"""
UAF-81.90: Wave Function Collapse 3D Solver.
Implements multi-story 3D constraint satisfaction with vertical sockets (UP/DOWN),
stairwell/elevator shafts, Shannon entropy, AC-3 propagation, and backtracking.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Set, Tuple

from uaf.level_design.core.contracts import (
    Direction3D,
    OPPOSITE_DIR_3D,
    DIR_OFFSETS_3D,
    SocketType,
    are_sockets_compatible,
    ModularTileDefinition,
    PlacedTile,
)
from uaf.level_design.wfc.solver2d import WFCContradictionError


class WaveFunctionCollapse3D:
    """
    3D Wave Function Collapse solver.
    Operates on a discrete (width x depth x height) grid of modular 3D tiles.
    """

    def __init__(
        self,
        width: int,
        depth: int,
        height: int,
        tile_catalog: List[ModularTileDefinition],
        seed: Optional[int] = 42,
        tile_size_meters: float = 4.0,
        floor_height_meters: float = 3.5,
        max_backtracks: int = 250,
    ):
        if width <= 0 or depth <= 0 or height <= 0:
            raise ValueError(f"Grid dimensions must be positive, got {width}x{depth}x{height}")
        if not tile_catalog:
            raise ValueError("tile_catalog cannot be empty")

        self.width = width
        self.depth = depth
        self.height = height
        self.tile_catalog: Dict[str, ModularTileDefinition] = {t.tile_id: t for t in tile_catalog}
        self.seed = seed
        self.rng = random.Random(seed)
        self.tile_size_meters = tile_size_meters
        self.floor_height_meters = floor_height_meters
        self.max_backtracks = max_backtracks

        # Precompute 3D adjacency
        self._allowed_neighbors: Dict[Direction3D, Dict[str, Set[str]]] = {
            d: {tid: set() for tid in self.tile_catalog} for d in Direction3D
        }
        self._precompute_adjacency()

        # Grid state: (x, y, z) -> Set[str] of candidate tile_ids
        self.grid: Dict[Tuple[int, int, int], Set[str]] = {}
        self._init_grid()

    def _precompute_adjacency(self) -> None:
        """Precomputes compatible neighbor tile sets for each 3D direction."""
        for d in Direction3D:
            opp_d = OPPOSITE_DIR_3D[d]
            for tid_a, tile_a in self.tile_catalog.items():
                sock_a = tile_a.get_socket_3d(d)
                for tid_b, tile_b in self.tile_catalog.items():
                    sock_b = tile_b.get_socket_3d(opp_d)
                    if are_sockets_compatible(sock_a, sock_b):
                        self._allowed_neighbors[d][tid_a].add(tid_b)

    def _init_grid(self) -> None:
        """Initializes all 3D cells with all tile candidates."""
        all_tile_ids = set(self.tile_catalog.keys())
        self.grid = {
            (x, y, z): set(all_tile_ids)
            for x in range(self.width)
            for y in range(self.depth)
            for z in range(self.height)
        }

    def constrain_cell(self, x: int, y: int, z: int, allowed_tile_ids: Set[str]) -> bool:
        """Manually constrains a cell to a subset of tile IDs."""
        coord = (x, y, z)
        if coord not in self.grid:
            raise IndexError(f"Cell {coord} out of grid bounds")

        current = self.grid[coord]
        narrowed = current.intersection(allowed_tile_ids)
        if not narrowed:
            return False

        if narrowed != current:
            self.grid[coord] = narrowed
            return self._propagate([coord])
        return True

    def _compute_entropy(self, candidates: Set[str]) -> float:
        """Computes Shannon entropy for 3D cell candidates."""
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
        entropy += self.rng.uniform(1e-6, 1e-4)
        return entropy

    def _find_lowest_entropy_cell(self) -> Optional[Tuple[int, int, int]]:
        """Finds uncollapsed 3D cell with minimum positive entropy."""
        min_entropy = float("inf")
        best_coord: Optional[Tuple[int, int, int]] = None

        for coord, candidates in self.grid.items():
            if len(candidates) == 0:
                return coord
            if len(candidates) == 1:
                continue
            entropy = self._compute_entropy(candidates)
            if entropy < min_entropy:
                min_entropy = entropy
                best_coord = coord

        return best_coord

    def _propagate(self, initial_queue: List[Tuple[int, int, int]]) -> bool:
        """AC-3 arc consistency propagation in 3D (6 directions)."""
        queue = list(initial_queue)
        in_queue = set(queue)

        while queue:
            x, y, z = queue.pop(0)
            in_queue.discard((x, y, z))
            current_candidates = self.grid[(x, y, z)]

            for d in Direction3D:
                dx, dy, dz = DIR_OFFSETS_3D[d]
                nx, ny, nz = x + dx, y + dy, z + dz
                neighbor = (nx, ny, nz)

                if neighbor not in self.grid:
                    continue

                neighbor_candidates = self.grid[neighbor]
                allowed_for_neighbor: Set[str] = set()
                for tid in current_candidates:
                    allowed_for_neighbor.update(self._allowed_neighbors[d][tid])

                new_neighbor_candidates = neighbor_candidates.intersection(allowed_for_neighbor)

                if len(new_neighbor_candidates) != len(neighbor_candidates):
                    if not new_neighbor_candidates:
                        self.grid[neighbor] = set()
                        return False
                    self.grid[neighbor] = new_neighbor_candidates
                    if neighbor not in in_queue:
                        queue.append(neighbor)
                        in_queue.add(neighbor)

        return True

    def _pick_tile_weighted(self, candidates: Set[str]) -> str:
        tile_list = sorted(list(candidates))
        weights = [self.tile_catalog[t].weight for t in tile_list]
        return self.rng.choices(tile_list, weights=weights, k=1)[0]

    def solve(self) -> Dict[Tuple[int, int, int], PlacedTile]:
        """Solves 3D WFC grid and returns placed tiles with 3D world coordinates."""
        backtrack_stack: List[Tuple[Dict[Tuple[int, int, int], Set[str]], Tuple[int, int, int], str]] = []
        backtracks = 0

        # Check for pre-existing contradictions
        for coord, cands in self.grid.items():
            if len(cands) == 0:
                raise WFCContradictionError(f"3D Grid contains cell {coord} with 0 candidates prior to solving")
        backtracks = 0

        while True:
            cell = self._find_lowest_entropy_cell()
            if cell is None:
                for coord, candidates in self.grid.items():
                    if len(candidates) != 1:
                        raise WFCContradictionError(f"Cell {coord} has {len(candidates)} candidates upon completion")
                break

            candidates = self.grid[cell]
            if not candidates:
                if not backtrack_stack or backtracks >= self.max_backtracks:
                    raise WFCContradictionError(f"3D Contradiction at cell {cell} after {backtracks} backtracks")

                saved_grid, tried_cell, tried_tile = backtrack_stack.pop()
                backtracks += 1
                self.grid = saved_grid
                self.grid[tried_cell].discard(tried_tile)
                if not self.grid[tried_cell] or not self._propagate([tried_cell]):
                    continue
                continue

            chosen_tile = self._pick_tile_weighted(candidates)

            saved_grid = {k: set(v) for k, v in self.grid.items()}
            backtrack_stack.append((saved_grid, cell, chosen_tile))

            self.grid[cell] = {chosen_tile}
            consistent = self._propagate([cell])

            if not consistent:
                if backtracks >= self.max_backtracks:
                    raise WFCContradictionError(f"3D Propagation reached max backtracks ({self.max_backtracks})")

                saved_grid, tried_cell, tried_tile = backtrack_stack.pop()
                backtracks += 1
                self.grid = saved_grid
                self.grid[tried_cell].discard(tried_tile)
                self._propagate([tried_cell])

        result: Dict[Tuple[int, int, int], PlacedTile] = {}
        for (x, y, z), candidates in self.grid.items():
            tile_id = next(iter(candidates))
            tile_def = self.tile_catalog[tile_id]
            world_x = float(x * self.tile_size_meters)
            world_y = float(y * self.tile_size_meters)
            world_z = float(z * self.floor_height_meters)

            result[(x, y, z)] = PlacedTile(
                tile_id=tile_id,
                x=x,
                y=y,
                z=z,
                room_type=tile_def.room_type,
                world_pos=(world_x, world_y, world_z),
                rotation_deg=0.0,
            )

        return result
