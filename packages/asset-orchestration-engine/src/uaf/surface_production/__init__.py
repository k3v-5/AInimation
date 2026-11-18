"""
Universal Asset Factory (UAF) - Procedural Texture, Material & Surface Fabrication System (UAF-81.18)
"""

from .models import (
    SurfaceWeatheringState,
    MaterialPBRProfile,
    SurfaceDefinition,
    TexturePackingType,
    TextureChannelDefinition,
)

from .engine import (
    SurfaceProductionFabricator,
)

from .validation import (
    SurfaceProductionQualityScore,
    SurfaceProductionValidationReport,
    SurfaceProductionValidator,
)

from .package import (
    SurfaceProductionPackage,
)

__all__ = [
    "SurfaceWeatheringState",
    "MaterialPBRProfile",
    "SurfaceDefinition",
    "TexturePackingType",
    "TextureChannelDefinition",
    "SurfaceProductionFabricator",
    "SurfaceProductionQualityScore",
    "SurfaceProductionValidationReport",
    "SurfaceProductionValidator",
    "SurfaceProductionPackage",
]
