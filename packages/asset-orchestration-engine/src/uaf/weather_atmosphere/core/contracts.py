"""
UAF-81.100: Core Atmospheric Contracts, Sky Profiles & Weather State Models.
Defines Pydantic v2 schemas for SkyAtmosphere, ExponentialHeightFog, VolumetricClouds,
photometric lighting parameters, environmental surface states, and UE5 Material Parameter Collections.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field, field_validator


class WeatherBiomeType(str, Enum):
    """Ecological and aesthetic biome classifications for atmospheric tuning."""
    ARCTIC = "ARCTIC"
    TUNDRA = "TUNDRA"
    ALPINE = "ALPINE"
    TEMPERATE_FOREST = "TEMPERATE_FOREST"
    DESERT = "DESERT"
    SWAMP = "SWAMP"
    VOLCANIC = "VOLCANIC"
    CYBERPUNK_NEON = "CYBERPUNK_NEON"


class PrecipitationType(str, Enum):
    """Categorization of active precipitation and atmospheric particulate fall."""
    NONE = "NONE"
    LIGHT_RAIN = "LIGHT_RAIN"
    HEAVY_STORM = "HEAVY_STORM"
    SNOW = "SNOW"
    BLIZZARD = "BLIZZARD"
    SANDSTORM = "SANDSTORM"
    ASH_FALL = "ASH_FALL"


class CloudCoveragePreset(str, Enum):
    """Standard cloud cover categories based on meteorological okta ratings."""
    CLEAR_SKY = "CLEAR_SKY"          # 0/8 oktas
    FEW_CLOUDS = "FEW_CLOUDS"        # 1-2/8 oktas
    SCATTERED = "SCATTERED"          # 3-4/8 oktas
    BROKEN_OVERCAST = "BROKEN_OVERCAST" # 5-7/8 oktas
    STORM_DENSE = "STORM_DENSE"      # 8/8 oktas


class Vector3D(BaseModel):
    """3D spatial vector with standard vector algebra and UE5 coordinate conversion."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self) -> Vector3D:
        mag = self.length()
        if mag < 1e-7:
            return Vector3D(x=0.0, y=0.0, z=0.0)
        return Vector3D(x=self.x / mag, y=self.y / mag, z=self.z / mag)

    def dot(self, other: Vector3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def to_ue5_cm(self) -> Vector3D:
        """Converts internal meters to Unreal Engine centimeters (1m = 100cm)."""
        return Vector3D(x=self.x * 100.0, y=self.y * 100.0, z=self.z * 100.0)

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


class ColorRGB(BaseModel):
    """Normalized linear floating-point RGB color [0.0, 1.0] with HDR support."""
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0

    @field_validator("r", "g", "b")
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        return max(0.0, float(v))

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.r, self.g, self.b)

    def to_ue5_linear(self) -> Dict[str, float]:
        return {"r": round(self.r, 4), "g": round(self.g, 4), "b": round(self.b, 4), "a": 1.0}


class SkyAtmosphereSpec(BaseModel):
    """
    Physical Rayleigh and Mie scattering profile for UE5 SkyAtmosphere component.
    Scattering coefficients are represented in 1/km.
    """
    rayleigh_scattering: ColorRGB = Field(
        default_factory=lambda: ColorRGB(r=0.05802, g=0.13558, b=0.33100),
        description="Rayleigh scattering coefficient per wavelength in 1/km"
    )
    rayleigh_scale_height_km: float = Field(default=8.0, ge=0.5, le=30.0)
    mie_scattering: float = Field(default=0.003996, ge=0.0, description="Mie scattering coefficient in 1/km")
    mie_absorption: float = Field(default=0.000444, ge=0.0, description="Mie absorption coefficient in 1/km")
    mie_anisotropy_g: float = Field(default=0.8, ge=-0.99, le=0.99, description="Phase function asymmetry parameter")
    multi_scattering_factor: float = Field(default=1.0, ge=0.0, le=2.0)
    absorption_coefficient: ColorRGB = Field(
        default_factory=lambda: ColorRGB(r=0.000650, g=0.001881, b=0.000085),
        description="Ozone layer absorption coefficient in 1/km"
    )
    ground_albedo: ColorRGB = Field(default_factory=lambda: ColorRGB(r=0.1, g=0.1, b=0.1))
    atmosphere_height_km: float = Field(default=60.0, ge=10.0, le=200.0)


class ExponentialHeightFogSpec(BaseModel):
    """
    Volumetric and planar height fog configuration for UE5 ExponentialHeightFog component.
    """
    fog_density: float = Field(default=0.02, ge=0.0, le=10.0)
    fog_height_falloff: float = Field(default=0.2, ge=0.001, le=5.0)
    fog_inscattering_color: ColorRGB = Field(
        default_factory=lambda: ColorRGB(r=0.45, g=0.55, b=0.65)
    )
    fog_max_opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    start_distance_cm: float = Field(default=0.0, ge=0.0)
    directional_inscattering_exponent: float = Field(default=4.0, ge=1.0, le=64.0)
    directional_inscattering_start_distance_cm: float = Field(default=10000.0, ge=0.0)
    volumetric_fog_enabled: bool = Field(default=True)
    volumetric_fog_scattering_distribution: float = Field(default=0.2, ge=-0.9, le=0.9)
    volumetric_fog_extinction_scale: float = Field(default=1.0, ge=0.1, le=10.0)
    volumetric_fog_distance_cm: float = Field(default=6000.0, ge=500.0, le=50000.0)


