"""
Universal Asset Factory (UAF) - Universal Geometry, Mesh Processing & Procedural Modeling System (UAF-81.53)
"""

from .models import (
    MeshCategory53,
    TopologyType53,
    MeshDimensions53,
    UniversalMeshSpecification,
)

from .engine import (
    UniversalGeometryFabricationPlatform,
)

from .validation import (
    UniversalGeometryQualityScore,
    UniversalGeometryValidationReport,
    UniversalGeometryValidator,
)

from .package import (
    UniversalGeometryPackage,
)

__all__ = [
    "MeshCategory53",
    "TopologyType53",
    "MeshDimensions53",
    "UniversalMeshSpecification",
    "UniversalGeometryFabricationPlatform",
    "UniversalGeometryQualityScore",
    "UniversalGeometryValidationReport",
    "UniversalGeometryValidator",
    "UniversalGeometryPackage",
]
