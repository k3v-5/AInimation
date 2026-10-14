"""
CineCamera Choreographer for Unreal Engine 5.

Generates beat-synced cinematics and camera motion tracks aligned with audio
onset grids and music rhythm cues. Supports 5 cinematic presets:
smooth_orbit, dramatic_orbit, aerial_pan, front_close, and spiral_ascent.

100% Zero-Any compliant with Pydantic v2 strict models.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple, Union

from backend.core.models import CameraKeyframe, Vector3D


class CineCameraChoreographer:
    """
    Choreographs procedural CineCamera movements driven by musical beat timestamps.
    Provides mathematical Look-At tracking, physical FOV/distance clamping, and
    fallbacks for empty or out-of-bounds beat grids.
    """

    def __init__(self, default_fov: float = 45.0, distance: float = 400.0) -> None:
        self.default_fov: float = max(10.0, min(120.0, default_fov))
        self.distance: float = max(50.0, distance)

    @staticmethod
    def calculate_look_at(cam_pos: Vector3D, target_pos: Vector3D) -> Tuple[float, float]:
        """
        Compute camera Pitch and Yaw to face a 3D target point in Unreal coordinates.
        Unreal Engine coordinate system: X forward, Y right, Z up.

        Returns:
            Tuple of (pitch_degrees, yaw_degrees).
        """
        dx = target_pos.x - cam_pos.x
        dy = target_pos.y - cam_pos.y
        dz = target_pos.z - cam_pos.z
        dist_xy = math.hypot(dx, dy)

        yaw = math.degrees(math.atan2(dy, dx))
        pitch = math.degrees(math.atan2(dz, max(1e-5, dist_xy)))
        return round(pitch, 2), round(yaw, 2)

    def generate_track(
        self,
        beat_timestamps: List[float],
        total_duration: float,
        preset: str = "smooth_orbit",
        center_z: float = 120.0,
    ) -> List[CameraKeyframe]:
        """
        Generate camera keyframes synchronized to audio beats.

        Args:
            beat_timestamps: List of timestamp markers in seconds.
            total_duration: Total sequence duration in seconds.
            preset: Motion preset ('smooth_orbit', 'dramatic_orbit', 'aerial_pan', 'front_close', 'spiral_ascent').
            center_z: Focal tracking height in centimeters (Z-axis).

        Returns:
            List of strictly validated CameraKeyframe objects.
        """
        duration = max(0.1, float(total_duration))
        keyframes: List[CameraKeyframe] = []
        target = Vector3D(x=0.0, y=0.0, z=center_z)
        target_pos = target

        # Filter and sort beats within [0.0, duration]
        sorted_beats = sorted([b for b in beat_timestamps if 0.0 <= b <= duration])

        # Fallback if beat list is empty: create start and end boundary keyframes
        if not sorted_beats:
            cam_start = Vector3D(x=0.0, y=-self.distance, z=center_z)
            p_start, y_start = self.calculate_look_at(cam_start, target)
            keyframes.append(
                CameraKeyframe(
                    time=0.0,
                    x=cam_start.x,
                    y=cam_start.y,
                    z=cam_start.z,
                    pitch=p_start,
                    yaw=y_start,
                    roll=0.0,
                    fov=self.default_fov,
                    focal_length=35.0,
                    aperture=2.8,
                    focus_distance=self.distance,
                )
            )

            cam_end = Vector3D(x=self.distance * 0.5, y=-self.distance * 0.866, z=center_z + 20.0)
            p_end, y_end = self.calculate_look_at(cam_end, target)
            keyframes.append(
                CameraKeyframe(
                    time=round(duration, 4),
                    x=round(cam_end.x, 2),
                    y=round(cam_end.y, 2),
                    z=round(cam_end.z, 2),
                    pitch=p_end,
                    yaw=y_end,
                    roll=0.0,
                    fov=self.default_fov,
                    focal_length=35.0,
                    aperture=2.8,
                    focus_distance=round(math.hypot(cam_end.x, cam_end.y), 2),
                )
            )
            return keyframes

        # Ensure start keyframe at 0.0
        if sorted_beats[0] > 0.05:
            sorted_beats.insert(0, 0.0)
        # Ensure ending keyframe at total_duration
        if sorted_beats[-1] < duration - 0.05:
            sorted_beats.append(duration)

        for i, t in enumerate(sorted_beats):
            progress = t / duration if duration > 0 else 0.0

            if preset == "dramatic_orbit":
                angle = progress * 2.0 * math.pi
                radius = self.distance * (0.8 + 0.4 * math.sin(angle * 2.0))
                x = radius * math.sin(angle)
                y = -radius * math.cos(angle)
                z = center_z + 40.0 * math.sin(angle * 3.0)
                cam_pos = Vector3D(x=x, y=y, z=z)
                base_pitch, base_yaw = self.calculate_look_at(cam_pos, target)
                pitch = base_pitch + 8.0 * math.sin(angle * 2.0)
                yaw = (base_yaw + 360.0) % 360.0
                fov = self.default_fov + (5.0 if i % 2 == 0 else -5.0)

            elif preset == "aerial_pan":
                x = (progress - 0.5) * self.distance * 1.5
                y = -self.distance * 0.9
                z = center_z + 200.0 - 50.0 * progress
                pitch = -25.0
                yaw = 15.0 * math.sin(progress * math.pi)
                fov = self.default_fov + 10.0

            elif preset == "front_close":
                x = 0.0 + 20.0 * math.sin(progress * math.pi * 4.0)
                y = -self.distance * 0.5
                z = center_z + 10.0 * math.cos(progress * math.pi * 2.0)
                pitch, yaw = self.calculate_look_at(Vector3D(x=x, y=y, z=z), target_pos)
                fov = max(25.0, self.default_fov - 15.0)

            elif preset == "spiral_ascent":
                angle = progress * 3.0 * math.pi
                radius = self.distance * (1.0 - 0.2 * progress)
                x = radius * math.sin(angle)
                y = -radius * math.cos(angle)
                z = center_z - 30.0 + 150.0 * progress
                cam_pos = Vector3D(x=x, y=y, z=z)
                pitch, yaw = self.calculate_look_at(cam_pos, target)
                fov = self.default_fov

            else:  # Default 'smooth_orbit'
                angle = progress * math.pi * 1.5
                x = self.distance * math.sin(angle)
                y = -self.distance * math.cos(angle)
                z = center_z + 20.0 * math.sin(progress * math.pi)
                cam_pos = Vector3D(x=x, y=y, z=z)
                pitch, yaw = self.calculate_look_at(cam_pos, target)
                fov = self.default_fov

            # Compute physical focus distance to center target
            focus_dist = round(math.sqrt(x * x + y * y + (z - center_z) ** 2), 2)
            focal_len = round(36.0 / (2.0 * math.tan(math.radians(max(10.0, min(120.0, fov)) / 2.0))), 1)

            kf = CameraKeyframe(
                time=round(t, 4),
                x=round(x, 2),
                y=round(y, 2),
                z=round(z, 2),
                pitch=round(pitch, 2),
                yaw=round(yaw, 2),
                roll=0.0,
                fov=round(max(10.0, min(120.0, fov)), 1),
                focal_length=focal_len,
                aperture=2.8,
                focus_distance=max(50.0, focus_dist),
            )
            keyframes.append(kf)

        return keyframes


def generate_camera_track(
    beat_timestamps: List[float],
    total_duration: float,
    preset: str = "smooth_orbit",
    default_fov: float = 45.0,
    distance: float = 400.0,
) -> List[CameraKeyframe]:
    """
    Functional facade for generating a CineCamera choreography track.
    """
    choreographer = CineCameraChoreographer(default_fov=default_fov, distance=distance)
    return choreographer.generate_track(
        beat_timestamps=beat_timestamps,
        total_duration=total_duration,
        preset=preset,
    )
