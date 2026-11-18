"""
UAF-81.82: NavMesh Graph, Adjacency Verification, and Portal Extraction.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from ..models.definition import (
    InvalidNavMesh,
    NavPolygon,
    Portal,
    Vec3,
    vec3_distance_sq,
)
from .polygon import (
    closest_point_on_polygon,
    compute_polygon_area_2d,
    find_shared_edge,
    is_point_inside_polygon_2d,
    is_polygon_convex,
)


class NavMesh:
    """
    Deterministic container of convex NavPolygons forming a navigation graph.
    Supports adjacency verification, portal generation, and spatial point location.
    """

    def __init__(self):
        self._polygons: Dict[int, NavPolygon] = {}
        self._portals: Dict[Tuple[int, int], Portal] = {}
        self._revision: int = 0

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def polygons(self) -> Dict[int, NavPolygon]:
        return self._polygons

    def add_polygon(self, poly: NavPolygon, validate: bool = True) -> None:
        """Register a convex polygon into the NavMesh."""
        if validate:
            if not is_polygon_convex(poly.vertices):
                raise InvalidNavMesh(f"Polygon {poly.polygon_id} is not strictly convex.")
            area = compute_polygon_area_2d(poly.vertices)
            if area < 1e-6:
                raise InvalidNavMesh(f"Polygon {poly.polygon_id} is degenerate (area={area}).")

        self._polygons[poly.polygon_id] = poly
        self._revision += 1

    def remove_polygon(self, polygon_id: int) -> bool:
        if polygon_id in self._polygons:
            del self._polygons[polygon_id]
            # Invalidate any cached portals referencing this polygon
            self._portals = {k: v for k, v in self._portals.items() if polygon_id not in k}
            self._revision += 1
            return True
        return False

    def get_polygon(self, polygon_id: int) -> Optional[NavPolygon]:
        return self._polygons.get(polygon_id)

    def build_adjacency(self) -> None:
        """
        Compute adjacency graph and reciprocal neighbor connections for all polygons.
        Ensures neighbors are sorted deterministically by neighbor_id ASC.
        """
        poly_list = [self._polygons[pid] for pid in sorted(self._polygons.keys())]
        new_polys: Dict[int, NavPolygon] = {}

        for i, p_a in enumerate(poly_list):
            neighbors: List[int] = []
            for j, p_b in enumerate(poly_list):
                if i == j:
                    continue
                edge = find_shared_edge(p_a, p_b)
                if edge is not None:
                    neighbors.append(p_b.polygon_id)
                    # Cache portal
                    self._portals[(p_a.polygon_id, p_b.polygon_id)] = Portal(
                        left=edge[0],
                        right=edge[1],
                        from_poly=p_a.polygon_id,
                        to_poly=p_b.polygon_id,
                    )

            neighbors.sort()
            new_polys[p_a.polygon_id] = NavPolygon(
                polygon_id=p_a.polygon_id,
                vertices=p_a.vertices,
                neighbors=tuple(neighbors),
                area_type=p_a.area_type,
                traversal_cost=p_a.traversal_cost,
            )

        self._polygons = new_polys
        self._revision += 1

    def get_portal(self, from_poly: int, to_poly: int) -> Optional[Portal]:
        """Retrieve the portal segment between two adjacent polygons."""
        cached = self._portals.get((from_poly, to_poly))
        if cached is not None:
            return cached

        pa = self.get_polygon(from_poly)
        pb = self.get_polygon(to_poly)
        if pa is None or pb is None:
            return None

        edge = find_shared_edge(pa, pb)
        if edge is not None:
            portal = Portal(
                left=edge[0],
                right=edge[1],
                from_poly=from_poly,
                to_poly=to_poly,
            )
            self._portals[(from_poly, to_poly)] = portal
            return portal
        return None

    def find_containing_polygon(self, point: Vec3, y_tolerance: float = 2.0) -> Optional[int]:
        """Find the polygon containing point in the horizontal plane within y_tolerance."""
        # Check strict containment first (ordered by polygon_id ASC for determinism)
        for pid in sorted(self._polygons.keys()):
            poly = self._polygons[pid]
            if is_point_inside_polygon_2d(point, poly.vertices, y_tolerance):
                return pid

        # If not strictly inside, find closest polygon within 5 meters
        best_pid: Optional[int] = None
        best_d2 = 25.0  # (5.0m)^2
        for pid in sorted(self._polygons.keys()):
            poly = self._polygons[pid]
            cl = closest_point_on_polygon(point, poly.vertices)
            d2 = vec3_distance_sq(point, cl)
            if d2 < best_d2:
                best_d2 = d2
                best_pid = pid

        return best_pid
