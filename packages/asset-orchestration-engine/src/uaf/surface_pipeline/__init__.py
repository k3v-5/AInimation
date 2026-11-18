"""
Universal Asset Factory (UAF) - Procedural Texture, UV, Material & Surface Detail Fabrication System (UAF-81.27)
"""

from .models import (
    SurfaceClass27,
    UVStrategyType,
    ColorSpace27,
    TextureMapDefinition,
    SurfaceDefinition27,
)

from .engine import (
    SurfacePipelineFabricationPlatform,
)

from .validation import (
    SurfacePipelineQualityScore,
    SurfacePipelineValidationReport,
    SurfacePipelineValidator,
)

from .package import (
    SurfacePipelinePackage,
)

__all__ = [
    "SurfaceClass27",
    "UVStrategyType",
    "ColorSpace27",
    "TextureMapDefinition",
    "SurfaceDefinition27",
    "SurfacePipelineFabricationPlatform",
    "SurfacePipelineQualityScore",
    "SurfacePipelineValidationReport",
    "SurfacePipelineValidator",
    "SurfacePipelinePackage",
]
