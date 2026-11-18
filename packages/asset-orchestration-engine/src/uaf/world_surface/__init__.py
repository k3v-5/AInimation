"""
Universal Asset Factory (UAF) - Procedural Terrain, Biome & World Surface Fabrication (UAF-81.13)
"""

from .terrain import (
    TerrainMode,
    ErosionType,
    TerritoryModel,
    LandmarkType,
    NaturalLandmark,
)

from .biomes import (
    BiomeType,
    BiomeProfile,
)

from .generator import (
    ProceduralWorldSurfaceFabricator,
)

from .validation import (
    WorldSurfaceQualityScore,
    WorldSurfaceValidationReport,
    WorldSurfaceValidator,
)

from .package import (
    WorldSurfacePackage,
)

__all__ = [
    "TerrainMode",
    "ErosionType",
    "TerritoryModel",
    "LandmarkType",
    "NaturalLandmark",
    "BiomeType",
    "BiomeProfile",
    "ProceduralWorldSurfaceFabricator",
    "WorldSurfaceQualityScore",
    "WorldSurfaceValidationReport",
    "WorldSurfaceValidator",
    "WorldSurfacePackage",
]
