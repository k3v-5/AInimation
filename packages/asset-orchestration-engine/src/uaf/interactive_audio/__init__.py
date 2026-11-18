"""
UAF-81.94: Procedural Interactive Audio, Spatial Acoustics & MetaSounds.
Analytical Sabine/Eyring acoustic reverberation, topological sound diffraction,
adaptive music stem orchestration with Quartz quantization clock,
3D spatial distance attenuation conforming to Rule 10,
and Unreal Engine 5 MetaSounds Source Asset exporters.
"""

from uaf.interactive_audio.core import (
    AcousticMaterial,
    StemRole,
    QuantizationSubdivision,
    OcclusionState,
    AttenuationCurveType,
    MATERIAL_ABSORPTION_TABLE,
    MaterialAbsorption,
    RoomAcousticProfile,
    AudioStem,
    SpatialAttenuationProfile,
    AcousticRaycastResult,
)
from uaf.interactive_audio.adaptive import (
    QuartzQuantizationClock,
    AdaptiveMusicOrchestrator,
)
from uaf.interactive_audio.acoustics import (
    SabineEyringAcousticCalculator,
    TopologicalAcousticDiffraction,
)
from uaf.interactive_audio.spatial import (
    SpatialAttenuationCalculator,
)
from uaf.interactive_audio.export import (
    MetaSoundNodeSchema,
    UE5MetaSoundsGraphManifest,
    UE5MetaSoundsExporter,
)

__all__ = [
    # Core contracts
    "AcousticMaterial",
    "StemRole",
    "QuantizationSubdivision",
    "OcclusionState",
    "AttenuationCurveType",
    "MATERIAL_ABSORPTION_TABLE",
    "MaterialAbsorption",
    "RoomAcousticProfile",
    "AudioStem",
    "SpatialAttenuationProfile",
    "AcousticRaycastResult",
    # Adaptive music
    "QuartzQuantizationClock",
    "AdaptiveMusicOrchestrator",
    # Acoustics & Diffraction
    "SabineEyringAcousticCalculator",
    "TopologicalAcousticDiffraction",
    # Spatial attenuation (Rule 10)
    "SpatialAttenuationCalculator",
    # Export
    "MetaSoundNodeSchema",
    "UE5MetaSoundsGraphManifest",
    "UE5MetaSoundsExporter",
]
