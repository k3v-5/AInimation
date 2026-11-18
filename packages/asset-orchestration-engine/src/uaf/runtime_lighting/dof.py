"""
Depth of Field & Circle of Confusion (CoC) for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass

from .core import ensure_finite_scalar


@dataclass
class DOFSettings:
    """
    Cinematic Depth of Field based on physical camera thin-lens model.
    """
    enabled: bool = False
    focus_distance: float = 3.0          # Focus plane in meters (Df)
    focal_length: float = 50.0           # Lens focal length in mm (f)
    aperture_f_stop: float = 2.8         # Aperture f-number (N)
    sensor_width: float = 36.0           # Sensor width in mm (full frame 35mm)
    max_blur_radius_px: float = 32.0     # Max bokeh diameter in screen pixels

    def __post_init__(self) -> None:
        self.focus_distance = max(0.1, ensure_finite_scalar(self.focus_distance, "focus_distance", 3.0))
        self.focal_length = max(1.0, min(1000.0, ensure_finite_scalar(self.focal_length, "focal_length", 50.0)))
        self.aperture_f_stop = max(0.5, min(64.0, ensure_finite_scalar(self.aperture_f_stop, "aperture_f_stop", 2.8)))
        self.sensor_width = max(1.0, min(100.0, ensure_finite_scalar(self.sensor_width, "sensor_width", 36.0)))
        self.max_blur_radius_px = max(0.0, min(128.0, ensure_finite_scalar(self.max_blur_radius_px, "max_blur_radius_px", 32.0)))

    def calculate_coc(self, subject_distance_m: float, screen_width_px: int = 1920) -> float:
        """
        Calculates Circle of Confusion (CoC) diameter in pixels.
        CoC = abs(D - Df) / D * (f^2 / (N * (Df - f)))
        """
        if not self.enabled or self.max_blur_radius_px <= 0.0:
            return 0.0

        d = max(0.01, float(subject_distance_m))
        df = self.focus_distance
        f = self.focal_length * 0.001  # mm to m
        n = self.aperture_f_stop

        if df <= f:
            return 0.0

        # Physical aperture diameter A = f / N
        aperture_diam = f / n
        # Magnification factor
        coc_m = abs(d - df) / d * (f * f / (n * (df - f)))

        # Convert CoC from meters on sensor to screen pixels
        sensor_w_m = self.sensor_width * 0.001
        coc_px = (coc_m / sensor_w_m) * screen_width_px
        return round(min(self.max_blur_radius_px, max(0.0, coc_px)), 4)
