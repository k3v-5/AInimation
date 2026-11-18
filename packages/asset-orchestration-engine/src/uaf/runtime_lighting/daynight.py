"""
Day/Night Controller & Astronomical Ephemeris for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Tuple

from .core import ensure_finite_scalar, normalize_vec3


class DayPeriod(str, Enum):
    NIGHT = "NIGHT"
    DAWN = "DAWN"
    MORNING = "MORNING"
    NOON = "NOON"
    AFTERNOON = "AFTERNOON"
    SUNSET = "SUNSET"
    DUSK = "DUSK"


@dataclass
class EphemerisData:
    """Astronomical coordinates and state of celestial bodies."""
    sun_azimuth_deg: float
    sun_elevation_deg: float
    sun_direction: Tuple[float, float, float]
    moon_azimuth_deg: float
    moon_elevation_deg: float
    moon_direction: Tuple[float, float, float]
    period: DayPeriod
    day_fraction: float


class DayNightController:
    """
    Decoupled time and astronomical controller computing solar and lunar ephemeris deterministically.
    """

    def __init__(
        self,
        latitude_deg: float = 34.05,
        longitude_deg: float = -118.25,
        day_of_year: int = 172,       # Summer solstice approx
        time_of_day_hours: float = 12.0,
        time_scale: float = 1.0,
    ) -> None:
        self.latitude_deg = max(-90.0, min(90.0, float(latitude_deg)))
        self.longitude_deg = max(-180.0, min(180.0, float(longitude_deg)))
        self.day_of_year = max(1, min(365, int(day_of_year)))
        self.time_of_day_hours = max(0.0, min(24.0, float(time_of_day_hours)))
        self.time_scale = max(0.0, float(time_scale))

        self.simulation_time: float = 0.0
        self.world_time_seconds: float = self.time_of_day_hours * 3600.0

    def tick(self, dt: float) -> EphemerisData:
        """Advances simulation and world time deterministically, then computes ephemeris."""
        self.simulation_time += dt
        self.world_time_seconds = (self.world_time_seconds + dt * self.time_scale) % 86400.0
        self.time_of_day_hours = self.world_time_seconds / 3600.0
        return self.compute_ephemeris()

    def set_time_of_day(self, hours: float) -> EphemerisData:
        """Directly sets the time of day in hours [0.0, 24.0)."""
        self.time_of_day_hours = hours % 24.0
        self.world_time_seconds = self.time_of_day_hours * 3600.0
        return self.compute_ephemeris()

    def compute_ephemeris(self) -> EphemerisData:
        """
        Calculates exact solar and lunar positions using standard spherical trigonometry.
        """
        lat_rad = math.radians(self.latitude_deg)

        # Solar declination angle delta
        # delta = 23.45 * sin(360/365 * (284 + day))
        declination_deg = 23.45 * math.sin(math.radians((360.0 / 365.0) * (284 + self.day_of_year)))
        decl_rad = math.radians(declination_deg)

        # Hour angle H: 15 degrees per hour from solar noon (12:00)
        hour_angle_deg = 15.0 * (self.time_of_day_hours - 12.0)
        h_rad = math.radians(hour_angle_deg)

        # Solar elevation angle: sin(el) = sin(lat)*sin(decl) + cos(lat)*cos(decl)*cos(H)
        sin_elev = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(h_rad)
        sin_elev = max(-1.0, min(1.0, sin_elev))
        sun_elev_rad = math.asin(sin_elev)
        sun_elev_deg = math.degrees(sun_elev_rad)

        # Solar azimuth angle: cos(az) = (sin(decl) - sin(lat)*sin(el)) / (cos(lat)*cos(el))
        cos_elev = math.cos(sun_elev_rad)
        if abs(cos_elev) > 1e-5:
            cos_az = (math.sin(decl_rad) - math.sin(lat_rad) * sin_elev) / (math.cos(lat_rad) * cos_elev)
            cos_az = max(-1.0, min(1.0, cos_az))
            sun_az_deg = math.degrees(math.acos(cos_az))
            if hour_angle_deg > 0:
                sun_az_deg = 360.0 - sun_az_deg
        else:
            sun_az_deg = 180.0

        # Convert spherical to light travel direction (vector pointing from sun to scene)
        # Vector on sky dome pointing to sun:
        sx = math.sin(math.radians(sun_az_deg)) * math.cos(sun_elev_rad)
        sy = math.sin(sun_elev_rad)
        sz = math.cos(math.radians(sun_az_deg)) * math.cos(sun_elev_rad)
        # Light travels in reverse direction (-sx, -sy, -sz)
        sun_light_dir = normalize_vec3((-sx, -sy, -sz))

        # Moon is approximately opposite to Sun on celestial sphere
        moon_elev_deg = -sun_elev_deg
        moon_az_deg = (sun_az_deg + 180.0) % 360.0
        moon_elev_rad = math.radians(moon_elev_deg)
        mx = math.sin(math.radians(moon_az_deg)) * math.cos(moon_elev_rad)
        my = math.sin(moon_elev_rad)
        mz = math.cos(math.radians(moon_az_deg)) * math.cos(moon_elev_rad)
        moon_light_dir = normalize_vec3((-mx, -my, -mz))

        # Determine period
        if sun_elev_deg < -12.0:
            period = DayPeriod.NIGHT
        elif -12.0 <= sun_elev_deg < 0.0:
            period = DayPeriod.DAWN if self.time_of_day_hours < 12.0 else DayPeriod.DUSK
        elif 0.0 <= sun_elev_deg < 15.0:
            period = DayPeriod.DAWN if self.time_of_day_hours < 12.0 else DayPeriod.SUNSET
        elif 15.0 <= sun_elev_deg < 45.0:
            period = DayPeriod.MORNING if self.time_of_day_hours < 12.0 else DayPeriod.AFTERNOON
        else:
            period = DayPeriod.NOON

        return EphemerisData(
            sun_azimuth_deg=round(sun_az_deg, 4),
            sun_elevation_deg=round(sun_elev_deg, 4),
            sun_direction=sun_light_dir,
            moon_azimuth_deg=round(moon_az_deg, 4),
            moon_elevation_deg=round(moon_elev_deg, 4),
            moon_direction=moon_light_dir,
            period=period,
            day_fraction=round(self.time_of_day_hours / 24.0, 6),
        )
