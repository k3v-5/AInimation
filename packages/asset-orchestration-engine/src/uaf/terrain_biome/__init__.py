"""
Universal Asset Factory (UAF) - Procedural Terrain, Biome, Vegetation, Landscape & Outdoor World System (UAF-81.36)
"""

from .models import (
    BiomeType36,
    VegetationCategory36,
    SlopeClassification36,
    TerrainBounds36,
    TerrainBiomeSpecification,
)

from .engine import (
    TerrainBiomeFabricationPlatform,
)

from .validation import (
    TerrainBiomeQualityScore,
    TerrainBiomeValidationReport,
    TerrainBiomeValidator,
)

from .package import (
    TerrainBiomePackage,
)

__all__ = [
    "BiomeType36",
    "VegetationCategory36",
    "SlopeClassification36",
    "TerrainBounds36",
    "TerrainBiomeSpecification",
    "TerrainBiomeFabricationPlatform",
    "TerrainBiomeQualityScore",
    "TerrainBiomeValidationReport",
    "TerrainBiomeValidator",
    "TerrainBiomePackage",
]
