"""
ProceduralWorldSurfaceFabricator generates all 5 canonical world configurations.
UAF-81.13 Sections 200, 201.
"""

from typing import List, Dict, Any, Tuple
from ..terrain.territory import TerritoryModel, TerrainMode
from ..terrain.landmark import NaturalLandmark, LandmarkType
from ..biomes.biome import BiomeType, BiomeProfile


class ProceduralWorldSurfaceFabricator:
    """
    Synthesizes complete world territories and ecological biome distributions (Section 201).
    """

    @classmethod
    def build_desert_world(cls, world_id: str = "World_Desert", seed: int = 101) -> Tuple[TerritoryModel, List[BiomeProfile], List[NaturalLandmark]]:
        """1. Desert World (Dunes, monoliths, arid climate)."""
        terr = TerritoryModel(territory_id=world_id, world_width_m=2000.0, world_length_m=2000.0, max_height_m=120.0, seed=seed)
        biomes = [BiomeProfile.create_desert_profile()]
        landmarks = [
            NaturalLandmark("LM_Dune_Monolith", LandmarkType.MONOLITH, [500.0, 500.0, 60.0], prominence=0.85),
            NaturalLandmark("LM_Oasis_Ruin", LandmarkType.RUIN, [-200.0, -300.0, 10.0], prominence=0.7),
        ]
        return terr, biomes, landmarks

    @classmethod
    def build_forest_world(cls, world_id: str = "World_Forest", seed: int = 202) -> Tuple[TerritoryModel, List[BiomeProfile], List[NaturalLandmark]]:
        """2. Forest World (Temperate canopy, lake, rolling hills)."""
        terr = TerritoryModel(territory_id=world_id, world_width_m=2000.0, world_length_m=2000.0, max_height_m=180.0, seed=seed)
        biomes = [BiomeProfile.create_forest_profile()]
        landmarks = [
            NaturalLandmark("LM_Deep_Lake", LandmarkType.LAKE, [0.0, 0.0, 15.0], prominence=0.9),
            NaturalLandmark("LM_Ancient_Cliff", LandmarkType.CLIFF, [400.0, -400.0, 90.0], prominence=0.8),
        ]
        return terr, biomes, landmarks

    @classmethod
    def build_industrial_wasteland_world(cls, world_id: str = "World_Wasteland", seed: int = 303) -> Tuple[TerritoryModel, List[BiomeProfile], List[NaturalLandmark]]:
        """3. Industrial Wasteland (Slag terrain, craters, ruins)."""
        terr = TerritoryModel(territory_id=world_id, world_width_m=1500.0, world_length_m=1500.0, max_height_m=90.0, seed=seed)
        biomes = [BiomeProfile.create_wasteland_profile()]
        landmarks = [
            NaturalLandmark("LM_Blast_Crater", LandmarkType.CRATER, [100.0, 250.0, -15.0], prominence=0.95),
            NaturalLandmark("LM_Smelter_Ruin", LandmarkType.RUIN, [-150.0, -100.0, 40.0], prominence=0.75),
        ]
        return terr, biomes, landmarks

    @classmethod
    def build_alien_biome_world(cls, world_id: str = "World_Alien", seed: int = 404) -> Tuple[TerritoryModel, List[BiomeProfile], List[NaturalLandmark]]:
        """4. Alien Biome (Exotic spires, craters, bioluminescent flora)."""
        terr = TerritoryModel(territory_id=world_id, world_width_m=2500.0, world_length_m=2500.0, max_height_m=350.0, seed=seed)
        biomes = [BiomeProfile.create_alien_profile()]
        landmarks = [
            NaturalLandmark("LM_Crystal_Spire", LandmarkType.NATURAL_FORMATION, [300.0, 300.0, 150.0], prominence=1.0),
            NaturalLandmark("LM_Impact_Basin", LandmarkType.CRATER, [-500.0, 0.0, 20.0], prominence=0.9),
        ]
        return terr, biomes, landmarks

    @classmethod
    def build_hybrid_multi_biome_world(cls, world_id: str = "World_MultiBiome", seed: int = 505) -> Tuple[TerritoryModel, List[BiomeProfile], List[NaturalLandmark]]:
        """5. Hybrid Multi-Biome World (Forest transitioning to Desert and Mountain)."""
        terr = TerritoryModel(territory_id=world_id, world_width_m=4000.0, world_length_m=4000.0, max_height_m=500.0, seed=seed)
        biomes = [
            BiomeProfile.create_forest_profile(),
            BiomeProfile.create_desert_profile(),
            BiomeProfile(
                biome_type=BiomeType.ARCTIC,
                temperature_celsius=-15.0,
                moisture=0.3,
                dominant_ground_material="M_Ground_SnowIce",
                vegetation_density=0.0,
                rock_density=0.5,
                has_water=False,
            ),
        ]
        landmarks = [
            NaturalLandmark("LM_Summit_Peak", LandmarkType.MOUNTAIN, [0.0, 1000.0, 480.0], prominence=1.0),
            NaturalLandmark("LM_Divide_Canyon", LandmarkType.CLIFF, [0.0, 0.0, 80.0], prominence=0.85),
        ]
        return terr, biomes, landmarks
