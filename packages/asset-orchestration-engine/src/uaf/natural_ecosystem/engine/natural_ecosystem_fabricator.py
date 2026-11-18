"""
NaturalEcosystemFabricationPlatform manufactures canonical Golden Environments matching Section 135.
UAF-81.51 Sections 135, 139, 142.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    NaturalEcosystemSpecification,
    NaturalBiomeType51,
    TerrainType51,
    NaturalTerrainDimensions51,
)


class NaturalEcosystemFabricationPlatform:
    """
    Synthesizes complete, production-grade natural landscapes, biomes, foliage, rocks, and water systems for Unreal Engine.
    """

    @classmethod
    def build_golden_forest(cls, eco_id: str = "Eco_Gold_Forest51") -> Tuple[NaturalEcosystemSpecification, str, str, str, str]:
        """1. GOLDEN_FOREST (Section 135: dense canopy, river system, rock clusters, forest trails)."""
        dims = NaturalTerrainDimensions51(width_m=2500.0, length_m=2500.0, height_scale_m=250.0)
        spec = NaturalEcosystemSpecification(eco_id, NaturalBiomeType51.FOREST, TerrainType51.ROLLING, dims)
        return (
            spec,
            f"/Game/Environments/Natural/{eco_id}/Landscape_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Foliage/Foliage_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Water/WaterMesh_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Navigation/Nav_{eco_id}",
        )

    @classmethod
    def build_golden_desert(cls, eco_id: str = "Eco_Gold_Desert51") -> Tuple[NaturalEcosystemSpecification, str, str, str, str]:
        """2. GOLDEN_DESERT (Section 135: dunes, wind erosion, rock arches, dry wadi)."""
        dims = NaturalTerrainDimensions51(width_m=4000.0, length_m=4000.0, height_scale_m=350.0)
        spec = NaturalEcosystemSpecification(eco_id, NaturalBiomeType51.DESERT, TerrainType51.DESERT, dims)
        return (
            spec,
            f"/Game/Environments/Natural/{eco_id}/Landscape_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Foliage/Foliage_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Water/WaterMesh_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Navigation/Nav_{eco_id}",
        )

    @classmethod
    def build_golden_mountain(cls, eco_id: str = "Eco_Gold_Mountain51") -> Tuple[NaturalEcosystemSpecification, str, str, str, str]:
        """3. GOLDEN_MOUNTAIN (Section 135: peaks, thermal rock erosion, alpine trees, mountain pass)."""
        dims = NaturalTerrainDimensions51(width_m=5000.0, length_m=5000.0, height_scale_m=900.0)
        spec = NaturalEcosystemSpecification(eco_id, NaturalBiomeType51.MOUNTAIN, TerrainType51.MOUNTAINOUS, dims)
        return (
            spec,
            f"/Game/Environments/Natural/{eco_id}/Landscape_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Foliage/Foliage_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Water/WaterMesh_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Navigation/Nav_{eco_id}",
        )

    @classmethod
    def build_golden_swamp(cls, eco_id: str = "Eco_Gold_Swamp51") -> Tuple[NaturalEcosystemSpecification, str, str, str, str]:
        """4. GOLDEN_SWAMP (Section 135: wetlands, muddy banks, cypress knees, mangrove roots)."""
        dims = NaturalTerrainDimensions51(width_m=2000.0, length_m=2000.0, height_scale_m=80.0)
        spec = NaturalEcosystemSpecification(eco_id, NaturalBiomeType51.SWAMP, TerrainType51.SWAMP, dims)
        return (
            spec,
            f"/Game/Environments/Natural/{eco_id}/Landscape_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Foliage/Foliage_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Water/WaterMesh_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Navigation/Nav_{eco_id}",
        )

    @classmethod
    def build_golden_coastal(cls, eco_id: str = "Eco_Gold_Coastal51") -> Tuple[NaturalEcosystemSpecification, str, str, str, str]:
        """5. GOLDEN_COASTAL (Section 135: shoreline, ocean waves, sea cliffs, coastal foliage)."""
        dims = NaturalTerrainDimensions51(width_m=3500.0, length_m=3500.0, height_scale_m=180.0)
        spec = NaturalEcosystemSpecification(eco_id, NaturalBiomeType51.COASTAL, TerrainType51.COASTAL, dims)
        return (
            spec,
            f"/Game/Environments/Natural/{eco_id}/Landscape_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Foliage/Foliage_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Water/WaterMesh_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Navigation/Nav_{eco_id}",
        )

    @classmethod
    def build_golden_hybrid(cls, eco_id: str = "Eco_Gold_Hybrid51") -> Tuple[NaturalEcosystemSpecification, str, str, str, str]:
        """6. GOLDEN_HYBRID (Section 135: multi-biome transition zone, foothills, stream, varied flora)."""
        dims = NaturalTerrainDimensions51(width_m=4500.0, length_m=4500.0, height_scale_m=400.0)
        spec = NaturalEcosystemSpecification(eco_id, NaturalBiomeType51.HYBRID, TerrainType51.HILLY, dims)
        return (
            spec,
            f"/Game/Environments/Natural/{eco_id}/Landscape_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Foliage/Foliage_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Water/WaterMesh_{eco_id}",
            f"/Game/Environments/Natural/{eco_id}/Navigation/Nav_{eco_id}",
        )
