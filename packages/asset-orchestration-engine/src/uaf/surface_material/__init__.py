"""
Universal Asset Factory (UAF) - Procedural Material, Texture, Surface & Decal Production System (UAF-81.30)
"""

from .models import (
    SurfaceType30,
    MaterialModel30,
    ColorSpace30,
    SurfaceMapItem,
    ProductionSurfaceDefinition,
)

from .engine import (
    SurfaceMaterialProductionPlatform,
)

from .validation import (
    SurfaceMaterialQualityScore,
    SurfaceMaterialValidationReport,
    SurfaceMaterialValidator,
)

from .package import (
    SurfaceMaterialPackage,
)

__all__ = [
    "SurfaceType30",
    "MaterialModel30",
    "ColorSpace30",
    "SurfaceMapItem",
    "ProductionSurfaceDefinition",
    "SurfaceMaterialProductionPlatform",
    "SurfaceMaterialQualityScore",
    "SurfaceMaterialValidationReport",
    "SurfaceMaterialValidator",
    "SurfaceMaterialPackage",
]
