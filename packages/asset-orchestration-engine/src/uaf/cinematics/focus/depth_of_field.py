"""
UAF-81.97: Autofocus & Physical Depth of Field (DoF) Calculator.
Calculates optical focal distance, hyperfocal distance, near/far focus limits,
circle of confusion, and shot-based aperture recommendations.
"""

import math
from typing import Dict, Optional, Tuple, Any

from ..core.contracts import (
    Vector3D,
    LensSettings,
    FocusSettings,
    CinematicShotType,
)


class AutoFocusDepthOfField:
    """
    Computes physically grounded optical focus parameters for Unreal Engine CineCamera.
    """

    @staticmethod
    def compute_hyperfocal_distance_m(
        focal_length_mm: float,
        aperture_fstop: float,
        circle_of_confusion_mm: float = 0.03,
    ) -> float:
        """
        Computes the hyperfocal distance H (in meters):
        H = (f^2 / (N * c)) + f
        """
        f_m = focal_length_mm * 0.001
        c_m = circle_of_confusion_mm * 0.001
        n = max(0.5, aperture_fstop)

        h_m = (f_m ** 2) / (n * c_m) + f_m
        return round(h_m, 3)

    @staticmethod
    def compute_depth_of_field(
        subject_distance_m: float,
        focal_length_mm: float,
        aperture_fstop: float,
        circle_of_confusion_mm: float = 0.03,
    ) -> Dict[str, Any]:
        """
        Computes near focus limit, far focus limit, and total depth of field span.
        """
        d = max(0.05, subject_distance_m)
        h = AutoFocusDepthOfField.compute_hyperfocal_distance_m(
            focal_length_mm=focal_length_mm,
            aperture_fstop=aperture_fstop,
            circle_of_confusion_mm=circle_of_confusion_mm,
        )

        d_near = (h * d) / (h + d)

        if d >= h:
            d_far = float("inf")
            dof_total = float("inf")
        else:
            d_far = (h * d) / max(0.01, h - d)
            dof_total = d_far - d_near

        return {
            "subject_distance_m": round(d, 3),
            "hyperfocal_distance_m": h,
            "near_limit_m": round(d_near, 3),
            "far_limit_m": round(d_far, 3) if d_far != float("inf") else -1.0,
            "dof_total_m": round(dof_total, 3) if dof_total != float("inf") else -1.0,
            "is_infinite_dof": d >= h,
        }

    @staticmethod
    def recommend_aperture_for_shot(shot_type: CinematicShotType) -> float:
        """
        Selects standard cinematographic f-stop according to narrative shot intention.
        """
        if shot_type == CinematicShotType.CLOSE_UP:
            return 1.8  # Shallow bokeh to isolate subject
        elif shot_type in (CinematicShotType.OVER_THE_SHOULDER, CinematicShotType.SHOT_REVERSE_SHOT):
            return 2.8  # Moderate depth keeping speaker and listener context clear
        elif shot_type == CinematicShotType.ORBIT_BOSS_REVEAL:
            return 2.8  # Crisp subject with cinematographic soft background
        elif shot_type in (CinematicShotType.ESTABLISHING_SHOT, CinematicShotType.WIDE_ACTION):
            return 8.0  # Deep focus keeping large architecture and combat readable
        elif shot_type == CinematicShotType.DUTCH_ANGLE:
            return 2.4
        else:
            return 4.0

    @staticmethod
    def calculate_autofocus_tracking(
        cam_pos: Vector3D,
        target_pos: Vector3D,
        lens: LensSettings,
        shot_type: CinematicShotType = CinematicShotType.OVER_THE_SHOULDER,
    ) -> Dict[str, Any]:
        """
        Solves focus distance and recommended aperture for a given camera and target.
        """
        dist = cam_pos.distance_to(target_pos)
        recommended_fstop = AutoFocusDepthOfField.recommend_aperture_for_shot(shot_type)
        dof_info = AutoFocusDepthOfField.compute_depth_of_field(
            subject_distance_m=dist,
            focal_length_mm=lens.focal_length_mm,
            aperture_fstop=recommended_fstop,
        )

        return {
            "focus_distance_m": round(dist, 3),
            "recommended_fstop": recommended_fstop,
            "depth_of_field": dof_info,
        }
