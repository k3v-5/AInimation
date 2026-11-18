"""
World, Environment, and Level semantic models.
UAF-81.1 Sections 42, 43, 44.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class EnvironmentSemanticModel:
    name: str
    biome: str
    terrain_type: str = "rocky"
    atmosphere: Dict[str, Any] = field(default_factory=dict)
    lighting: Dict[str, Any] = field(default_factory=dict)
    vegetation_density: float = 0.5
    structures: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "biome": self.biome,
            "terrain_type": self.terrain_type,
            "atmosphere": self.atmosphere,
            "lighting": self.lighting,
            "vegetation_density": self.vegetation_density,
            "structures": self.structures,
        }


@dataclass
class WorldSemanticModel:
    world_name: str
    scale: str = "large"
    region_count: int = 1
    biomes: List[str] = field(default_factory=list)
    requires_streaming: bool = True
    gameplay_spaces: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_name": self.world_name,
            "scale": self.scale,
            "region_count": self.region_count,
            "biomes": self.biomes,
            "requires_streaming": self.requires_streaming,
            "gameplay_spaces": self.gameplay_spaces,
        }


@dataclass
class LevelSemanticModel:
    level_name: str
    visual_layout: Dict[str, Any] = field(default_factory=dict)
    gameplay_layout: Dict[str, Any] = field(default_factory=dict)
    spawn_zones: List[str] = field(default_factory=list)
    encounters: List[str] = field(default_factory=list)
    streaming_budget_mb: float = 2048.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level_name": self.level_name,
            "visual_layout": self.visual_layout,
            "gameplay_layout": self.gameplay_layout,
            "spawn_zones": self.spawn_zones,
            "encounters": self.encounters,
            "streaming_budget_mb": self.streaming_budget_mb,
        }
