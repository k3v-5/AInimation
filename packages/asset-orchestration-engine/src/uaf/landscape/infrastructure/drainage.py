"""
UAF-81.91: River Drainage Networks, Flow Accumulation & Channel Carving.
Simulates D8 hydrological routing, identifies river basins, carves riverbeds,
and extracts river spline trajectories.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

from uaf.landscape.core.contracts import SplineNode, Heightfield2D


class RiverDrainageNetwork:
    """
    Simulates water drainage across a heightfield using standard D8 flow direction,
    calculates upstream flow accumulation, and extracts river paths.
    """

    D8_OFFSETS: List[Tuple[int, int]] = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (1, -1), (-1, 1), (1, 1),
    ]

    def __init__(
        self,
        river_accumulation_threshold: int = 25,
        carve_depth_meters: float = 2.5,
        carve_width_cells: int = 1,
    ):
        self.accumulation_threshold = river_accumulation_threshold
        self.carve_depth = carve_depth_meters
        self.carve_width = carve_width_cells

    def compute_flow_accumulation(self, heightfield: Heightfield2D) -> Tuple[List[List[Tuple[int, int]]], List[List[int]]]:
        """
        Computes D8 flow direction and total upstream cell accumulation matrix.
        Returns:
            flow_dir: flow_dir[y][x] = (target_x, target_y)
            accumulation: accumulation[y][x] = number of contributing cells
        """
        w, h = heightfield.width, heightfield.height
        flow_dir: List[List[Tuple[int, int]]] = [[(x, y) for x in range(w)] for y in range(h)]
        in_degree: List[List[int]] = [[0 for _ in range(w)] for _ in range(h)]

        # 1. Determine steepest downhill neighbor for each cell
        for y in range(h):
            for x in range(w):
                curr_h = heightfield.get_elevation(x, y)
                steepest_drop = 0.0
                best_neighbor = (x, y)

                for dx, dy in self.D8_OFFSETS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        dist = math.hypot(dx, dy)
                        drop = (curr_h - heightfield.get_elevation(nx, ny)) / dist
                        if drop > steepest_drop:
                            steepest_drop = drop
                            best_neighbor = (nx, ny)

                flow_dir[y][x] = best_neighbor
                if best_neighbor != (x, y):
                    bx, by = best_neighbor
                    in_degree[by][bx] += 1

        # 2. Topological sort to compute upstream accumulation
        queue: List[Tuple[int, int]] = [
            (x, y) for y in range(h) for x in range(w) if in_degree[y][x] == 0
        ]
        accumulation: List[List[int]] = [[1 for _ in range(w)] for _ in range(h)]

        while queue:
            cx, cy = queue.pop(0)
            tx, ty = flow_dir[cy][cx]

            if (tx, ty) != (cx, cy):
                accumulation[ty][tx] += accumulation[cy][cx]
                in_degree[ty][tx] -= 1
                if in_degree[ty][tx] == 0:
                    queue.append((tx, ty))

        return flow_dir, accumulation

    def extract_river_splines(
        self,
        heightfield: Heightfield2D,
        flow_dir: List[List[Tuple[int, int]]],
        accumulation: List[List[int]],
    ) -> List[List[SplineNode]]:
        """
        Extracts river splines by tracing continuous downstream paths of cells
        whose upstream flow accumulation exceeds the threshold.
        """
        w, h = heightfield.width, heightfield.height
        visited_in_river: Set[Tuple[int, int]] = set()
        rivers: List[List[SplineNode]] = []

        # Find river heads (cells with accumulation >= threshold whose source is below threshold)
        river_heads: List[Tuple[int, int]] = []
        for y in range(h):
            for x in range(w):
                if accumulation[y][x] >= self.accumulation_threshold:
                    # Check if upstream cells are below threshold
                    is_head = True
                    for dx, dy in self.D8_OFFSETS:
                        px, py = x + dx, y + dy
                        if 0 <= px < w and 0 <= py < h:
                            if flow_dir[py][px] == (x, y) and accumulation[py][px] >= self.accumulation_threshold:
                                is_head = False
                                break
                    if is_head:
                        river_heads.append((x, y))

        for head in river_heads:
            curr = head
            river_nodes: List[SplineNode] = []
            pt_idx = 0

            while curr not in visited_in_river:
                visited_in_river.add(curr)
                cx, cy = curr
                world_x, world_y, world_z = heightfield.get_world_coords_cm(cx, cy)

                node = SplineNode(
                    node_id=f"RiverNode_{len(rivers)}_{pt_idx}",
                    world_pos=(world_x, world_y, world_z),
                    width_cm=min(2500.0, 400.0 + accumulation[cy][cx] * 15.0),
                )
                river_nodes.append(node)
                pt_idx += 1

                nxt = flow_dir[cy][cx]
                if nxt == curr or accumulation[nxt[1]][nxt[0]] < self.accumulation_threshold:
                    break
                curr = nxt

            if len(river_nodes) >= 3:
                # Calculate tangents
                for i in range(len(river_nodes)):
                    if i == 0:
                        t = (
                            river_nodes[1].world_pos[0] - river_nodes[0].world_pos[0],
                            river_nodes[1].world_pos[1] - river_nodes[0].world_pos[1],
                            river_nodes[1].world_pos[2] - river_nodes[0].world_pos[2],
                        )
                    elif i == len(river_nodes) - 1:
                        t = (
                            river_nodes[-1].world_pos[0] - river_nodes[-2].world_pos[0],
                            river_nodes[-1].world_pos[1] - river_nodes[-2].world_pos[1],
                            river_nodes[-1].world_pos[2] - river_nodes[-2].world_pos[2],
                        )
                    else:
                        t = (
                            (river_nodes[i + 1].world_pos[0] - river_nodes[i - 1].world_pos[0]) * 0.5,
                            (river_nodes[i + 1].world_pos[1] - river_nodes[i - 1].world_pos[1]) * 0.5,
                            (river_nodes[i + 1].world_pos[2] - river_nodes[i - 1].world_pos[2]) * 0.5,
                        )
                    river_nodes[i].tangent = t

                rivers.append(river_nodes)

        return rivers

    def carve_riverbeds(
        self,
        heightfield: Heightfield2D,
        accumulation: List[List[int]],
    ) -> Heightfield2D:
        """Slightly depresses terrain along high-flow drainage paths to form natural water channels."""
        w, h = heightfield.width, heightfield.height
        vert_range = heightfield.max_elevation_meters - heightfield.min_elevation_meters
        norm_carve = self.carve_depth / max(1.0, vert_range)

        for y in range(h):
            for x in range(w):
                acc = accumulation[y][x]
                if acc >= self.accumulation_threshold:
                    factor = min(1.0, acc / (self.accumulation_threshold * 3.0))
                    curr = heightfield.get_elevation(x, y)
                    heightfield.set_elevation(x, y, curr - norm_carve * factor)

        return heightfield
