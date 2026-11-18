"""
UAF-81.82: Convex Polygon Geometry, Winding Validation, and Portal Mathematics.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from ..models.definition import (
    NavPolygon,
    Vec3,
    ensure_finite_float,
    ensure_finite_vec3,
    vec3_cross,
    vec3_distance_sq,
    vec3_dot,
    vec3_sub,
    vec3_add,
    vec3_scale,
    vec3_length,
)


def cross_product_2d_xz(v0: Vec3, v1: Vec3, v2: Vec3) -> float:
    """Compute 2D cross product in XZ horizontal plane: (v1 - v0) x (v2 - v1)."""
    dx1 = v1[0] - v0[0]
    dz1 = v1[2] - v0[2]
    dx2 = v2[0] - v1[0]
    dz2 = v2[2] - v1[2]
    return dx1 * dz2 - dz1 * dx2


def is_polygon_convex(vertices: Sequence[Vec3]) -> bool:
    """Verify that a polygon is strictly convex in the horizontal XZ plane."""
    n = len(vertices)
    if n < 3:
        return False

    sign = 0.0
    for i in range(n):
        v0 = vertices[i]
        v1 = vertices[(i + 1) % n]
        v2 = vertices[(i + 2) % n]
        cp = cross_product_2d_xz(v0, v1, v2)
        if abs(cp) > 1e-9:
            if sign == 0.0:
                sign = 1.0 if cp > 0 else -1.0
            elif (cp > 0 and sign < 0) or (cp < 0 and sign > 0):
                return False
    return sign != 0.0


def compute_polygon_area_2d(vertices: Sequence[Vec3]) -> float:
    """Compute 2D signed area in XZ plane using Gauss shoelace formula."""
    n = len(vertices)
    if n < 3:
        return 0.0
    area2 = 0.0
    for i in range(n):
        j = (i + 1) % n
        area2 += vertices[i][0] * vertices[j][2] - vertices[j][0] * vertices[i][2]
    return abs(area2) * 0.5


def is_point_inside_polygon_2d(point: Vec3, vertices: Sequence[Vec3], y_tolerance: float = 2.0) -> bool:
    """
    Check if a 3D point is inside a convex polygon in the XZ plane with Y elevation tolerance.
    """
    n = len(vertices)
    if n < 3:
        return False

    # Check Y elevation tolerance against polygon average Y
    avg_y = sum(v[1] for v in vertices) / n
    if abs(point[1] - avg_y) > y_tolerance:
        return False

    # All 2D cross products must have the same sign (or be on boundary)
    sign = 0.0
    for i in range(n):
        v0 = vertices[i]
        v1 = vertices[(i + 1) % n]
        cp = (v1[0] - v0[0]) * (point[2] - v0[2]) - (v1[2] - v0[2]) * (point[0] - v0[0])
        if abs(cp) > 1e-8:
            if sign == 0.0:
                sign = 1.0 if cp > 0 else -1.0
            elif (cp > 0 and sign < 0) or (cp < 0 and sign > 0):
                return False
    return True


def project_point_to_segment(p: Vec3, a: Vec3, b: Vec3) -> Vec3:
    """Project point p onto line segment ab."""
    ab = vec3_sub(b, a)
    l2 = vec3_dot(ab, ab)
    if l2 < 1e-12:
        return a
    ap = vec3_sub(p, a)
    t = max(0.0, min(1.0, vec3_dot(ap, ab) / l2))
    return vec3_add(a, vec3_scale(ab, t))


def closest_point_on_polygon(point: Vec3, vertices: Sequence[Vec3]) -> Vec3:
    """Find the closest point on the polygon surface to the given point."""
    if is_point_inside_polygon_2d(point, vertices):
        avg_y = sum(v[1] for v in vertices) / len(vertices)
        return (point[0], avg_y, point[2])

    # Find closest point among all perimeter edges
    best_pt = vertices[0]
    best_d2 = float("inf")
    n = len(vertices)
    for i in range(n):
        pt = project_point_to_segment(point, vertices[i], vertices[(i + 1) % n])
        d2 = vec3_distance_sq(point, pt)
        if d2 < best_d2:
            best_d2 = d2
            best_pt = pt
    return best_pt


def find_shared_edge(poly_a: NavPolygon, poly_b: NavPolygon, eps: float = 1e-4) -> Optional[Tuple[Vec3, Vec3]]:
    """
    Find the shared edge between two adjacent polygons.
    Returns (v_left, v_right) oriented from poly_a to poly_b.
    """
    verts_a = poly_a.vertices
    verts_b = poly_b.vertices
    na = len(verts_a)
    nb = len(verts_b)

    for i in range(na):
        ea0 = verts_a[i]
        ea1 = verts_a[(i + 1) % na]

        for j in range(nb):
            eb0 = verts_b[j]
            eb1 = verts_b[(j + 1) % nb]

            # In CCW polygons, shared edge runs in opposite direction
            d1 = vec3_distance_sq(ea0, eb1)
            d2 = vec3_distance_sq(ea1, eb0)
            if d1 < eps * eps and d2 < eps * eps:
                return (ea0, ea1)

            # Check matching in same direction as fallback
            d3 = vec3_distance_sq(ea0, eb0)
            d4 = vec3_distance_sq(ea1, eb1)
            if d3 < eps * eps and d4 < eps * eps:
                return (ea0, ea1)

    return None
