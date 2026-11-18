"""
Universal Asset Factory (UAF) - Procedural Material, Texture, UV, Decal & Surface Authoring System (UAF-81.34)
"""

from .models import (
    MaterialFamily34,
    WearType34,
    DamageType34,
    SurfaceDecalItem,
    SurfaceAuthoringSpecification,
)

from .engine import (
    SurfaceDecalFabricationPlatform,
)

from .validation import (
    SurfaceDecalQualityScore,
    SurfaceDecalValidationReport,
    SurfaceDecalValidator,
)

from .package import (
    SurfaceDecalPackage,
)

__all__ = [
    "MaterialFamily34",
    "WearType34",
    "DamageType34",
    "SurfaceDecalItem",
    "SurfaceAuthoringSpecification",
    "SurfaceDecalFabricationPlatform",
    "SurfaceDecalQualityScore",
    "SurfaceDecalValidationReport",
    "SurfaceDecalValidator",
    "SurfaceDecalPackage",
]
