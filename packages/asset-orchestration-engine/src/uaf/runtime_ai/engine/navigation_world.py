"""
UAF-81.82: Headless Navigation World, Streaming Tile Links, and Spatial Raycasting.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from ..models.definition import (
    NavigationProfile,
    NavigationTileUnavailable,
    PathResult,
    PathStatus,
    Vec3,
    vec3_add,
    vec3_distance_sq,
    vec3_dot,
    vec3_scale,
    vec3_sub,
)
from ..navigation.astar import AStarPathfinder
from ..navigation.dynamic_obstacles import DynamicObstacle, DynamicObstacleManager
from ..navigation.funnel import FunnelAlgorithm
from ..navigation.mesh import NavMesh
from ..navigation.tile import NavTile


class NavigationWorld:
    """
    Independent, headless navigation world container.
    Integrates static/dynamic NavMesh, spatial tiles, dynamic obstacles,
    and cell streaming state from UAF-81.81 without graphics/rendering dependencies.
    """

    def __init__(self):
        self.nav_mesh = NavMesh()
        self.tiles: Dict[Tuple[int, int], NavTile] = {}
        self.obstacle_manager = DynamicObstacleManager()
        self.world_revision: int = 0

    def register_tile(self, tile: NavTile) -> None:
        self.tiles[(tile.tile_x, tile.tile_y)] = tile
        self.world_revision += 1

    def unregister_tile(self, tile_x: int, tile_y: int) -> Optional[NavTile]:
        tile = self.tiles.pop((tile_x, tile_y), None)
        if tile:
            # Remove its polygons from NavMesh
            for pid in list(tile.polygon_ids):
                self.nav_mesh.remove_polygon(pid)
            self.world_revision += 1
        return tile

    def set_cell_streaming_state(self, tile_x: int, tile_y: int, is_resident: bool) -> None:
        """Invoked by UAF-81.81 streaming engine when a spatial cell changes residency."""
        tile = self.tiles.get((tile_x, tile_y))
        if tile is not None:
            tile.set_resident(is_resident)
            self.world_revision += 1

    def is_location_navigable(self, position: Vec3) -> bool:
        """Check if position is covered by a resident navigation tile."""
        for tile in self.tiles.values():
            if tile.is_resident and tile.contains_point_2d(position):
                return True
        # If no tiles registered, fallback to presence of containing polygon
        if not self.tiles:
            return self.nav_mesh.find_containing_polygon(position) is not None
        return False

    def find_path(
        self,
        start_point: Vec3,
        goal_point: Vec3,
        profile: Optional[NavigationProfile] = None,
        request_id: int = 0,
    ) -> PathResult:
        """
        Execute pathfinding from start_point to goal_point.
        Rejects request with NAVIGATION_UNAVAILABLE if start or goal lies in an unloaded tile.
        """
        # 1. Streaming residency check
        if self.tiles:
            if not self.is_location_navigable(start_point) or not self.is_location_navigable(goal_point):
                return PathResult(
                    request_id=request_id,
                    status=PathStatus.NAVIGATION_UNAVAILABLE,
                )

        # 2. A* Polygon search
        astar_res = AStarPathfinder.find_path(
            self.nav_mesh,
            start_point,
            goal_point,
            profile=profile,
            request_id=request_id,
        )

        if astar_res.status != PathStatus.SUCCESS:
            return astar_res

        # 3. Funnel smoothing
        smoothed_pts = FunnelAlgorithm.smooth_path(
            start_point,
            astar_res.portals,
            goal_point,
        )

        return PathResult(
            request_id=request_id,
            status=PathStatus.SUCCESS,
            polygons=astar_res.polygons,
            portals=astar_res.portals,
            points=smoothed_pts,
            total_cost=astar_res.total_cost,
        )

    def raycast(self, origin: Vec3, direction: Vec3, max_distance: float) -> bool:
        """
        Perform a spatial line-of-sight raycast against active dynamic obstacles.
        Returns True if blocked by an obstacle within max_distance.
        """
        dir_norm = direction
        l2 = dir_norm[0] * dir_norm[0] + dir_norm[1] * dir_norm[1] + dir_norm[2] * dir_norm[2]
        if l2 > 1e-8:
            inv = 1.0 / (l2 ** 0.5)
            dir_norm = (dir_norm[0] * inv, dir_norm[1] * inv, dir_norm[2] * inv)

        for obs in self.obstacle_manager.obstacles.values():
            if not obs.enabled:
                continue

            # Ray to cylinder in horizontal plane
            rel = (obs.position[0] - origin[0], 0.0, obs.position[2] - origin[2])
            proj_t = rel[0] * dir_norm[0] + rel[2] * dir_norm[2]

            if proj_t < 0.0 or proj_t > max_distance:
                continue

            closest_x = origin[0] + proj_t * dir_norm[0]
            closest_z = origin[2] + proj_t * dir_norm[2]

            d_sq = (closest_x - obs.position[0]) ** 2 + (closest_z - obs.position[2]) ** 2
            if d_sq <= (obs.radius * obs.radius):
                # Height check
                curr_y = origin[1] + proj_t * dir_norm[1]
                if abs(curr_y - obs.position[1]) <= obs.height:
                    return True

        return False
