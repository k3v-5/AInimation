"""
UAF-81.82: Deterministic Funnel Algorithm (String Pulling) for Path Smoothing.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from ..models.definition import Portal, Vec3, vec3_distance_sq


def tri_area_2d(a: Vec3, b: Vec3, c: Vec3) -> float:
    """Compute signed 2D triangle area (cross product z-component in XZ plane)."""
    return (b[0] - a[0]) * (c[2] - a[2]) - (c[0] - a[0]) * (b[2] - a[2])


class FunnelAlgorithm:
    """
    String pulling / Funnel algorithm.
    Takes a sequence of portals produced by A* and generates a minimal-length,
    smoothed piecewise-linear path strictly contained within the polygon corridor.
    """

    @staticmethod
    def smooth_path(start_point: Vec3, portals: Sequence[Portal], goal_point: Vec3) -> Tuple[Vec3, ...]:
        """Produce smoothed 3D waypoints through the portal sequence."""
        if not portals:
            return (start_point, goal_point)

        # Build list of portal endpoints (left, right) with goal at the end
        pts_left: List[Vec3] = [p.left for p in portals] + [goal_point]
        pts_right: List[Vec3] = [p.right for p in portals] + [goal_point]

        num_portals = len(pts_left)

        path: List[Vec3] = [start_point]

        portal_apex: Vec3 = start_point
        portal_left: Vec3 = pts_left[0]
        portal_right: Vec3 = pts_right[0]

        apex_idx = 0
        left_idx = 0
        right_idx = 0

        i = 1
        while i < num_portals:
            left = pts_left[i]
            right = pts_right[i]

            # 1. Update Right vertex
            if tri_area_2d(portal_apex, portal_right, right) <= 0.0:
                if portal_apex == portal_right or tri_area_2d(portal_apex, portal_left, right) > 0.0:
                    # Tighten funnel to the right
                    portal_right = right
                    right_idx = i
                else:
                    # Right crossed Left -> Apex moves to Left
                    if vec3_distance_sq(path[-1], portal_left) > 1e-6:
                        path.append(portal_left)
                    portal_apex = portal_left
                    apex_idx = left_idx
                    # Reset portal
                    portal_left = portal_apex
                    portal_right = portal_apex
                    left_idx = apex_idx
                    right_idx = apex_idx
                    # Restart from next portal after apex
                    i = apex_idx + 1
                    continue

            # 2. Update Left vertex
            if tri_area_2d(portal_apex, portal_left, left) >= 0.0:
                if portal_apex == portal_left or tri_area_2d(portal_apex, portal_right, left) < 0.0:
                    # Tighten funnel to the left
                    portal_left = left
                    left_idx = i
                else:
                    # Left crossed Right -> Apex moves to Right
                    if vec3_distance_sq(path[-1], portal_right) > 1e-6:
                        path.append(portal_right)
                    portal_apex = portal_right
                    apex_idx = right_idx
                    # Reset portal
                    portal_left = portal_apex
                    portal_right = portal_apex
                    left_idx = apex_idx
                    right_idx = apex_idx
                    # Restart from next portal after apex
                    i = apex_idx + 1
                    continue

            i += 1

        if vec3_distance_sq(path[-1], goal_point) > 1e-6:
            path.append(goal_point)

        return tuple(path)
