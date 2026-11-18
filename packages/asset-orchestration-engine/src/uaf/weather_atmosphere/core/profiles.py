"""
UAF-81.100: Biome Atmospheric Profiles Factory & Registry.
Pre-calibrated profiles for ecological biomes: Arctic, Tundra, Alpine,
Temperate Forest, Desert, Swamp, Volcanic, and Cyberpunk Neon.
"""

from typing import Dict
from uaf.weather_atmosphere.core.contracts import (
    WeatherBiomeType,
    BiomeAtmosphereProfile,
    SkyAtmosphereSpec,
    ExponentialHeightFogSpec,
    VolumetricCloudSpec,
    ColorRGB,
    Vector3D,
    PrecipitationType,
)


def create_arctic_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.ARCTIC,
        name="Arctic Ice Field & Polar Vortex",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.045, g=0.12, b=0.38),
            rayleigh_scale_height_km=6.5,
            mie_scattering=0.006,
            mie_absorption=0.0003,
            mie_anisotropy_g=0.85,
            multi_scattering_factor=1.3,
            ground_albedo=ColorRGB(r=0.85, g=0.88, b=0.92),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.035,
            fog_height_falloff=0.15,
            fog_inscattering_color=ColorRGB(r=0.75, g=0.85, b=0.95),
            volumetric_fog_distance_cm=8000.0,
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=1.0,
            layer_height_km=3.0,
            cloud_coverage=0.65,
            density_multiplier=1.2,
            precipitation_probability=0.7,
        ),
        default_temperature_celsius=-18.0,
        base_humidity=0.80,
        prevailing_wind=Vector3D(x=12.0, y=6.0, z=0.0),
        typical_precipitations=[PrecipitationType.SNOW, PrecipitationType.BLIZZARD],
    )


def create_tundra_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.TUNDRA,
        name="Subarctic Tundra & Permafrost Plains",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.052, g=0.13, b=0.35),
            rayleigh_scale_height_km=7.2,
            ground_albedo=ColorRGB(r=0.3, g=0.32, b=0.35),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.025,
            fog_height_falloff=0.2,
            fog_inscattering_color=ColorRGB(r=0.6, g=0.7, b=0.8),
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=1.2,
            layer_height_km=3.5,
            cloud_coverage=0.5,
            precipitation_probability=0.45,
        ),
        default_temperature_celsius=-4.0,
        base_humidity=0.70,
        prevailing_wind=Vector3D(x=8.0, y=3.0, z=0.0),
        typical_precipitations=[PrecipitationType.LIGHT_RAIN, PrecipitationType.SNOW],
    )


def create_alpine_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.ALPINE,
        name="High Altitude Alpine Ridgelines",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.058, g=0.14, b=0.34),
            rayleigh_scale_height_km=5.0,  # Thinner atmosphere
            mie_scattering=0.002,          # Ultra crisp, low aerosols
            multi_scattering_factor=0.9,
            ground_albedo=ColorRGB(r=0.4, g=0.42, b=0.45),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.012,
            fog_height_falloff=0.3,
            fog_inscattering_color=ColorRGB(r=0.65, g=0.75, b=0.9),
            volumetric_fog_distance_cm=12000.0,
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=0.8,
            layer_height_km=2.5,
            cloud_coverage=0.35,
            density_multiplier=0.9,
            precipitation_probability=0.3,
        ),
        default_temperature_celsius=2.0,
        base_humidity=0.45,
        prevailing_wind=Vector3D(x=14.0, y=-4.0, z=0.0),
        typical_precipitations=[PrecipitationType.SNOW, PrecipitationType.BLIZZARD],
    )


def create_temperate_forest_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.TEMPERATE_FOREST,
        name="Temperate Deciduous & Coniferous Woodland",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.05802, g=0.13558, b=0.33100),
            rayleigh_scale_height_km=8.0,
            mie_scattering=0.003996,
            ground_albedo=ColorRGB(r=0.15, g=0.2, b=0.12),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.02,
            fog_height_falloff=0.18,
            fog_inscattering_color=ColorRGB(r=0.55, g=0.65, b=0.72),
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=1.8,
            layer_height_km=4.5,
            cloud_coverage=0.4,
            density_multiplier=0.85,
            precipitation_probability=0.35,
        ),
        default_temperature_celsius=19.0,
        base_humidity=0.60,
        prevailing_wind=Vector3D(x=4.0, y=2.0, z=0.0),
        typical_precipitations=[PrecipitationType.NONE, PrecipitationType.LIGHT_RAIN, PrecipitationType.HEAVY_STORM],
    )


