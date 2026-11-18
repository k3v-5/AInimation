"""
Procedural Sky System & Celestial Coordinator for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .sun import Sun
from .moon import Moon
from .daynight import DayNightController, DayPeriod, EphemerisData
from .core import kelvin_to_rgb


@dataclass
class SkySystem:
    """
    Coordinates procedural sky dome, sun, moon, and time-of-day progression.
    """
    sun: Sun = field(default_factory=Sun)
    moon: Moon = field(default_factory=Moon)
    controller: DayNightController = field(default_factory=DayNightController)

    # Sky dome parameters
    zenith_color: Tuple[float, float, float] = (0.05, 0.15, 0.4)
    horizon_color: Tuple[float, float, float] = (0.4, 0.6, 0.8)
    ground_color: Tuple[float, float, float] = (0.05, 0.05, 0.04)
    star_intensity: float = 1.0

    def update(self, dt: float) -> EphemerisData:
        """Updates ephemeris and aligns sun and moon light vectors."""
        eph = self.controller.tick(dt)
        self.sun.direction = eph.sun_direction
        self.moon.direction = eph.moon_direction

        # Adjust solar color temperature based on elevation
        elev = eph.sun_elevation_deg
        if elev < 0.0:
            # Below horizon
            self.sun.intensity = 0.0
            self.sun.temperature = 2500.0
        elif elev < 10.0:
            # Sunset / Sunrise reddening
            t = elev / 10.0
            self.sun.temperature = 2500.0 + t * 2500.0  # 2500K -> 5000K
            self.sun.intensity = 120000.0 * (t * 0.3)
        else:
            # Daylight
            self.sun.temperature = 5800.0
            self.sun.intensity = self.sun.get_solar_irradiance(elev)

        return eph

    def evaluate_sky_radiance(self, view_dir: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Computes analytical sky dome radiance in view direction.
        view_dir is normalized vector pointing from camera to sky.
        """
        vy = view_dir[1]
        sun_elev = self.controller.compute_ephemeris().sun_elevation_deg

        # Day factor [0.0 = night, 1.0 = noon]
        day_factor = max(0.0, min(1.0, (sun_elev + 5.0) / 45.0))

        if day_factor > 0.0:
            # Daytime / Sunset
            if sun_elev < 15.0:
                # Sunset orange/red horizon
                horizon = (0.8, 0.3, 0.1)
                zenith = (0.1, 0.15, 0.35)
            else:
                horizon = self.horizon_color
                zenith = self.zenith_color

            grad = max(0.0, min(1.0, vy))
            r = (zenith[0] * grad + horizon[0] * (1.0 - grad)) * day_factor
            g = (zenith[1] * grad + horizon[1] * (1.0 - grad)) * day_factor
            b = (zenith[2] * grad + horizon[2] * (1.0 - grad)) * day_factor
            return (round(r, 6), round(g, 6), round(b, 6))
        else:
            # Nighttime deep navy + stars
            night_sky = (0.002, 0.004, 0.01)
            grad = max(0.0, min(1.0, vy))
            return (
                round(night_sky[0] * grad, 6),
                round(night_sky[1] * grad, 6),
                round(night_sky[2] * grad, 6),
            )
