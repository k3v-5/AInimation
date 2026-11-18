"""
Universal Asset Factory (UAF) - Terrain, World, Biome & Procedural Map Generation System (UAF-81.48)
"""

from .models import (
    BiomeType48,
    TerrainGenMethod48,
    ErosionType48,
    TerrainDimensions48,
    TerrainWorldSpecification,
)

from .engine import (
    TerrainWorldFabricationPlatform,
)

from .validation import (
    TerrainWorldQualityScore,
    TerrainWorldValidationReport,
    TerrainWorldValidator,
)

from .package import (
    TerrainWorldPackage,
)

__all__ = [
    "BiomeType48",
    "TerrainGenMethod48",
    "ErosionType48",
    "TerrainDimensions48",
    "TerrainWorldSpecification",
    "TerrainWorldFabricationPlatform",
    "TerrainWorldQualityScore",
    "TerrainWorldValidationReport",
    "TerrainWorldValidator",
    "TerrainWorldPackage",
]
