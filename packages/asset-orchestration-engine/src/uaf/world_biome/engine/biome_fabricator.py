"""
WorldBiomeFabricationPlatform manufactures canonical Golden Worlds matching Section 122.
UAF-81.32 Section 122.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    BiomeWorldDefinition,
    WorldType32,
    BiomeType32,
    WorldBounds32,
    BiomeDefinition32,
)


class WorldBiomeFabricationPlatform:
    """
    Synthesizes complete, production-grade procedural worlds, heightmap terrains, biomes, and Unreal levels.
    """

    @classmethod
    def build_golden_small_combat_map(cls, world_id: str = "World_Golden_SmallCombat") -> Tuple[BiomeWorldDefinition, str, str]:
        """1. GOLDEN_SMALL_COMBAT_MAP (Section 122: tight bounds, urban ruins / indoor arena)."""
        bounds = WorldBounds32(-2000.0, 2000.0, -2000.0, 2000.0, 0.0, 1200.0)
        biomes = [
            BiomeDefinition32("Biome_UrbanCombat", BiomeType32.URBAN_RUINS, temperature=0.5, humidity=0.4, altitude_range=[0.0, 500.0]),
        ]
        w_def = BiomeWorldDefinition(world_id, WorldType32.ROOM_BASED, bounds, biomes)
        return w_def, f"TR_{world_id}", f"LV_{world_id}"

    @classmethod
    def build_golden_scifi_facility(cls, world_id: str = "World_Golden_SciFiFacility") -> Tuple[BiomeWorldDefinition, str, str]:
        """2. GOLDEN_SCI_FI_FACILITY (Section 122: interior facility biomes, sealed tech sectors)."""
        bounds = WorldBounds32(-4000.0, 4000.0, -4000.0, 4000.0, 0.0, 1500.0)
        biomes = [
            BiomeDefinition32("Biome_LabSector", BiomeType32.SCI_FI_INTERIOR, temperature=0.6, humidity=0.3, altitude_range=[0.0, 800.0]),
        ]
        w_def = BiomeWorldDefinition(world_id, WorldType32.FACILITY, bounds, biomes)
        return w_def, f"TR_{world_id}", f"LV_{world_id}"

    @classmethod
    def build_golden_industrial_complex(cls, world_id: str = "World_Golden_IndustrialComplex") -> Tuple[BiomeWorldDefinition, str, str]:
        """3. GOLDEN_INDUSTRIAL_COMPLEX (Section 122: refinery yards, steel plant sectors)."""
        bounds = WorldBounds32(-6000.0, 6000.0, -6000.0, 6000.0, 0.0, 2500.0)
        biomes = [
            BiomeDefinition32("Biome_IndustrialYard", BiomeType32.INDUSTRIAL_SECTOR, temperature=0.7, humidity=0.2, altitude_range=[0.0, 1200.0]),
        ]
        w_def = BiomeWorldDefinition(world_id, WorldType32.INDUSTRIAL, bounds, biomes)
        return w_def, f"TR_{world_id}", f"LV_{world_id}"

    @classmethod
    def build_golden_outdoor_combat_map(cls, world_id: str = "World_Golden_OutdoorCombat") -> Tuple[BiomeWorldDefinition, str, str]:
        """4. GOLDEN_OUTDOOR_COMBAT_MAP (Section 122: rolling hills, forest and rocky biomes, natural slopes)."""
        bounds = WorldBounds32(-8000.0, 8000.0, -8000.0, 8000.0, 0.0, 4000.0)
        biomes = [
            BiomeDefinition32("Biome_ValleyForest", BiomeType32.TEMPERATE_FOREST, temperature=0.55, humidity=0.7, altitude_range=[0.0, 2000.0]),
            BiomeDefinition32("Biome_HighlandRidge", BiomeType32.VOLCANIC_WASTELAND, temperature=0.8, humidity=0.1, altitude_range=[2000.0, 4000.0]),
        ]
        w_def = BiomeWorldDefinition(world_id, WorldType32.OUTDOOR_COMBAT, bounds, biomes)
        return w_def, f"TR_{world_id}", f"LV_{world_id}"

    @classmethod
    def build_golden_hybrid_level(cls, world_id: str = "World_Golden_HybridLevel") -> Tuple[BiomeWorldDefinition, str, str]:
        """5. GOLDEN_HYBRID_LEVEL (Section 122: exterior mountain pass into interior bunker facility)."""
        bounds = WorldBounds32(-10000.0, 10000.0, -10000.0, 10000.0, -2000.0, 5000.0)
        biomes = [
            BiomeDefinition32("Biome_MountainPass", BiomeType32.ARCTIC_TUNDRA, temperature=0.15, humidity=0.6, altitude_range=[1000.0, 5000.0]),
            BiomeDefinition32("Biome_SubterraneanFacility", BiomeType32.SCI_FI_INTERIOR, temperature=0.5, humidity=0.2, altitude_range=[-2000.0, 1000.0]),
        ]
        w_def = BiomeWorldDefinition(world_id, WorldType32.HYBRID, bounds, biomes)
        return w_def, f"TR_{world_id}", f"LV_{world_id}"
