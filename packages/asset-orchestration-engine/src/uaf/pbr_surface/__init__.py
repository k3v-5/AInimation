"""
Universal Asset Factory (UAF) - Material, Texture, UV, PBR, Procedural Surface & Unreal Material Authoring System (UAF-81.43)
"""

from .models import (
    MaterialCategory43,
    UVStrategy43,
    TexelDensityProfile43,
    PBRProperties43,
    PBRSurfaceSpecification,
)

from .engine import (
    PBRSurfaceFabricationPlatform,
)

from .validation import (
    PBRSurfaceQualityScore,
    PBRSurfaceValidationReport,
    PBRSurfaceValidator,
)

from .package import (
    PBRSurfacePackage,
)

__all__ = [
    "MaterialCategory43",
    "UVStrategy43",
    "TexelDensityProfile43",
    "PBRProperties43",
    "PBRSurfaceSpecification",
    "PBRSurfaceFabricationPlatform",
    "PBRSurfaceQualityScore",
    "PBRSurfaceValidationReport",
    "PBRSurfaceValidator",
    "PBRSurfacePackage",
]