class VolumetricCloudSpec(BaseModel):
    """
    Volumetric cloud layer definition matching UE5 VolumetricCloudComponent.
    """
    layer_bottom_altitude_km: float = Field(default=1.5, ge=0.1, le=20.0)
    layer_height_km: float = Field(default=4.0, ge=0.5, le=25.0)
    cloud_coverage: float = Field(default=0.4, ge=0.0, le=1.0)
    density_multiplier: float = Field(default=0.8, ge=0.0, le=10.0)
    tracing_max_distance_km: float = Field(default=50.0, ge=5.0, le=200.0)
    view_sample_count_scale: float = Field(default=1.0, ge=0.25, le=4.0)
    shadow_tracing_distance_km: float = Field(default=15.0, ge=1.0, le=50.0)
    precipitation_probability: float = Field(default=0.2, ge=0.0, le=1.0)


class BiomeAtmosphereProfile(BaseModel):
    """Complete atmospheric profile bundle tailored for a specific ecological biome."""
    biome: WeatherBiomeType
    name: str
    sky_atmosphere: SkyAtmosphereSpec
    height_fog: ExponentialHeightFogSpec
    volumetric_clouds: VolumetricCloudSpec
    default_temperature_celsius: float = Field(default=20.0)
    base_humidity: float = Field(default=0.5, ge=0.0, le=1.0)
    prevailing_wind: Vector3D = Field(default_factory=lambda: Vector3D(x=5.0, y=2.0, z=0.0))
    typical_precipitations: List[PrecipitationType] = Field(
        default_factory=lambda: [PrecipitationType.NONE, PrecipitationType.LIGHT_RAIN]
    )


class WeatherState(BaseModel):
    """
    Dynamic runtime meteorological snapshot driving active shaders and lighting.
    """
    time_of_day_hours: float = Field(default=12.0, ge=0.0, le=24.0)
    precipitation_type: PrecipitationType = Field(default=PrecipitationType.NONE)
    precipitation_intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    temperature_celsius: float = Field(default=20.0)
    relative_humidity: float = Field(default=0.5, ge=0.0, le=1.0)
    wind_vector: Vector3D = Field(default_factory=lambda: Vector3D(x=5.0, y=2.0, z=0.0))
    barometric_pressure_hpa: float = Field(default=1013.25, ge=800.0, le=1100.0)

    @property
    def is_precipitating(self) -> bool:
        return self.precipitation_type != PrecipitationType.NONE and self.precipitation_intensity > 0.01

    @property
    def is_freezing(self) -> bool:
        return self.temperature_celsius <= 0.0


class SurfaceWeatherModifier(BaseModel):
    """
    Evaluated local surface parameters used to modulate material roughness, albedo, and normals.
    """
    surface_id: str = "surface_default"
    wetness_amount: float = Field(default=0.0, ge=0.0, le=1.0)
    puddle_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    puddle_depth_cm: float = Field(default=0.0, ge=0.0)
    puddle_normal_flatten_factor: float = Field(default=0.0, ge=0.0, le=1.0)
    snow_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    snow_thickness_cm: float = Field(default=0.0, ge=0.0)
    roughness_multiplier: float = Field(default=1.0, ge=0.0, le=2.0)
    albedo_darkening_factor: float = Field(default=1.0, ge=0.1, le=1.0)
    wind_ripple_displacement: Vector3D = Field(default_factory=Vector3D)


class MaterialParameterCollectionSpec(BaseModel):
    """
    Schema representing Unreal Engine 5 MaterialParameterCollection (MPC_Weather).
    """
    collection_name: str = "MPC_Weather"
    scalar_parameters: Dict[str, float] = Field(default_factory=dict)
    vector_parameters: Dict[str, Tuple[float, float, float, float]] = Field(default_factory=dict)


class DiurnalKeyframe(BaseModel):
    """Discrete keyframe along the 24-hour celestial trajectory for Sequencer / Curves."""
    hour: float
    sun_elevation_deg: float
    sun_azimuth_deg: float
    sun_lux: float
    sun_kelvin: float
    sun_color: ColorRGB
    moon_elevation_deg: float
    moon_azimuth_deg: float
    moon_lux: float
    fog_density: float
    ev100: float


class WeatherSystemManifest(BaseModel):
    """Complete root manifest bundling all atmospheric presets and runtime metadata."""
    manifest_id: str
    active_biome: WeatherBiomeType
    atmosphere_profile: BiomeAtmosphereProfile
    initial_weather: WeatherState
    diurnal_track: List[DiurnalKeyframe] = Field(default_factory=list)
    mpc_spec: MaterialParameterCollectionSpec
    ue5_version: str = "5.4"
