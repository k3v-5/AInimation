"""
UAF-81.97: Camera Trajectory & Catmull-Rom Spline Solver.
Evaluates C1-continuous spline trajectories across spatial control points and resolves
collision clearance against room walls, bounding volumes, and terrain elevation.
"""

import math
from typing import Dict, List, Optional, Tuple, Any

from ..core.contracts import (
    Vector3D,
    Rotator3D,
    Transform3D,
    CameraKeyframe,
)
from ..framing.framing_engine import CinematicFramingEngine


class BoundingBox3D:
    """Represents an axis-aligned bounding volume for collision avoidance."""

    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float, min_z: float, max_z: float):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_z = min_z
        self.max_z = max_z

    def contains(self, p: Vector3D, margin: float = 0.0) -> bool:
        return (
            (self.min_x - margin) <= p.x <= (self.max_x + margin)
            and (self.min_y - margin) <= p.y <= (self.max_y + margin)
            and (self.min_z - margin) <= p.z <= (self.max_z + margin)
        )


class CameraTrajectorySolver:
    """
    Computes smooth, jerk-free spline flight paths for CineCameras with obstacle avoidance.
    """

    @staticmethod
    def evaluate_catmull_rom_point(
        p0: Vector3D,
        p1: Vector3D,
        p2: Vector3D,
        p3: Vector3D,
        t: float,
    ) -> Vector3D:
        """
        Standard cubic Catmull-Rom formula for parameter t in [0.0, 1.0].
        """
        t2 = t * t
        t3 = t2 * t

        # Basis coefficients
        b0 = -t3 + 2.0 * t2 - t
        b1 = 3.0 * t3 - 5.0 * t2 + 2.0
        b2 = -3.0 * t3 + 4.0 * t2 + t
        b3 = t3 - t2

        x = 0.5 * (p0.x * b0 + p1.x * b1 + p2.x * b2 + p3.x * b3)
        y = 0.5 * (p0.y * b0 + p1.y * b1 + p2.y * b2 + p3.y * b3)
        z = 0.5 * (p0.z * b0 + p1.z * b1 + p2.z * b2 + p3.z * b3)

        return Vector3D(x=round(x, 4), y=round(y, 4), z=round(z, 4))

    @staticmethod
    def evaluate_spline_path(
        control_points: List[Vector3D],
        samples_per_segment: int = 10,
    ) -> List[Vector3D]:
        """
        Evaluates a complete spline passing through all control points.
        """
        if len(control_points) < 2:
            return list(control_points)

        # Pad start and end
        padded = [control_points[0]] + list(control_points) + [control_points[-1]]

        path: List[Vector3D] = []
        num_segments = len(control_points) - 1

        for seg in range(num_segments):
            p0 = padded[seg]
            p1 = padded[seg + 1]
            p2 = padded[seg + 2]
            p3 = padded[seg + 3]

            for s in range(samples_per_segment):
                t = s / samples_per_segment
                pt = CameraTrajectorySolver.evaluate_catmull_rom_point(p0, p1, p2, p3, t)
                path.append(pt)

        path.append(control_points[-1])
        return path

    @staticmethod
    def apply_collision_avoidance(
        path: List[Vector3D],
        obstacles: List[BoundingBox3D],
        min_clearance_m: float = 0.5,
        min_ground_height_m: float = 0.3,
    ) -> List[Vector3D]:
        """
        Adjusts camera points outward from obstacle bounding boxes and pushes above ground plane.
        """
        corrected_path: List[Vector3D] = []

        for pt in path:
            p = pt.model_copy()

            # Enforce ground elevation clearance
            if p.z < min_ground_height_m:
                p.z = min_ground_height_m

            # Enforce bounding box obstacle avoidance
            for obs in obstacles:
                if obs.contains(p, margin=min_clearance_m):
                    # Push point to nearest boundary exterior
                    dist_left = abs(p.x - obs.min_x)
                    dist_right = abs(p.x - obs.max_x)
                    dist_front = abs(p.y - obs.min_y)
                    dist_back = abs(p.y - obs.max_y)
                    dist_top = abs(p.z - obs.max_z)

                    min_dist = min(dist_left, dist_right, dist_front, dist_back, dist_top)
                    if min_dist == dist_top:
                        p.z = obs.max_z + min_clearance_m
                    elif min_dist == dist_left:
                        p.x = obs.min_x - min_clearance_m
                    elif min_dist == dist_right:
                        p.x = obs.max_x + min_clearance_m
                    elif min_dist == dist_front:
                        p.y = obs.min_y - min_clearance_m
                    else:
                        p.y = obs.max_y + min_clearance_m

            corrected_path.append(p)

        return corrected_path

    @staticmethod
    def generate_spline_keyframes(
        control_points: List[Vector3D],
        target_focus_point: Vector3D,
        duration_s: float = 5.0,
        samples_count: int = 25,
        obstacles: Optional[List[BoundingBox3D]] = None,
        focal_length_mm: float = 35.0,
        aperture_fstop: float = 2.8,
    ) -> List[CameraKeyframe]:
        """
        Produces a sequence of CameraKeyframes along the collision-free Catmull-Rom spline.
        """
        samples_per_seg = max(2, samples_count // max(1, len(control_points) - 1))
        raw_path = CameraTrajectorySolver.evaluate_spline_path(control_points, samples_per_seg)

        if obstacles:
            final_path = CameraTrajectorySolver.apply_collision_avoidance(raw_path, obstacles)
        else:
            final_path = raw_path

        keyframes: List[CameraKeyframe] = []
        n_points = len(final_path)

        for i, pos in enumerate(final_path):
            fraction = i / max(1, n_points - 1)
            t_sec = round(fraction * duration_s, 3)

            rot = CinematicFramingEngine.compute_look_at_rotation(pos, target_focus_point)
            focus_dist = round(pos.distance_to(target_focus_point), 2)

            keyframes.append(
                CameraKeyframe(
                    time_seconds=t_sec,
                    transform=Transform3D(position=pos, rotation=rot),
                    focal_length_mm=focal_length_mm,
                    aperture_fstop=aperture_fstop,
                    focus_distance_m=focus_dist,
                )
            )

        return keyframes
