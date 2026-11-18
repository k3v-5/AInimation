"""
UAF-81.82: Deterministic A* Pathfinder on Convex NavPolygons.
"""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Sequence, Set, Tuple

from ..models.definition import (
    NavigationProfile,
    PathRequest,
    PathResult,
    PathStatus,
    Portal,
    Vec3,
    vec3_distance,
)
from .mesh import NavMesh


class AStarPathfinder:
    """
    Deterministic A* pathfinding implementation.
    Guarantees bit-exact, reproducible paths using strict total-ordering tuples
    (f_score, g_score, polygon_id) on all heap operations.
    """

    @staticmethod
    def find_path(
        nav_mesh: NavMesh,
        start_point: Vec3,
        goal_point: Vec3,
        profile: Optional[NavigationProfile] = None,
        request_id: int = 0,
    ) -> PathResult:
        """Find the optimal sequence of polygons and portals from start_point to goal_point."""
        prof = profile or NavigationProfile(profile_id="Default")

        # 1. Locate start and goal polygons
        start_poly_id = nav_mesh.find_containing_polygon(start_point)
        if start_poly_id is None:
            return PathResult(
                request_id=request_id,
                status=PathStatus.INVALID_START,
            )

        goal_poly_id = nav_mesh.find_containing_polygon(goal_point)
        if goal_poly_id is None:
            return PathResult(
                request_id=request_id,
                status=PathStatus.INVALID_GOAL,
            )

        start_poly = nav_mesh.get_polygon(start_poly_id)
        goal_poly = nav_mesh.get_polygon(goal_poly_id)

        if not prof.is_area_allowed(start_poly.area_type) or not prof.is_area_allowed(goal_poly.area_type):
            return PathResult(
                request_id=request_id,
                status=PathStatus.NO_PATH,
            )

        # 2. Same polygon trivial case
        if start_poly_id == goal_poly_id:
            dist = vec3_distance(start_point, goal_point)
            return PathResult(
                request_id=request_id,
                status=PathStatus.SUCCESS,
                polygons=(start_poly_id,),
                portals=(),
                points=(start_point, goal_point),
                total_cost=dist * start_poly.traversal_cost,
            )

        # 3. Deterministic A* search
        # Priority queue item: (f_score, g_score, polygon_id)
        open_heap: List[Tuple[float, float, int]] = []
        g_scores: Dict[int, float] = {start_poly_id: 0.0}
        came_from: Dict[int, int] = {}
        closed_set: Set[int] = set()

        h_start = vec3_distance(start_poly.centroid(), goal_point)
        heapq.heappush(open_heap, (h_start, 0.0, start_poly_id))

        found_path = False

        while open_heap:
            f, g, current_id = heapq.heappop(open_heap)

            if current_id in closed_set:
                continue

            closed_set.add(current_id)

            if current_id == goal_poly_id:
                found_path = True
                break

            current_poly = nav_mesh.get_polygon(current_id)
            if current_poly is None:
                continue

            current_centroid = current_poly.centroid()

            # Inspect neighbors in deterministic order (already sorted by neighbor_id ASC)
            for neighbor_id in current_poly.neighbors:
                if neighbor_id in closed_set:
                    continue

                neighbor_poly = nav_mesh.get_polygon(neighbor_id)
                if neighbor_poly is None:
                    continue

                # Check if profile allows this area
                if not prof.is_area_allowed(neighbor_poly.area_type):
                    continue

                neighbor_centroid = neighbor_poly.centroid()
                step_dist = vec3_distance(current_centroid, neighbor_centroid)
                tentative_g = g + (step_dist * neighbor_poly.traversal_cost)

                if tentative_g < g_scores.get(neighbor_id, float("inf")):
                    came_from[neighbor_id] = current_id
                    g_scores[neighbor_id] = tentative_g
                    h = vec3_distance(neighbor_centroid, goal_point)
                    tentative_f = tentative_g + h
                    heapq.heappush(open_heap, (tentative_f, tentative_g, neighbor_id))

        if not found_path:
            return PathResult(
                request_id=request_id,
                status=PathStatus.NO_PATH,
            )

        # 4. Reconstruct polygon chain
        path_polys: List[int] = []
        curr = goal_poly_id
        while curr in came_from:
            path_polys.append(curr)
            curr = came_from[curr]
        path_polys.append(start_poly_id)
        path_polys.reverse()

        # 5. Extract portal sequence
        portals: List[Portal] = []
        for i in range(len(path_polys) - 1):
            p_from = path_polys[i]
            p_to = path_polys[i + 1]
            portal = nav_mesh.get_portal(p_from, p_to)
            if portal is not None:
                portals.append(portal)

        return PathResult(
            request_id=request_id,
            status=PathStatus.SUCCESS,
            polygons=tuple(path_polys),
            portals=tuple(portals),
            points=(start_point, goal_point),
            total_cost=g_scores[goal_poly_id],
        )
