"""
TerrainWorldFabricationPlatform manufactures canonical Golden Worlds matching Section 126.
UAF-81.48 Sections 126, 140, 142.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    TerrainWorldSpecification,
    BiomeType48,
    TerrainGenMethod48,
    TerrainDimensions48,
)


class TerrainWorldFabricationPlatform:
    """
    Synthesizes complete, production-grade terrain, worlds, biomes, road networks, and world partitions for Unreal Engine.
    """

    @classmethod
    def build_golden_desert_world(cls, world_id: str = "World_Gold_Desert") -> Tuple[TerrainWorldSpecification, str, str, str]:
        """1. GOLDEN_DESERT_WORLD (Section 126: dunes, wind erosion, canyon roads, oasis POI)."""
        dims = TerrainDimensions48(width_m=4000.0, length_m=4000.0, min_height_m=50.0, max_height_m=350.0)
        spec = TerrainWorldSpecification(world_id, BiomeType48.DESERT, TerrainGenMethod48.HYBRID, dims)
        return (
            spec,
            f"/Game/Worlds/Terrain/{world_id}/Landscape_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Partition/WP_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Navigation/Nav_{world_id}",
        )

    @classmethod
    def build_golden_forest_world(cls, world_id: str = "World_Gold_Forest") -> Tuple[TerrainWorldSpecification, str, str, str]:
        """2. GOLDEN_FOREST_WORLD (Section 126: dense canopy, hydraulic river erosion, logging roads)."""
        dims = TerrainDimensions48(width_m=3000.0, length_m=3000.0, min_height_m=20.0, max_height_m=280.0)
        spec = TerrainWorldSpecification(world_id, BiomeType48.FOREST, TerrainGenMethod48.HYBRID, dims)
        return (
            spec,
            f"/Game/Worlds/Terrain/{world_id}/Landscape_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Partition/WP_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Navigation/Nav_{world_id}",
        )

    @classmethod
    def build_golden_mountain_world(cls, world_id: str = "World_Gold_Mountain") -> Tuple[TerrainWorldSpecification, str, str, str]:
        """3. GOLDEN_MOUNTAIN_WORLD (Section 126: peaks, thermal rock erosion, passes and bridges)."""
        dims = TerrainDimensions48(width_m=5000.0, length_m=5000.0, min_height_m=100.0, max_height_m=850.0)
        spec = TerrainWorldSpecification(world_id, BiomeType48.MOUNTAIN, TerrainGenMethod48.FRACTAL_NOISE, dims)
        return (
            spec,
            f"/Game/Worlds/Terrain/{world_id}/Landscape_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Partition/WP_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Navigation/Nav_{world_id}",
        )

    @classmethod
    def build_golden_industrial_world(cls, world_id: str = "World_Gold_Industrial") -> Tuple[TerrainWorldSpecification, str, str, str]:
        """4. GOLDEN_INDUSTRIAL_WORLD (Section 126: terraced terrain, industrial facilities, road grid)."""
        dims = TerrainDimensions48(width_m=2500.0, length_m=2500.0, min_height_m=10.0, max_height_m=120.0)
        spec = TerrainWorldSpecification(world_id, BiomeType48.INDUSTRIAL, TerrainGenMethod48.STAMP, dims)
        return (
            spec,
            f"/Game/Worlds/Terrain/{world_id}/Landscape_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Partition/WP_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Navigation/Nav_{world_id}",
        )

    @classmethod
    def build_golden_sci_fi_world(cls, world_id: str = "World_Gold_SciFi") -> Tuple[TerrainWorldSpecification, str, str, str]:
        """5. GOLDEN_SCI_FI_WORLD (Section 126: alien landscape, craters, research facility POIs)."""
        dims = TerrainDimensions48(width_m=3500.0, length_m=3500.0, min_height_m=0.0, max_height_m=420.0)
        spec = TerrainWorldSpecification(world_id, BiomeType48.SCI_FI, TerrainGenMethod48.VORONOI, dims)
        return (
            spec,
            f"/Game/Worlds/Terrain/{world_id}/Landscape_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Partition/WP_{world_id}",
            f"/Game/Worlds/Terrain/{world_id}/Navigation/Nav_{world_id}",
        )
