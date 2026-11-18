"""Public exports for navigation and pathfinding subsystem."""

from .polygon import (
    is_polygon_convex,
    compute_polygon_area_2d,
    is_point_inside_polygon_2d,
    closest_point_on_polygon,
    find_shared_edge,
    cross_product_2d_xz,
    project_point_to_segment,
)
from .mesh import NavMesh
from .tile import NavTile
from .astar import AStarPathfinder
from .funnel import FunnelAlgorithm
from .hierarchical import HierarchicalPathfinder
from .dynamic_obstacles import DynamicObstacle, DynamicObstacleManager
from .path import PathRequestQueue, PathValidator

__all__ = [
    "is_polygon_convex",
    "compute_polygon_area_2d",
    "is_point_inside_polygon_2d",
    "closest_point_on_polygon",
    "find_shared_edge",
    "cross_product_2d_xz",
    "project_point_to_segment",
    "NavMesh",
    "NavTile",
    "AStarPathfinder",
    "FunnelAlgorithm",
    "HierarchicalPathfinder",
    "DynamicObstacle",
    "DynamicObstacleManager",
    "PathRequestQueue",
    "PathValidator",
]
