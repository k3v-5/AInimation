"""
Motion Blur & Shutter Velocity for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from .core import ensure_finite_scalar, ensure_finite_vec3


@dataclass
class MotionBlurSettings:
    """
    Cinematic Motion Blur based on physical camera shutter angle.
    """
    enabled: bool = False
    amount: float = 0.5                  # Shutter angle fraction: 0.5 = 180 deg, 1.0 = 360 deg
    max_distortion_percent: float = 5.0  # Max blur vector length in screen percentage
    camera_motion_blur: bool = True
    per_object_motion_blur: bool = True

    def __post_init__(self) -> None:
        self.amount = max(0.0, min(1.0, ensure_finite_scalar(self.amount, "amount", 0.5)))
        self.max_distortion_percent = max(0.0, min(100.0, ensure_finite_scalar(self.max_distortion_percent, "max_distortion_percent", 5.0)))

    def evaluate_blur_vector(
        self,
        linear_velocity: Tuple[float, float, float],
        dt: float
    ) -> Tuple[float, float, float]:
        """Calculates effective motion blur displacement vector scaled by shutter time."""
        if not self.enabled or dt <= 0.0:
            return (0.0, 0.0, 0.0)
        # Exposure duration = shutter fraction * dt
        shutter_time = self.amount * dt
        vx = linear_velocity[0] * shutter_time
        vy = linear_velocity[1] * shutter_time
        vz = linear_velocity[2] * shutter_time
        return (round(vx, 6), round(vy, 6), round(vz, 6))
