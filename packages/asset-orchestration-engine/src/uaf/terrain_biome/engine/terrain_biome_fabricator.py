"""
TerrainBiomeFabricationPlatform manufactures canonical Golden Worlds matching Section 123.
UAF-81.36 Sections 123, 126.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    TerrainBiomeSpecification,
    BiomeType36,
    VegetationCategory36,
    TerrainBounds36,
)


class TerrainBiomeFabricationPlatform:
    """
    Synthesizes complete, production-grade procedural terrains, biomes, foliage, and outdoor worlds.
    """

    @classmethod
    def build_golden_forest(cls, terrain_id: str = "Terrain_Gold_Forest") -> Tuple[TerrainBiomeSpecification, str]:
        """1. GOLDEN_FOREST (Section 123: dense tree foliage, ground ferns, temperate moisture)."""
        bounds = TerrainBounds36(0.0, 150.0, 2000.0, 2000.0)
        veg = [VegetationCategory36.TREE, VegetationCategory36.FERN, VegetationCategory36.BUSH]
        spec = TerrainBiomeSpecification(terrain_id, BiomeType36.FOREST, bounds, veg, water_body_count=1, road_segments_count=2)
        return spec, f"/Game/Environments/Landscapes/{terrain_id}"

    @classmethod
    def build_golden_desert(cls, terrain_id: str = "Terrain_Gold_Desert") -> Tuple[TerrainBiomeSpecification, str]:
        """2. GOLDEN_DESERT (Section 123: arid dunes, rocky outcroppings, sparse shrubs)."""
        bounds = TerrainBounds36(50.0, 300.0, 4000.0, 4000.0)
        veg = [VegetationCategory36.BUSH]
        spec = TerrainBiomeSpecification(terrain_id, BiomeType36.DESERT, bounds, veg, water_body_count=0, road_segments_count=1)
        return spec, f"/Game/Environments/Landscapes/{terrain_id}"

    @classmethod
    def build_golden_mountain(cls, terrain_id: str = "Terrain_Gold_Mountain") -> Tuple[TerrainBiomeSpecification, str]:
        """3. GOLDEN_MOUNTAIN (Section 123: steep cliffs, alpine rock, peak altitude gradient)."""
        bounds = TerrainBounds36(500.0, 2500.0, 3000.0, 3000.0)
        veg = [VegetationCategory36.TREE, VegetationCategory36.GRASS]
        spec = TerrainBiomeSpecification(terrain_id, BiomeType36.ROCKY, bounds, veg, water_body_count=1, road_segments_count=1)
        return spec, f"/Game/Environments/Landscapes/{terrain_id}"

    @classmethod
    def build_golden_swamp(cls, terrain_id: str = "Terrain_Gold_Swamp") -> Tuple[TerrainBiomeSpecification, str]:
        """4. GOLDEN_SWAMP (Section 123: low sea level, shallow water bodies, dense root vegetation)."""
        bounds = TerrainBounds36(-10.0, 40.0, 1500.0, 1500.0)
        veg = [VegetationCategory36.ROOT, VegetationCategory36.VINE, VegetationCategory36.MUSHROOM]
        spec = TerrainBiomeSpecification(terrain_id, BiomeType36.SWAMP, bounds, veg, water_body_count=4, road_segments_count=0)
        return spec, f"/Game/Environments/Landscapes/{terrain_id}"

    @classmethod
    def build_golden_river_valley(cls, terrain_id: str = "Terrain_Gold_RiverValley") -> Tuple[TerrainBiomeSpecification, str]:
        """5. GOLDEN_RIVER_VALLEY (Section 123: river carving through valley, connecting road spline)."""
        bounds = TerrainBounds36(100.0, 600.0, 2500.0, 5000.0)
        veg = [VegetationCategory36.TREE, VegetationCategory36.GRASS, VegetationCategory36.FLOWER]
        spec = TerrainBiomeSpecification(terrain_id, BiomeType36.GRASSLAND, bounds, veg, water_body_count=1, road_segments_count=3)
        return spec, f"/Game/Environments/Landscapes/{terrain_id}"

    @classmethod
    def build_golden_urban_outdoor(cls, terrain_id: str = "Terrain_Gold_UrbanOutdoor") -> Tuple[TerrainBiomeSpecification, str]:
        """6. GOLDEN_URBAN_OUTDOOR (Section 123: graded flat terrain, asphalt road network, minimal vegetation)."""
        bounds = TerrainBounds36(10.0, 30.0, 2000.0, 2000.0)
        veg = [VegetationCategory36.GRASS, VegetationCategory36.TREE]
        spec = TerrainBiomeSpecification(terrain_id, BiomeType36.URBAN, bounds, veg, water_body_count=0, road_segments_count=8)
        return spec, f"/Game/Environments/Landscapes/{terrain_id}"

    @classmethod
    def build_golden_alien_biome(cls, terrain_id: str = "Terrain_Gold_AlienBiome") -> Tuple[TerrainBiomeSpecification, str]:
        """7. GOLDEN_ALIEN_BIOME (Section 123: alien plants, exotic slope distributions, custom terrain forms)."""
        bounds = TerrainBounds36(0.0, 800.0, 3000.0, 3000.0)
        veg = [VegetationCategory36.ALIEN_PLANT, VegetationCategory36.MUSHROOM]
        spec = TerrainBiomeSpecification(terrain_id, BiomeType36.ALIEN, bounds, veg, water_body_count=2, road_segments_count=0)
        return spec, f"/Game/Environments/Landscapes/{terrain_id}"
