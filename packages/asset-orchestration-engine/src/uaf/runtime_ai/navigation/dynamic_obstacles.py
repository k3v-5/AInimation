"""
UAF-81.82: Dynamic Obstacle Registration, Mesh Carving, and Revision Invalidation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from ..models.definition import NavAreaType, NavPolygon, Vec3, vec3_distance_sq
from .mesh import NavMesh
from .polygon import is_point_inside_polygon_2d, project_point_to_segment


@dataclass(frozen=True)
class DynamicObstacle:
    obstacle_id: str
    position: Vec3
    radius: float = 1.0
    height: float = 2.0
    enabled: bool = True


class DynamicObstacleManager:
    """
    Manages runtime dynamic obstacles (doors, barriers, collapsed terrain).
    Marks intersecting NavPolygons as blocked (NO_GO) without full NavMesh rebuilds,
    incrementing revision counters to signal path invalidation.
    """

    def __init__(self):
        self._obstacles: Dict[str, DynamicObstacle] = {}
        self._blocked_polys: Dict[str, Set[int]] = {}  # obstacle_id -> set(polygon_ids)
        self._original_areas: Dict[int, str] = {}      # polygon_id -> original_area_type

    @property
    def obstacles(self) -> Dict[str, DynamicObstacle]:
        return self._obstacles

    def register_obstacle(self, obstacle: DynamicObstacle, nav_mesh: NavMesh) -> Set[int]:
        self._obstacles[obstacle.obstacle_id] = obstacle
        affected = self._apply_obstacle(obstacle, nav_mesh)
        self._blocked_polys[obstacle.obstacle_id] = affected
        return affected

    def remove_obstacle(self, obstacle_id: str, nav_mesh: NavMesh) -> Set[int]:
        if obstacle_id not in self._obstacles:
            return set()

        del self._obstacles[obstacle_id]
        affected = self._blocked_polys.pop(obstacle_id, set())

        # Restore original areas for polygons no longer blocked by any other obstacle
        all_other_blocked: Set[int] = set()
        for s in self._blocked_polys.values():
            all_other_blocked.update(s)

        for pid in affected:
            if pid not in all_other_blocked and pid in self._original_areas:
                orig_area = self._original_areas.pop(pid)
                poly = nav_mesh.get_polygon(pid)
                if poly is not None:
                    restored = NavPolygon(
                        polygon_id=poly.polygon_id,
                        vertices=poly.vertices,
                        neighbors=poly.neighbors,
                        area_type=orig_area,
                        traversal_cost=poly.traversal_cost,
                    )
                    nav_mesh.add_polygon(restored, validate=False)

        return affected

    def _apply_obstacle(self, obstacle: DynamicObstacle, nav_mesh: NavMesh) -> Set[int]:
        """Find and block polygons intersecting the cylinder obstacle."""
        affected: Set[int] = set()
        r2 = obstacle.radius * obstacle.radius

        for pid in sorted(nav_mesh.polygons.keys()):
            poly = nav_mesh.polygons[pid]
            # Height check
            avg_y = sum(v[1] for v in poly.vertices) / len(poly.vertices)
            if abs(obstacle.position[1] - avg_y) > obstacle.height:
                continue

            # Check if obstacle center is inside polygon or near any edge
            intersects = False
            if is_point_inside_polygon_2d(obstacle.position, poly.vertices):
                intersects = True
            else:
                n = len(poly.vertices)
                for i in range(n):
                    pt = project_point_to_segment(obstacle.position, poly.vertices[i], poly.vertices[(i + 1) % n])
                    if vec3_distance_sq(obstacle.position, pt) <= r2:
                        intersects = True
                        break

            if intersects:
                affected.add(pid)
                if pid not in self._original_areas:
                    self._original_areas[pid] = poly.area_type
                # Mark as NO_GO
                blocked_poly = NavPolygon(
                    polygon_id=poly.polygon_id,
                    vertices=poly.vertices,
                    neighbors=poly.neighbors,
                    area_type=NavAreaType.NO_GO.value,
                    traversal_cost=poly.traversal_cost,
                )
                nav_mesh.add_polygon(blocked_poly, validate=False)

        return affected
