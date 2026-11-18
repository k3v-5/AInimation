"""
UAF-81.100: Environmental Shader Blender & Surface Weather Layering.
Simulates physical surface weather interaction: rainfall wetness accumulation,
thermodynamic drying, zenith-dependent snow deposition, puddle specular flattening,
and UE5 Material Parameter Collection (MPC_Weather) compilation.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

from uaf.weather_atmosphere.core.contracts import (
    BiomeAtmosphereProfile,
    ColorRGB,
    MaterialParameterCollectionSpec,
    PrecipitationType,
    SurfaceWeatherModifier,
    Vector3D,
    WeatherState,
)
from uaf.weather_atmosphere.cycle.day_night_controller import DayNightCycleController


class EnvironmentalShaderBlender:
    """
    Evaluates dynamic weather layers on scene surfaces and packages
    global weather parameters for Unreal Engine 5 materials.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def compute_slope_degrees(normal: Vector3D) -> float:
        """Computes surface slope angle in degrees relative to vertical Z-up normal."""
        norm = normal.normalize()
        # Cosine of angle with (0, 0, 1) is simply norm.z
        cos_theta = max(-1.0, min(1.0, norm.z))
        angle_rad = math.acos(cos_theta)
        return math.degrees(angle_rad)

    def accumulate_wetness(
        self,
        current_wetness: float,
        precip_type: PrecipitationType,
        intensity: float,
        temperature_c: float,
        humidity: float,
        slope_deg: float,
        delta_s: float,
    ) -> float:
        """
        Simulates rainfall water deposition and thermodynamic evaporation.
        Steep slopes shed water faster; horizontal surfaces retain moisture.
        """
        w = max(0.0, min(1.0, current_wetness))
        if delta_s <= 0.0:
            return w

        is_raining = precip_type in (PrecipitationType.LIGHT_RAIN, PrecipitationType.HEAVY_STORM)
        slope_rad = math.radians(min(89.0, slope_deg))

        if is_raining and intensity > 0.01:
            # Rain accumulation rate scaled by normal zenith angle (cos of slope)
            zenith_factor = max(0.1, math.cos(slope_rad))
            accumulation_rate = intensity * 0.15 * zenith_factor * delta_s
            w += accumulation_rate
        else:
            # Evaporation driven by temperature, vapor deficit, and slope drainage
            temp_factor = max(0.02, max(0.0, temperature_c) / 25.0)
            vapor_deficit = max(0.05, 1.0 - humidity)
            slope_drainage = 1.0 + 1.5 * math.sin(slope_rad)
            evaporation_rate = temp_factor * vapor_deficit * 0.04 * slope_drainage * delta_s
            w -= evaporation_rate

        return max(0.0, min(1.0, round(w, 4)))

    def compute_puddles(
        self,
        wetness: float,
        normal_z: float,
        slope_deg: float,
        noise_val: float = 0.5,
    ) -> Tuple[float, float, float]:
        """
        Calculates puddle accumulation on upward horizontal surfaces.
        Returns (puddle_coverage [0..1], puddle_depth_cm, normal_flatten_factor [0..1]).
        """
        # Puddles only settle on surfaces with slope < 25 degrees (normal_z > 0.90)
        if slope_deg > 25.0 or normal_z < 0.90 or wetness < 0.30:
            return (0.0, 0.0, 0.0)

        # Non-linear thresholding: puddles emerge once wetness exceeds 0.30
        threshold_factor = (wetness - 0.30) / 0.70
        slope_damping = max(0.0, 1.0 - (slope_deg / 25.0))
        noise_mod = 0.8 + 0.4 * max(0.0, min(1.0, noise_val))

        puddle_cov = max(0.0, min(1.0, threshold_factor * slope_damping * noise_mod))
        puddle_depth_cm = round(puddle_cov * 2.0, 2)  # Up to 2 cm puddle depth

        # Normal flattening: water surface tension levels ripples towards pure vertical (0, 0, 1)
        flatten_factor = round(puddle_cov * 0.96, 4)

        return (round(puddle_cov, 4), puddle_depth_cm, flatten_factor)

    def accumulate_snow(
        self,
        current_snow: float,
        precip_type: PrecipitationType,
        intensity: float,
        temperature_c: float,
        normal_z: float,
        slope_deg: float,
        delta_s: float,
    ) -> Tuple[float, float]:
        """
        Simulates subzero snow accumulation with zenith cutoff and thermodynamic melting.
        Returns (snow_coverage [0..1], snow_thickness_cm).
        """
        s = max(0.0, min(1.0, current_snow))
        if delta_s <= 0.0:
            return (s, round(s * 15.0, 2))

        is_snowing = precip_type in (PrecipitationType.SNOW, PrecipitationType.BLIZZARD)

        if temperature_c <= 0.0:
            if is_snowing and intensity > 0.01:
                # Zenith dot product cutoff: snow slides off steep cliffs (slope > 50 degrees)
                if slope_deg < 50.0 and normal_z > 0.60:
                    zenith_factor = math.cos(math.radians(slope_deg))
                    accumulation = intensity * 0.10 * zenith_factor * delta_s
                    s += accumulation
        else:
            # Melting above freezing point
            melting_rate = (temperature_c / 10.0) * 0.05 * delta_s
            s -= melting_rate

        s = max(0.0, min(1.0, round(s, 4)))
        thickness_cm = round(s * 15.0, 2)  # Up to 15 cm snow blanket
        return (s, thickness_cm)

    def evaluate_surface(
        self,
        world_pos: Vector3D,
        normal: Vector3D,
        weather: WeatherState,
        current_surface: Optional[SurfaceWeatherModifier] = None,
        delta_s: float = 1.0,
    ) -> SurfaceWeatherModifier:
        """
        Computes the complete weathered surface modifier for a mesh vertex or material pixel.
        """
        prev_wet = current_surface.wetness_amount if current_surface else 0.0
        prev_snow = current_surface.snow_coverage if current_surface else 0.0

        norm = normal.normalize()
        slope_deg = self.compute_slope_degrees(norm)

        # 1. Wetness
        wet = self.accumulate_wetness(
            current_wetness=prev_wet,
            precip_type=weather.precipitation_type,
            intensity=weather.precipitation_intensity,
            temperature_c=weather.temperature_celsius,
            humidity=weather.relative_humidity,
            slope_deg=slope_deg,
            delta_s=delta_s,
        )

        # 2. Puddles
        puddle_cov, puddle_depth, flatten_factor = self.compute_puddles(
            wetness=wet,
            normal_z=norm.z,
            slope_deg=slope_deg,
        )

        # 3. Snow
        snow_cov, snow_thick = self.accumulate_snow(
            current_snow=prev_snow,
            precip_type=weather.precipitation_type,
            intensity=weather.precipitation_intensity,
            temperature_c=weather.temperature_celsius,
            normal_z=norm.z,
            slope_deg=slope_deg,
            delta_s=delta_s,
        )

        # 4. Roughness modulation:
        # Water/puddles drop roughness down to 0.02 (specular mirror).
        # Snow increases roughness up to ~0.75.
        base_roughness = 1.0
        if puddle_cov > 0.05:
            roughness_mult = (1.0 - puddle_cov) * base_roughness + puddle_cov * 0.03
        elif wet > 0.05:
            roughness_mult = (1.0 - wet * 0.6) * base_roughness
        else:
            roughness_mult = base_roughness

        if snow_cov > 0.05:
            roughness_mult = (1.0 - snow_cov) * roughness_mult + snow_cov * 0.78

        # 5. Albedo darkening from water trapping (Fresnel internal reflections)
        albedo_darkening = 1.0 - 0.35 * wet * (1.0 - snow_cov)

        # 6. Wind displacement vector
        wind_speed = weather.wind_vector.length()
        wind_dir = weather.wind_vector.normalize()
        displacement = Vector3D(
            x=wind_dir.x * wind_speed * 0.05,
            y=wind_dir.y * wind_speed * 0.05,
            z=math.sin(world_pos.x * 0.1 + world_pos.y * 0.1) * 0.02 * wind_speed,
        )

        return SurfaceWeatherModifier(
            surface_id=current_surface.surface_id if current_surface else "surface_default",
            wetness_amount=wet,
            puddle_coverage=puddle_cov,
            puddle_depth_cm=puddle_depth,
            puddle_normal_flatten_factor=flatten_factor,
            snow_coverage=snow_cov,
            snow_thickness_cm=snow_thick,
            roughness_multiplier=round(roughness_mult, 4),
            albedo_darkening_factor=round(albedo_darkening, 4),
            wind_ripple_displacement=displacement,
        )

    def compile_mpc_parameters(
        self,
        weather: WeatherState,
        day_night: DayNightCycleController,
        atmosphere: BiomeAtmosphereProfile,
    ) -> MaterialParameterCollectionSpec:
        """
        Compiles scalar and vector parameters into a UE5 MaterialParameterCollection (MPC_Weather).
        """
        sun_elev, sun_az = day_night.compute_sun_position(weather.time_of_day_hours)
        moon_elev, moon_az = day_night.compute_moon_position(weather.time_of_day_hours)
        sun_lux = day_night.compute_solar_lux(sun_elev)
        moon_lux = day_night.compute_lunar_lux(moon_elev)
        kelvin = day_night.compute_sun_color_temperature(sun_elev)
        sun_rgb = day_night.kelvin_to_rgb(kelvin)
        total_lux = max(sun_lux + moon_lux, 0.05)
        ev100 = day_night.compute_ev100(total_lux)

        wind_speed = weather.wind_vector.length()
        wind_dir = weather.wind_vector.normalize()

        # Sun direction vector in UE5 world coordinates
        elev_rad = math.radians(sun_elev)
        az_rad = math.radians(sun_az)
        sun_dir_x = math.cos(elev_rad) * math.sin(az_rad)
        sun_dir_y = math.cos(elev_rad) * math.cos(az_rad)
        sun_dir_z = math.sin(elev_rad)

        # Moon direction vector
        m_elev_rad = math.radians(moon_elev)
        m_az_rad = math.radians(moon_az)
        moon_dir_x = math.cos(m_elev_rad) * math.sin(m_az_rad)
        moon_dir_y = math.cos(m_elev_rad) * math.cos(m_az_rad)
        moon_dir_z = math.sin(m_elev_rad)

        fog_color = atmosphere.height_fog.fog_inscattering_color

        scalars: Dict[str, float] = {
            "Weather_Wetness": round(0.8 if weather.is_precipitating and not weather.is_freezing else 0.0, 4),
            "Weather_PuddleAmount": round(0.6 if weather.precipitation_intensity > 0.5 and not weather.is_freezing else 0.0, 4),
            "Weather_SnowAmount": round(0.9 if weather.is_precipitating and weather.is_freezing else 0.0, 4),
            "Weather_WindSpeed": round(wind_speed, 2),
            "Weather_RainIntensity": round(weather.precipitation_intensity, 3),
            "Weather_TemperatureC": round(weather.temperature_celsius, 2),
            "Weather_RelativeHumidity": round(weather.relative_humidity, 3),
            "Weather_SunLux": round(sun_lux, 2),
            "Weather_MoonLux": round(moon_lux, 4),
            "Weather_EV100": round(ev100, 2),
            "Weather_FogDensity": round(atmosphere.height_fog.fog_density, 4),
        }

        vectors: Dict[str, Tuple[float, float, float, float]] = {
            "Weather_WindDirection": (round(wind_dir.x, 4), round(wind_dir.y, 4), round(wind_dir.z, 4), round(wind_speed, 2)),
            "Weather_SunDirection": (round(sun_dir_x, 4), round(sun_dir_y, 4), round(sun_dir_z, 4), round(sun_elev, 2)),
            "Weather_SunColor": (round(sun_rgb.r, 4), round(sun_rgb.g, 4), round(sun_rgb.b, 4), round(kelvin, 1)),
            "Weather_MoonDirection": (round(moon_dir_x, 4), round(moon_dir_y, 4), round(moon_dir_z, 4), round(moon_elev, 2)),
            "Weather_MoonColor": (0.65, 0.75, 0.90, 1.0),
            "Weather_FogColor": (round(fog_color.r, 4), round(fog_color.g, 4), round(fog_color.b, 4), round(atmosphere.height_fog.fog_density, 4)),
        }

        return MaterialParameterCollectionSpec(
            collection_name="MPC_Weather",
            scalar_parameters=scalars,
            vector_parameters=vectors,
        )
