"""
UAF-81.91: Cost-Surface Road Routing, Catmull-Rom Spline Smoothing & Cut-and-Fill Carving.
Plans energy-minimizing transport links connecting POIs across complex terrain,
smooths routes into high-order cubic splines, and terraforms roadbeds.
"""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Set, Tuple

from uaf.landscape.core.contracts import (
    RoadCategory,
    SplineNode,
    RoadPath,
    Heightfield2D,
)


class RoadNetworkPlanner:
    """
    Plans and smooths road networks across continuous heightfields using
    cost-surface pathfinding and Catmull-Rom spline formulation.
    """

    def __init__(
        self,
        slope_penalty_factor: float = 12.0,
        max_allowed_slope_deg: float = 30.0,
    ):
        self.slope_penalty = slope_penalty_factor
        self.max_slope = max_allowed_slope_deg

    def plan_road(
        self,
        heightfield: Heightfield2D,
        start_coord: Tuple[int, int],
        goal_coord: Tuple[int, int],
        road_id: str = "ROAD_01",
        name: str = "Trans-Valley Highway",
        category: RoadCategory = RoadCategory.MAIN_ROAD,
    ) -> Optional[RoadPath]:
        """
        Calculates minimum-energy path between start_coord and goal_coord,
        smooths into Catmull-Rom splines, and calculates gradient metrics.
        """
        raw_path = self._astar_cost_surface(heightfield, start_coord, goal_coord)
        if not raw_path or len(raw_path) < 2:
            return None

        # Downsample/simplify raw path to key control points
        control_points = self._simplify_path(raw_path, tolerance_cells=1.5)

        # Interpolate control points with Catmull-Rom splines
        spline_nodes = self._generate_catmull_rom_spline(heightfield, control_points, category)

        # Calculate metrics
        total_length_m = 0.0
        max_grad_pct = 0.0

        for i in range(len(spline_nodes) - 1):
            p1 = spline_nodes[i].world_pos
            p2 = spline_nodes[i + 1].world_pos

            dx = (p2[0] - p1[0]) / 100.0
            dy = (p2[1] - p1[1]) / 100.0
            dz = (p2[2] - p1[2]) / 100.0

            seg_len_2d = math.hypot(dx, dy)
            seg_len_3d = math.sqrt(dx * dx + dy * dy + dz * dz)
            total_length_m += seg_len_3d

            if seg_len_2d > 1e-3:
                grad_pct = (abs(dz) / seg_len_2d) * 100.0
                if grad_pct > max_grad_pct:
                    max_grad_pct = grad_pct

        return RoadPath(
            road_id=road_id,
            name=name,
            category=category,
            nodes=spline_nodes,
            total_length_meters=round(total_length_m, 2),
            max_gradient_pct=round(max_grad_pct, 2),
        )

    def _astar_cost_surface(
        self,
        heightfield: Heightfield2D,
        start: Tuple[int, int],
        goal: Tuple[int, int],
    ) -> Optional[List[Tuple[int, int]]]:
        """A* search on a weighted slope-penalized cost surface."""
        w, h = heightfield.width, heightfield.height
        vert_scale = heightfield.max_elevation_meters - heightfield.min_elevation_meters
        cell_m = heightfield.meters_per_cell

        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return math.hypot(a[0] - b[0], a[1] - b[1])

        counter = 0
        frontier: List[Tuple[float, int, Tuple[int, int], List[Tuple[int, int]]]] = []
        heapq.heappush(frontier, (0.0, counter, start, [start]))

        g_scores: Dict[Tuple[int, int], float] = {start: 0.0}

        offsets = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
        ]

        while frontier:
            _, _, curr, path = heapq.heappop(frontier)
            if curr == goal:
                return path

            cx, cy = curr
            curr_h = heightfield.get_elevation(cx, cy)

            for ox, oy in offsets:
                nx, ny = cx + ox, cy + oy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue

                neighbor_h = heightfield.get_elevation(nx, ny)
                dist_cells = math.hypot(ox, oy)
                horiz_dist_m = dist_cells * cell_m
                vert_diff_m = abs(curr_h - neighbor_h) * vert_scale

                # Calculate slope in degrees
                slope_deg = math.degrees(math.atan2(vert_diff_m, horiz_dist_m))
                if slope_deg > self.max_slope:
                    continue  # Impassable cliff for road

                # Cost metric: distance * (1 + slope penalty)
                slope_normalized = slope_deg / self.max_slope
                cost_weight = dist_cells * (1.0 + self.slope_penalty * (slope_normalized ** 2))

                tentative_g = g_scores[curr] + cost_weight
                if tentative_g < g_scores.get((nx, ny), float("inf")):
                    g_scores[(nx, ny)] = tentative_g
                    f = tentative_g + heuristic((nx, ny), goal)
                    counter += 1
                    heapq.heappush(frontier, (f, counter, (nx, ny), path + [(nx, ny)]))

        return None

    def _simplify_path(self, path: List[Tuple[int, int]], tolerance_cells: float = 1.5) -> List[Tuple[int, int]]:
        """Ramer-Douglas-Peucker line simplification for discrete grid paths."""
        if len(path) <= 2:
            return path

        start, end = path[0], path[-1]
        max_dist = 0.0
        max_idx = 0

        # Line equation from start to end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        line_len = math.hypot(dx, dy)

        for i in range(1, len(path) - 1):
            px, py = path[i]
            if line_len > 1e-5:
                dist = abs(dy * px - dx * py + end[0] * start[1] - end[1] * start[0]) / line_len
            else:
                dist = math.hypot(px - start[0], py - start[1])

            if dist > max_dist:
                max_dist = dist
                max_idx = i

        if max_dist > tolerance_cells:
            left = self._simplify_path(path[: max_idx + 1], tolerance_cells)
            right = self._simplify_path(path[max_idx:], tolerance_cells)
            return left[:-1] + right

        return [start, end]

    def _generate_catmull_rom_spline(
        self,
        heightfield: Heightfield2D,
        control_points: List[Tuple[int, int]],
        category: RoadCategory,
        subdivisions_per_seg: int = 4,
    ) -> List[SplineNode]:
        """Interpolates control points with smooth Catmull-Rom cubic splines."""
        road_width_cm = {
            RoadCategory.HIGHWAY: 1200.0,
            RoadCategory.MAIN_ROAD: 800.0,
            RoadCategory.DIRT_TRACK: 450.0,
            RoadCategory.MOUNTAIN_TRAIL: 250.0,
        }.get(category, 600.0)

        # Convert control points to 3D world coordinates
        pts_3d = [heightfield.get_world_coords_cm(pt[0], pt[1]) for pt in control_points]
        if len(pts_3d) < 2:
            return []

        # Duplicate endpoints for Catmull-Rom clamping
        augmented = [pts_3d[0]] + pts_3d + [pts_3d[-1]]

        spline_nodes: List[SplineNode] = []
        node_idx = 0

        for i in range(1, len(augmented) - 2):
            p0 = augmented[i - 1]
            p1 = augmented[i]
            p2 = augmented[i + 1]
            p3 = augmented[i + 2]

            for s in range(subdivisions_per_seg if i < len(augmented) - 3 else subdivisions_per_seg + 1):
                t = s / subdivisions_per_seg

                # Catmull-Rom cubic evaluation
                t2 = t * t
                t3 = t2 * t

                x = 0.5 * (
                    (2.0 * p1[0])
                    + (-p0[0] + p2[0]) * t
                    + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                    + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
                )
                y = 0.5 * (
                    (2.0 * p1[1])
                    + (-p0[1] + p2[1]) * t
                    + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                    + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
                )
                z = 0.5 * (
                    (2.0 * p1[2])
                    + (-p0[2] + p2[2]) * t
                    + (2.0 * p0[2] - 5.0 * p1[2] + 4.0 * p2[2] - p3[2]) * t2
                    + (-p0[2] + 3.0 * p1[2] - 3.0 * p2[2] + p3[2]) * t3
                )

                spline_nodes.append(
                    SplineNode(
                        node_id=f"RoadNode_{node_idx}",
                        world_pos=(round(x, 2), round(y, 2), round(z, 2)),
                        width_cm=road_width_cm,
                    )
                )
                node_idx += 1

        # Calculate tangents
        for i in range(len(spline_nodes)):
            if i == 0:
                p_next = spline_nodes[1].world_pos
                p_curr = spline_nodes[0].world_pos
                t = (p_next[0] - p_curr[0], p_next[1] - p_curr[1], p_next[2] - p_curr[2])
            elif i == len(spline_nodes) - 1:
                p_curr = spline_nodes[-1].world_pos
                p_prev = spline_nodes[-2].world_pos
                t = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1], p_curr[2] - p_prev[2])
            else:
                p_next = spline_nodes[i + 1].world_pos
                p_prev = spline_nodes[i - 1].world_pos
                t = (
                    (p_next[0] - p_prev[0]) * 0.5,
                    (p_next[1] - p_prev[1]) * 0.5,
                    (p_next[2] - p_prev[2]) * 0.5,
                )
            spline_nodes[i].tangent = t

        return spline_nodes

    def carve_roadbed(
        self,
        heightfield: Heightfield2D,
        road: RoadPath,
        blend_radius_cells: int = 1,
    ) -> Heightfield2D:
        """
        Terraforms / levels the heightfield beneath the road to prevent sideways vehicle tipping.
        """
        vert_range = heightfield.max_elevation_meters - heightfield.min_elevation_meters
        cm_per_cell = heightfield.meters_per_cell * 100.0

        for node in road.nodes:
            wx, wy, wz = node.world_pos
            gx = int(round(wx / cm_per_cell))
            gy = int(round(wy / cm_per_cell))

            target_norm_h = (wz / 100.0 - heightfield.min_elevation_meters) / max(1.0, vert_range)

            for ox in range(-blend_radius_cells, blend_radius_cells + 1):
                for oy in range(-blend_radius_cells, blend_radius_cells + 1):
                    x, y = gx + ox, gy + oy
                    if 0 <= x < heightfield.width and 0 <= y < heightfield.height:
                        d = math.hypot(ox, oy)
                        if d <= blend_radius_cells:
                            weight = 1.0 - (d / (blend_radius_cells + 1.0))
                            curr = heightfield.get_elevation(x, y)
                            heightfield.set_elevation(x, y, curr * (1.0 - weight) + target_norm_h * weight)

        return heightfield
