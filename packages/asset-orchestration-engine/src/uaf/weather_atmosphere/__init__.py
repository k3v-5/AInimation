"""
UAF-81.100: Volumetric Weather Cycles, Dynamic Day/Night & Atmosphere.
Unifies ecological biomes, physical Rayleigh/Mie scattering, diurnal celestial cycles,
surface weather modifiers (wetness, puddles, snow, wind), and UE5 export pipelines.
"""

from .core.contracts import (
    WeatherBiomeType,
    PrecipitationType,
    CloudCoveragePreset,
    Vector3D,
    ColorRGB,
    SkyAtmosphereSpec,
    ExponentialHeightFogSpec,
    VolumetricCloudSpec,
    BiomeAtmosphereProfile,
    WeatherState,
    SurfaceWeatherModifier,
    MaterialParameterCollectionSpec,
    DiurnalKeyframe,
    WeatherSystemManifest,
)
from .core.profiles import (
    BIOME_PROFILE_REGISTRY,
    get_default_biome_profile,
    create_arctic_profile,
    create_tundra_profile,
    create_alpine_profile,
    create_temperate_forest_profile,
    create_desert_profile,
    create_swamp_profile,
    create_volcanic_profile,
    create_cyberpunk_neon_profile,
)
from .cycle.day_night_controller import DayNightCycleController
from .shaders.environmental_shader_blender import EnvironmentalShaderBlender
from .export.ue5_weather_exporter import UE5WeatherExporter

__all__ = [
    "WeatherBiomeType",
    "PrecipitationType",
    "CloudCoveragePreset",
    "Vector3D",
    "ColorRGB",
    "SkyAtmosphereSpec",
    "ExponentialHeightFogSpec",
    "VolumetricCloudSpec",
    "BiomeAtmosphereProfile",
    "WeatherState",
    "SurfaceWeatherModifier",
    "MaterialParameterCollectionSpec",
    "DiurnalKeyframe",
    "WeatherSystemManifest",
    "BIOME_PROFILE_REGISTRY",
    "get_default_biome_profile",
    "create_arctic_profile",
    "create_tundra_profile",
    "create_alpine_profile",
    "create_temperate_forest_profile",
    "create_desert_profile",
    "create_swamp_profile",
    "create_volcanic_profile",
    "create_cyberpunk_neon_profile",
    "DayNightCycleController",
    "EnvironmentalShaderBlender",
    "UE5WeatherExporter",
]
