"""
Universal Runtime Dynamic Lighting, Shadowing, Atmosphere & Post-Process System (UAF-81.85).
Part of the Asset Orchestration Engine / Universal Asset Factory.
"""

from .core import (
    LightId,
    ShadowCasterId,
    PostProcessVolumeId,
    ProbeId,
    LightType,
    LightMobility,
    LightPriority,
    ShadowBackend,
    FogType,
    VolumetricQuality,
    ToneMapperType,
    ExposureMode,
    AOBackend,
    UpdateFrequency,
    FallbackLevel,
    WeatherCondition,
    ensure_finite_scalar,
    ensure_finite_vec3,
    ensure_finite_vec4,
    normalize_vec3,
    kelvin_to_rgb,
    ev100_to_luminance,
    luminance_to_ev100,
    lumens_to_candelas,
    candelas_to_lumens,
)

from .lights import Light
from .point import PointLight
from .spot import SpotLight
from .directional import DirectionalLight
from .area import RectAreaLight, DiskAreaLight, LineAreaLight

from .cascades import CSMCalculator, CascadeSlice
from .atlas import ShadowAtlas, AtlasTile
from .shadows import (
    ShadowRequest,
    ShadowResult,
    ShadowProvider,
    CSMShadowProvider,
    AtlasShadowProvider,
    ReferenceShadowProvider,
    ContactShadowEvaluator,
)

from .probes import IrradianceProbe, ReflectionProbe, LightProbeGrid
from .ambient import AmbientLighting, StaticBakePipeline, BakeResult

from .sun import Sun
from .moon import Moon
from .daynight import DayPeriod, EphemerisData, DayNightController
from .sky import SkySystem

from .atmosphere import AtmosphereScattering
from .fog import FogSystem
from .volumetrics import VolumetricSystem
from .clouds import CloudSystem
from .weather import WeatherSystem, WeatherPreset, WEATHER_PRESETS

from .exposure import ExposureSettings
from .tonemapping import ToneMapper
from .color import ColorGradingSettings
from .lut import LUT3D

from .bloom import BloomSettings
from .ao import AOSettings
from .dof import DOFSettings
from .motion_blur import MotionBlurSettings
from .lens import LensSettings

from .postprocess import PostProcessSettings, PostProcessVolume, PostProcessStack
from .culling import SimpleFrustum, LightCuller
from .lod import LightingLODManager
from .budgets import BudgetManager, LightingBudgets, DegradationStep
from .profiler import LightingProfiler, LightingProfileFrame
from .validation import LightingValidator, LightingValidationReport
from .recovery import LightingCrashRecovery
from .snapshot import LightingSnapshot
from .replay import LightingEvent, LightingReplayEngine
from .world import LightingWorld
from .presets import GoldenLightingPresets

__all__ = [
    # Identifiers
    "LightId",
    "ShadowCasterId",
    "PostProcessVolumeId",
    "ProbeId",
    # Enums
    "LightType",
    "LightMobility",
    "LightPriority",
    "ShadowBackend",
    "FogType",
    "VolumetricQuality",
    "ToneMapperType",
    "ExposureMode",
    "AOBackend",
    "UpdateFrequency",
    "FallbackLevel",
    "WeatherCondition",
    # Numeric & Photometry
    "ensure_finite_scalar",
    "ensure_finite_vec3",
    "ensure_finite_vec4",
    "normalize_vec3",
    "kelvin_to_rgb",
    "ev100_to_luminance",
    "luminance_to_ev100",
    "lumens_to_candelas",
    "candelas_to_lumens",
    # Lights
    "Light",
    "PointLight",
    "SpotLight",
    "DirectionalLight",
    "RectAreaLight",
    "DiskAreaLight",
    "LineAreaLight",
    # Shadows
    "CSMCalculator",
    "CascadeSlice",
    "ShadowAtlas",
    "AtlasTile",
    "ShadowRequest",
    "ShadowResult",
    "ShadowProvider",
    "CSMShadowProvider",
    "AtlasShadowProvider",
    "ReferenceShadowProvider",
    "ContactShadowEvaluator",
    # Probes & Ambient
    "IrradianceProbe",
    "ReflectionProbe",
    "LightProbeGrid",
    "AmbientLighting",
    "StaticBakePipeline",
    "BakeResult",
    # Celestial
    "Sun",
    "Moon",
    "DayPeriod",
    "EphemerisData",
    "DayNightController",
    "SkySystem",
    # Atmosphere & Volumetrics
    "AtmosphereScattering",
    "FogSystem",
    "VolumetricSystem",
    "CloudSystem",
    "WeatherSystem",
    "WeatherPreset",
    "WEATHER_PRESETS",
    # Post-Process & Color
    "ExposureSettings",
    "ToneMapper",
    "ColorGradingSettings",
    "LUT3D",
    "BloomSettings",
    "AOSettings",
    "DOFSettings",
    "MotionBlurSettings",
    "LensSettings",
    "PostProcessSettings",
    "PostProcessVolume",
    "PostProcessStack",
    # Culling, Budgets & LOD
    "SimpleFrustum",
    "LightCuller",
    "LightingLODManager",
    "BudgetManager",
    "LightingBudgets",
    "DegradationStep",
    # Telemetry, Validation & Recovery
    "LightingProfiler",
    "LightingProfileFrame",
    "LightingValidator",
    "LightingValidationReport",
    "LightingCrashRecovery",
    # Snapshots & Replay
    "LightingSnapshot",
    "LightingEvent",
    "LightingReplayEngine",
    # Central World & Presets
    "LightingWorld",
    "GoldenLightingPresets",
]
