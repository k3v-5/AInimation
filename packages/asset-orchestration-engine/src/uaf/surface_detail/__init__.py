"""
Universal Asset Factory (UAF) - Procedural Material, Texture & Surface Detail Fabrication System (UAF-81.22)
"""

from .models import (
    PhysicalMaterialClass,
    SurfaceLayerType,
    SurfaceDetailDefinition,
    SurfaceDetailChannel,
)

from .engine import (
    SurfaceDetailFabricationPlatform,
)

from .validation import (
    SurfaceDetailQualityScore,
    SurfaceDetailValidationReport,
    SurfaceDetailValidator,
)

from .package import (
    SurfaceDetailPackage,
)

__all__ = [
    "PhysicalMaterialClass",
    "SurfaceLayerType",
    "SurfaceDetailDefinition",
    "SurfaceDetailChannel",
    "SurfaceDetailFabricationPlatform",
    "SurfaceDetailQualityScore",
    "SurfaceDetailValidationReport",
    "SurfaceDetailValidator",
    "SurfaceDetailPackage",
]