def create_desert_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.DESERT,
        name="Arid Dunes & Sunbaked Badlands",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.062, g=0.125, b=0.29),
            rayleigh_scale_height_km=9.0,
            mie_scattering=0.015,         # High mineral dust scattering
            mie_absorption=0.002,
            mie_anisotropy_g=0.72,
            ground_albedo=ColorRGB(r=0.55, g=0.45, b=0.3),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.008,
            fog_height_falloff=0.25,
            fog_inscattering_color=ColorRGB(r=0.85, g=0.75, b=0.55),
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=2.8,
            layer_height_km=3.0,
            cloud_coverage=0.1,
            density_multiplier=0.4,
            precipitation_probability=0.02,
        ),
        default_temperature_celsius=38.0,
        base_humidity=0.15,
        prevailing_wind=Vector3D(x=7.0, y=1.0, z=0.0),
        typical_precipitations=[PrecipitationType.NONE, PrecipitationType.SANDSTORM],
    )


def create_swamp_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.SWAMP,
        name="Subtropical Bayou & Murky Wetlands",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.055, g=0.13, b=0.30),
            mie_scattering=0.008,
            ground_albedo=ColorRGB(r=0.1, g=0.14, b=0.08),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.065,          # Heavy low-lying ground mist
            fog_height_falloff=0.08,
            fog_inscattering_color=ColorRGB(r=0.38, g=0.48, b=0.42),
            volumetric_fog_distance_cm=4500.0,
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=1.0,
            layer_height_km=5.0,
            cloud_coverage=0.7,
            density_multiplier=1.1,
            precipitation_probability=0.6,
        ),
        default_temperature_celsius=26.0,
        base_humidity=0.92,
        prevailing_wind=Vector3D(x=2.0, y=1.5, z=0.0),
        typical_precipitations=[PrecipitationType.LIGHT_RAIN, PrecipitationType.HEAVY_STORM],
    )


def create_volcanic_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.VOLCANIC,
        name="Volcanic Caldera & Ash Wasteland",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.08, g=0.09, b=0.22),
            mie_scattering=0.025,         # Heavy airborne particulate soot
            mie_absorption=0.012,
            mie_anisotropy_g=0.65,
            ground_albedo=ColorRGB(r=0.08, g=0.06, b=0.05),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.045,
            fog_height_falloff=0.12,
            fog_inscattering_color=ColorRGB(r=0.65, g=0.35, b=0.25),
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=0.6,
            layer_height_km=6.0,
            cloud_coverage=0.85,
            density_multiplier=1.6,
            precipitation_probability=0.5,
        ),
        default_temperature_celsius=46.0,
        base_humidity=0.30,
        prevailing_wind=Vector3D(x=6.0, y=5.0, z=0.0),
        typical_precipitations=[PrecipitationType.ASH_FALL, PrecipitationType.NONE],
    )


def create_cyberpunk_neon_profile() -> BiomeAtmosphereProfile:
    return BiomeAtmosphereProfile(
        biome=WeatherBiomeType.CYBERPUNK_NEON,
        name="Megacity Smog & Neon Acid Haze",
        sky_atmosphere=SkyAtmosphereSpec(
            rayleigh_scattering=ColorRGB(r=0.065, g=0.11, b=0.28),
            mie_scattering=0.018,
            mie_absorption=0.005,
            multi_scattering_factor=1.4,
            ground_albedo=ColorRGB(r=0.12, g=0.12, b=0.14),
        ),
        height_fog=ExponentialHeightFogSpec(
            fog_density=0.038,
            fog_height_falloff=0.14,
            fog_inscattering_color=ColorRGB(r=0.25, g=0.35, b=0.48),
            volumetric_fog_scattering_distribution=0.4, # High forward scatter for neon blooms
            volumetric_fog_distance_cm=5000.0,
        ),
        volumetric_clouds=VolumetricCloudSpec(
            layer_bottom_altitude_km=1.2,
            layer_height_km=4.0,
            cloud_coverage=0.75,
            density_multiplier=1.0,
            precipitation_probability=0.65,
        ),
        default_temperature_celsius=17.0,
        base_humidity=0.78,
        prevailing_wind=Vector3D(x=5.0, y=2.0, z=0.0),
        typical_precipitations=[PrecipitationType.LIGHT_RAIN, PrecipitationType.HEAVY_STORM],
    )


BIOME_PROFILE_REGISTRY: Dict[WeatherBiomeType, BiomeAtmosphereProfile] = {
    WeatherBiomeType.ARCTIC: create_arctic_profile(),
    WeatherBiomeType.TUNDRA: create_tundra_profile(),
    WeatherBiomeType.ALPINE: create_alpine_profile(),
    WeatherBiomeType.TEMPERATE_FOREST: create_temperate_forest_profile(),
    WeatherBiomeType.DESERT: create_desert_profile(),
    WeatherBiomeType.SWAMP: create_swamp_profile(),
    WeatherBiomeType.VOLCANIC: create_volcanic_profile(),
    WeatherBiomeType.CYBERPUNK_NEON: create_cyberpunk_neon_profile(),
}


def get_default_biome_profile(biome: WeatherBiomeType) -> BiomeAtmosphereProfile:
    """Retrieves standard pre-calibrated atmospheric profile for a biome."""
    if biome not in BIOME_PROFILE_REGISTRY:
        return create_temperate_forest_profile()
    return BIOME_PROFILE_REGISTRY[biome]
