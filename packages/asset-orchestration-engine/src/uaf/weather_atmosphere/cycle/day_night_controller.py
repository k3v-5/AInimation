"""
UAF-81.100: Celestial Trajectory, Day/Night Cycle & Photometric Photometry.
Computes solar and lunar positions, physical Rayleigh/Mie airmass attenuation,
Kelvin-to-RGB color temperature, and eye adaptation EV100 curves across the 24h diurnal cycle.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from uaf.weather_atmosphere.core.contracts import (
    ColorRGB,
    DiurnalKeyframe,
    Vector3D,
)


class DayNightCycleController:
    """
    Manages continuous diurnal time progression, celestial mechanics,
    photometric illuminance calculations, and auto-exposure curves.
    """

    def __init__(
        self,
        initial_hour: float = 12.0,
        time_scale: float = 1.0,
        latitude_deg: float = 35.0,
        day_of_month: float = 15.0,
    ) -> None:
        self.time_of_day_hours: float = float(initial_hour % 24.0)
        self.time_scale: float = float(time_scale)
        self.latitude_deg: float = float(latitude_deg)
        self.day_of_month: float = float(day_of_month)
        self.is_paused: bool = False

        # Initialize current exposure with standard midday EV100
        midday_lux = self.compute_solar_lux(self.compute_sun_position(12.0)[0])
        self.current_ev100: float = self.compute_ev100(midday_lux)

    def set_time(self, hour: float) -> None:
        """Sets current time of day in hours [0.0, 24.0)."""
        self.time_of_day_hours = float(hour % 24.0)

    def pause(self) -> None:
        self.is_paused = True

    def resume(self) -> None:
        self.is_paused = False

    def toggle_pause(self) -> bool:
        self.is_paused = not self.is_paused
        return self.is_paused

    def set_time_scale(self, scale: float) -> None:
        self.time_scale = max(0.0, float(scale))

    def set_latitude(self, latitude_deg: float) -> None:
        self.latitude_deg = max(-90.0, min(90.0, float(latitude_deg)))

    def advance_time(self, delta_seconds: float) -> float:
        """
        Advances the diurnal cycle by delta_seconds scaled by time_scale.
        Returns the new time_of_day_hours.
        """
        if self.is_paused or delta_seconds <= 0.0:
            return self.time_of_day_hours

        delta_hours = (delta_seconds * self.time_scale) / 3600.0
        self.time_of_day_hours = (self.time_of_day_hours + delta_hours) % 24.0

        delta_days = (delta_seconds * self.time_scale) / 86400.0
        self.day_of_month = (self.day_of_month + delta_days) % 29.53

        # Update eye adaptation toward target EV100
        sun_elev, _ = self.compute_sun_position(self.time_of_day_hours)
        moon_elev, _ = self.compute_moon_position(self.time_of_day_hours)
        sun_lux = self.compute_solar_lux(sun_elev)
        moon_lux = self.compute_lunar_lux(moon_elev)
        ambient_lux = max(sun_lux + moon_lux, 0.05)
        target_ev = self.compute_ev100(ambient_lux)
        self.current_ev100 = self.adapt_exposure(target_ev, self.current_ev100, delta_seconds)

        return self.time_of_day_hours

    def compute_sun_position(self, hour: Optional[float] = None) -> Tuple[float, float]:
        """
        Computes solar elevation and azimuth angles in degrees.
        Returns (elevation_deg, azimuth_deg).
        Elevation: -90° (nadir) to +90° (zenith).
        Azimuth: 0° (North), 90° (East), 180° (South), 270° (West).
        """
        h = self.time_of_day_hours if hour is None else float(hour % 24.0)

        # Solar hour angle: -180° at midnight, 0° at solar noon (12:00), +180° at next midnight
        hour_angle_deg = (h - 12.0) * 15.0
        hour_angle_rad = math.radians(hour_angle_deg)
        lat_rad = math.radians(self.latitude_deg)

        # Fixed mild declination for temperate season (~10°)
        declination_rad = math.radians(10.0)

        # Solar elevation
        sin_elev = math.sin(lat_rad) * math.sin(declination_rad) + math.cos(lat_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad)
        sin_elev = max(-1.0, min(1.0, sin_elev))
        elev_rad = math.asin(sin_elev)
        elev_deg = math.degrees(elev_rad)

        # Solar azimuth
        cos_elev = math.cos(elev_rad)
        if cos_elev < 1e-6:
            azimuth_deg = 180.0
        else:
            cos_az = (math.sin(declination_rad) - math.sin(lat_rad) * sin_elev) / (math.cos(lat_rad) * cos_elev)
            cos_az = max(-1.0, min(1.0, cos_az))
            az_raw = math.degrees(math.acos(cos_az))
            # If hour angle > 0 (afternoon/evening), azimuth is 360 - az_raw
            azimuth_deg = (360.0 - az_raw) if hour_angle_deg > 0 else az_raw

        return (round(elev_deg, 2), round(azimuth_deg, 2))

    def compute_moon_position(self, hour: Optional[float] = None) -> Tuple[float, float]:
        """
        Computes lunar elevation and azimuth angles in degrees.
        The moon roughly opposes the sun with an orbital inclination offset.
        """
        h = self.time_of_day_hours if hour is None else float(hour % 24.0)
        # Moon time is offset by 12 hours from the sun
        moon_hour = (h + 12.0) % 24.0

        hour_angle_deg = (moon_hour - 12.0) * 15.0
        hour_angle_rad = math.radians(hour_angle_deg)
        # Moon orbital inclination (+5.14 degrees)
        lat_rad = math.radians(self.latitude_deg + 5.14)
        declination_rad = math.radians(-10.0)

        sin_elev = math.sin(lat_rad) * math.sin(declination_rad) + math.cos(lat_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad)
        sin_elev = max(-1.0, min(1.0, sin_elev))
        elev_rad = math.asin(sin_elev)
        elev_deg = math.degrees(elev_rad)

        cos_elev = math.cos(elev_rad)
        if cos_elev < 1e-6:
            azimuth_deg = 0.0
        else:
            cos_az = (math.sin(declination_rad) - math.sin(lat_rad) * sin_elev) / (math.cos(lat_rad) * cos_elev)
            cos_az = max(-1.0, min(1.0, cos_az))
            az_raw = math.degrees(math.acos(cos_az))
            azimuth_deg = (360.0 - az_raw) if hour_angle_deg > 0 else az_raw

        return (round(elev_deg, 2), round(azimuth_deg, 2))

    def compute_moon_phase(self, day: Optional[float] = None) -> float:
        """
        Computes the illuminated fraction of the moon [0.0, 1.0].
        0.0 = New Moon, 0.5 = Quarter Moon, 1.0 = Full Moon.
        Synodic lunar period = 29.53 days.
        """
        d = self.day_of_month if day is None else float(day)
        phase_rad = 2.0 * math.pi * (d / 29.53)
        # 0.5 * (1 - cos(phase_rad)): at d=0 -> 0.0; at d=14.76 -> 1.0
        illum = 0.5 * (1.0 - math.cos(phase_rad))
        return max(0.0, min(1.0, round(illum, 4)))

    def compute_solar_lux(self, elevation_deg: float) -> float:
        """
        Computes direct clear-sky solar illuminance in Lux using Kasten-Young airmass extinction.
        Reaches ~110,000 to 120,000 Lux at solar zenith.
        """
        if elevation_deg <= -6.0:
            return 0.0
        elif elevation_deg <= 0.0:
            # Civil twilight transition (0 to 500 Lux)
            factor = (elevation_deg + 6.0) / 6.0
            return round(factor * 500.0, 2)

        elev_rad = math.radians(elevation_deg)
        # Kasten-Young optical airmass formula
        airmass = 1.0 / (math.sin(elev_rad) + 0.50572 * math.pow(elevation_deg + 6.07995, -1.6364))

        # Direct extraterrestrial solar constant in Lux (~120,000 Lux)
        i0_lux = 120000.0
        # Atmospheric transmittance: tau ~ 0.7^(m^0.678)
        transmittance = math.pow(0.70, math.pow(airmass, 0.678))
        direct_lux = i0_lux * transmittance

        return max(0.0, round(direct_lux, 2))

    def compute_lunar_lux(self, elevation_deg: float, moon_phase: Optional[float] = None) -> float:
        """
        Computes nocturnal lunar illuminance in Lux.
        Full moon at zenith delivers approximately 0.25 Lux.
        """
        if elevation_deg <= 0.0:
            return 0.0

        phase = self.compute_moon_phase() if moon_phase is None else max(0.0, min(1.0, float(moon_phase)))
        elev_rad = math.radians(elevation_deg)
        sin_elev = max(0.0, math.sin(elev_rad))

        max_lunar_lux = 0.25
        lunar_lux = max_lunar_lux * phase * sin_elev
        return max(0.0, round(lunar_lux, 4))

    @staticmethod
    def kelvin_to_rgb(kelvin: float) -> ColorRGB:
        """
        Converts correlated color temperature (Kelvin, 1000K to 12000K)
        to normalized linear RGB using the Tanner-Kang blackbody algorithm.
        """
        temp = max(1000.0, min(12000.0, float(kelvin))) / 100.0

        # Calculate Red
        if temp <= 66.0:
            r = 255.0
        else:
            r = 329.698727446 * math.pow(temp - 60.0, -0.1332047592)

        # Calculate Green
        if temp <= 66.0:
            g = 99.4708025861 * math.log(max(1.0, temp)) - 161.1195681661
        else:
            g = 288.1221695283 * math.pow(temp - 60.0, -0.0755148492)

        # Calculate Blue
        if temp >= 66.0:
            b = 255.0
        elif temp <= 19.0:
            b = 0.0
        else:
            b = 138.5177312231 * math.log(max(1.0, temp - 10.0)) - 305.0447927307

        # Clamp to [0, 255] and normalize to [0.0, 1.0]
        r_norm = max(0.0, min(1.0, r / 255.0))
        g_norm = max(0.0, min(1.0, g / 255.0))
        b_norm = max(0.0, min(1.0, b / 255.0))

        return ColorRGB(r=round(r_norm, 4), g=round(g_norm, 4), b=round(b_norm, 4))

    def compute_sun_color_temperature(self, elevation_deg: float) -> float:
        """
        Computes effective Correlated Color Temperature (CCT Kelvin)
        based on sun elevation angle above horizon.
        Dawn/Dusk: ~2000K - 3000K (golden hour amber).
        Zenith: ~5800K - 6500K (neutral sunlight).
        """
        if elevation_deg <= 0.0:
            return 2000.0
        elif elevation_deg <= 10.0:
            # Golden hour: 2000K -> 3500K
            t = elevation_deg / 10.0
            return round(2000.0 + t * 1500.0, 1)
        elif elevation_deg <= 45.0:
            # Morning / Afternoon transition: 3500K -> 5500K
            t = (elevation_deg - 10.0) / 35.0
            return round(3500.0 + t * 2000.0, 1)
        else:
            # Midday high elevation: 5500K -> 6500K
            t = (elevation_deg - 45.0) / 45.0
            return round(5500.0 + t * 1000.0, 1)

    @staticmethod
    def compute_ev100(illuminance_lux: float) -> float:
        """
        Computes standard Unreal Engine 5 physical Exposure Value at ISO 100 (EV100).
        Assumes 18% gray card average scene reflectance:
        Luminance L = (Lux * 0.18) / pi
        EV100 = log2( (L * 100) / 12.5 ) = log2( Lux * 0.458366 )
        """
        lux_clamped = max(1e-4, float(illuminance_lux))
        luminance = (lux_clamped * 0.18) / math.pi
        ev = math.log2((luminance * 100.0) / 12.5)
        return round(ev, 2)

    @staticmethod
    def adapt_exposure(
        target_ev100: float,
        current_ev100: float,
        delta_s: float,
        speed_up: float = 4.0,
        speed_down: float = 1.0,
    ) -> float:
        """
        Simulates asymmetric human eye pupil adaptation.
        Constriction (adjusting to brighter light) is faster than dilation (adjusting to dark).
        """
        if delta_s <= 0.0:
            return current_ev100

        rate = speed_up if target_ev100 > current_ev100 else speed_down
        blend = 1.0 - math.exp(-rate * delta_s)
        adapted = current_ev100 + (target_ev100 - current_ev100) * blend
        return round(adapted, 2)

    def generate_diurnal_track(self, steps_per_hour: int = 1) -> List[DiurnalKeyframe]:
        """
        Generates 24-hour keyframes with celestial positions, photometric lux,
        color temperatures, and exposure curves.
        """
        keyframes: List[DiurnalKeyframe] = []
        step_dt = 1.0 / max(1, steps_per_hour)
        total_steps = int(24.0 * steps_per_hour)

        for step in range(total_steps):
            h = step * step_dt
            sun_elev, sun_az = self.compute_sun_position(h)
            moon_elev, moon_az = self.compute_moon_position(h)
            sun_lux = self.compute_solar_lux(sun_elev)
            moon_lux = self.compute_lunar_lux(moon_elev)
            kelvin = self.compute_sun_color_temperature(sun_elev)
            sun_color = self.kelvin_to_rgb(kelvin)
            total_lux = max(sun_lux + moon_lux, 0.05)
            ev100 = self.compute_ev100(total_lux)

            # Modulate fog density slightly higher at dawn (dew/morning mist)
            dawn_factor = max(0.0, 1.0 - abs(h - 6.0) / 2.0)
            fog_density = round(0.02 + 0.015 * dawn_factor, 4)

            keyframes.append(
                DiurnalKeyframe(
                    hour=round(h, 2),
                    sun_elevation_deg=sun_elev,
                    sun_azimuth_deg=sun_az,
                    sun_lux=sun_lux,
                    sun_kelvin=kelvin,
                    sun_color=sun_color,
                    moon_elevation_deg=moon_elev,
                    moon_azimuth_deg=moon_az,
                    moon_lux=moon_lux,
                    fog_density=fog_density,
                    ev100=ev100,
                )
            )

        return keyframes
