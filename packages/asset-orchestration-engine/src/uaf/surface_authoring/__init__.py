"""
Universal Asset Factory (UAF) - Procedural Texture, Material & Surface Authoring Fabric (UAF-81.11)
"""

from .models import (
    MaterialFamilyType,
    MaterialLayerBlendMode,
    SurfaceRegion,
    MaterialCompositionLayer,
    MaterialRegionGraph,
)

from .authoring import (
    SurfaceAuthoringEngine,
)

from .validation import (
    SurfaceAuthoringQualityScore,
    SurfaceAuthoringValidationReport,
    SurfaceAuthoringValidator,
)

from .package import (
    AuthoredSurfacePackage,
)

__all__ = [
    "MaterialFamilyType",
    "MaterialLayerBlendMode",
    "SurfaceRegion",
    "MaterialCompositionLayer",
    "MaterialRegionGraph",
    "SurfaceAuthoringEngine",
    "SurfaceAuthoringQualityScore",
    "SurfaceAuthoringValidationReport",
    "SurfaceAuthoringValidator",
    "AuthoredSurfacePackage",
]
