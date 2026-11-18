"""
Universal Asset Factory (UAF) - Universal Material, Texture & Surface Authoring System (UAF-81.52)
"""

from .models import (
    SurfaceType52,
    PBRChannelType52,
    TextureResolution52,
    PBRSurfaceProperties52,
    UniversalSurfaceSpecification,
)

from .engine import (
    UniversalSurfaceFabricationPlatform,
)

from .validation import (
    UniversalSurfaceQualityScore,
    UniversalSurfaceValidationReport,
    UniversalSurfaceValidator,
)

from .package import (
    UniversalSurfacePackage,
)

__all__ = [
    "SurfaceType52",
    "PBRChannelType52",
    "TextureResolution52",
    "PBRSurfaceProperties52",
    "UniversalSurfaceSpecification",
    "UniversalSurfaceFabricationPlatform",
    "UniversalSurfaceQualityScore",
    "UniversalSurfaceValidationReport",
    "UniversalSurfaceValidator",
    "UniversalSurfacePackage",
]
