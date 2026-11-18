"""
BiomeType and BiomeProfile models for ecological and surface rules.
UAF-81.13 Sections 37, 38, 181, 201.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any


class BiomeType(str, Enum):
    DESERT = "DESERT"
    FOREST = "FOREST"
    ARCTIC = "ARCTIC"
    VOLCANIC = "VOLCANIC"
    URBAN_OUTSKIRTS = "URBAN_OUTSKIRTS"
    INDUSTRIAL_WASTELAND = "INDUSTRIAL_WASTELAND"
    ALIEN_BIOME = "ALIEN_BIOME"
    HYBRID_MULTI_BIOME = "HYBRID_MULTI_BIOME"


@dataclass
class BiomeProfile:
    biome_type: BiomeType
    temperature_celsius: float = 20.0
    moisture: float = 0.5            # 0.0 (arid) to 1.0 (saturated)
    dominant_ground_material: str = "M_Ground_Grass"
    vegetation_density: float = 0.5  # 0.0 to 1.0
    rock_density: float = 0.3        # 0.0 to 1.0
    has_water: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "biome_type": self.biome_type.value,
            "temperature_celsius": self.temperature_celsius,
            "moisture": self.moisture,
            "dominant_ground_material": self.dominant_ground_material,
            "vegetation_density": self.vegetation_density,
            "rock_density": self.rock_density,
            "has_water": self.has_water,
        }

    @classmethod
    def create_desert_profile(cls) -> "BiomeProfile":
        return cls(
            biome_type=BiomeType.DESERT,
            temperature_celsius=42.0,
            moisture=0.05,
            dominant_ground_material="M_Ground_DesertSand",
            vegetation_density=0.02,
            rock_density=0.4,
            has_water=False,
        )

    @classmethod
    def create_forest_profile(cls) -> "BiomeProfile":
        return cls(
            biome_type=BiomeType.FOREST,
            temperature_celsius=18.0,
            moisture=0.75,
            dominant_ground_material="M_Ground_ForestSoil",
            vegetation_density=0.85,
            rock_density=0.25,
            has_water=True,
        )

    @classmethod
    def create_wasteland_profile(cls) -> "BiomeProfile":
        return cls(
            biome_type=BiomeType.INDUSTRIAL_WASTELAND,
            temperature_celsius=26.0,
            moisture=0.15,
            dominant_ground_material="M_Ground_IndustrialSlag",
            vegetation_density=0.05,
            rock_density=0.6,
            has_water=False,
        )

    @classmethod
    def create_alien_profile(cls) -> "BiomeProfile":
        return cls(
            biome_type=BiomeType.ALIEN_BIOME,
            temperature_celsius=-10.0,
            moisture=0.6,
            dominant_ground_material="M_Ground_BioluminescentMoss",
            vegetation_density=0.5,
            rock_density=0.5,
            has_water=True,
        )
