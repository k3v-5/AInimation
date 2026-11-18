"""
Universal Asset Factory (UAF) - Material, Texture & Surface Fabrication System (UAF-81.15)
"""

from .models import (
    MaterialClassification,
    MaterialDomain,
    SurfaceWearType,
    SurfaceProfile,
    MaterialParameterType,
    MaterialGraphContract,
)

from .engine import (
    SurfaceFabricationEngine,
)

from .validation import (
    SurfaceFabricationQualityScore,
    SurfaceFabricationValidationReport,
    SurfaceFabricationValidator,
)

from .package import (
    SurfaceFabricationPackage,
)

__all__ = [
    "MaterialClassification",
    "MaterialDomain",
    "SurfaceWearType",
    "SurfaceProfile",
    "MaterialParameterType",
    "MaterialGraphContract",
    "SurfaceFabricationEngine",
    "SurfaceFabricationQualityScore",
    "SurfaceFabricationValidationReport",
    "SurfaceFabricationValidator",
    "SurfaceFabricationPackage",
]
