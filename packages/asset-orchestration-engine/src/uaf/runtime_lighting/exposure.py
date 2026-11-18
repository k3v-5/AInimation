"""
HDR Exposure & Eye Adaptation for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any, Dict

from .core import ExposureMode, ensure_finite_scalar, luminance_to_ev100, ev100_to_luminance


@dataclass
class ExposureSettings:
    """
    Physical camera exposure and automatic eye adaptation settings.
    """
    mode: ExposureMode = ExposureMode.AUTOMATIC
    fixed_ev100: float = 9.0                    # Used when mode == MANUAL
    min_ev100: float = -2.0                     # Darkest scene adaptation limit
    max_ev100: float = 16.0                     # Brightest scene adaptation limit
    compensation: float = 0.0                   # Exposure compensation in EV stops
    adaptation_speed_up: float = 3.0            # Adaptation speed towards brighter scenes
    adaptation_speed_down: float = 1.5          # Adaptation speed towards darker scenes
    current_ev100: float = 9.0

    def __post_init__(self) -> None:
        self.fixed_ev100 = ensure_finite_scalar(self.fixed_ev100, "fixed_ev100", 9.0)
        self.min_ev100 = ensure_finite_scalar(self.min_ev100, "min_ev100", -2.0)
        self.max_ev100 = max(self.min_ev100 + 0.1, ensure_finite_scalar(self.max_ev100, "max_ev100", 16.0))
        self.compensation = ensure_finite_scalar(self.compensation, "compensation", 0.0)
        self.adaptation_speed_up = max(0.01, ensure_finite_scalar(self.adaptation_speed_up, "adaptation_speed_up", 3.0))
        self.adaptation_speed_down = max(0.01, ensure_finite_scalar(self.adaptation_speed_down, "adaptation_speed_down", 1.5))
        self.current_ev100 = max(self.min_ev100, min(self.max_ev100, self.current_ev100))

    def evaluate_exposure(self, scene_average_luminance: float, dt: float) -> float:
        """
        Updates exposure dynamically with temporal eye adaptation.
        Returns the linear exposure scale factor applied to scene radiance.
        """
        if self.mode == ExposureMode.MANUAL:
            target_ev = self.fixed_ev100
        else:
            # Automatic EV from average scene luminance
            avg_lum = max(1e-5, scene_average_luminance)
            target_ev = luminance_to_ev100(avg_lum)
            target_ev = max(self.min_ev100, min(self.max_ev100, target_ev))

        target_ev += self.compensation

        # Temporal adaptation
        if dt > 0.0:
            diff = target_ev - self.current_ev100
            speed = self.adaptation_speed_up if diff > 0.0 else self.adaptation_speed_down
            # Exponential smooth interpolation: ev = ev + diff * (1 - exp(-speed * dt))
            factor = 1.0 - math.exp(-speed * dt)
            self.current_ev100 += diff * factor
        else:
            self.current_ev100 = target_ev

        # Exposure scale = 1.0 / (1.2 * 2^EV100)
        ev_linear = 2.0 ** self.current_ev100
        exposure_scale = 1.0 / max(1e-6, 1.2 * ev_linear)
        return exposure_scale
