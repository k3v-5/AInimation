"""
UAF-81.91: Universal Procedural Macro-Landscape, Hydraulic Erosion, Biome Distribution & Spline Infrastructure.
Decoupled, deterministic macro-world generation, river drainage, cost-surface roads,
and binary 16-bit Unreal Engine 5 Landscape export.
"""

from uaf.landscape.core import (
    BiomeType,
    RoadCategory,
    SplineNode,
    RoadPath,
    ClimateMap,
    TerrainLayerWeightmaps,
    Heightfield2D,
)
from uaf.landscape.generation import (
    PerlinNoise2D,
    FractalNoise2D,
    VoronoiCellularNoise2D,
    MacroTerrainGenerator,
)
from uaf.landscape.erosion import (
    HydraulicErosionSimulator,
    ThermalErosionSimulator,
)
from uaf.landscape.ecology import (
    ClimateModeler,
    WhittakerBiomeClassifier,
    TerrainWeightmapGenerator,
)
from uaf.landscape.infrastructure import (
    RiverDrainageNetwork,
    RoadNetworkPlanner,
)
from uaf.landscape.distribution import (
    FoliageInstance,
    PoissonDiskSampler2D,
    PCGFoliageDistributor,
)
from uaf.landscape.export import (
    UE5LandscapeManifest,
    UE5LandscapeExporter,
)

__all__ = [
    # Core
    "BiomeType",
    "RoadCategory",
    "SplineNode",
    "RoadPath",
    "ClimateMap",
    "TerrainLayerWeightmaps",
    "Heightfield2D",
    # Generation
    "PerlinNoise2D",
    "FractalNoise2D",
    "VoronoiCellularNoise2D",
    "MacroTerrainGenerator",
    # Erosion
    "HydraulicErosionSimulator",
    "ThermalErosionSimulator",
    # Ecology
    "ClimateModeler",
    "WhittakerBiomeClassifier",
    "TerrainWeightmapGenerator",
    # Infrastructure
    "RiverDrainageNetwork",
    "RoadNetworkPlanner",
    # Foliage
    "FoliageInstance",
    "PoissonDiskSampler2D",
    "PCGFoliageDistributor",
    # Export
    "UE5LandscapeManifest",
    "UE5LandscapeExporter",
]
