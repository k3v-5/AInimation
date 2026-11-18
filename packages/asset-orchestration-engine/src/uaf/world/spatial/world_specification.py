"""
WorldSpecification models spatial level goals, themes, biomes, and budgets.
UAF-81.6 Section 4.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .world_grid import WorldGrid
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldSpecification:
    world_id: str
    seed: int = 42
    dimensions: List[float] = field(default_factory=lambda: [100.0, 100.0, 30.0])  # Width, Depth, Height in meters
    theme: str = "SCI_FI"
    biome: str = "INTERIOR_FACILITY"
    style: str = "BRUTALIST"
    density: float = 0.5  # 0.0 to 1.0
    gameplay_profile: str = "TACTICAL"
    performance_profile: str = "PRODUCTION"
    grid: WorldGrid = field(default_factory=WorldGrid)
    parameters: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    @property
    def world_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "seed": self.seed,
            "dimensions": self.dimensions,
            "theme": self.theme,
            "biome": self.biome,
            "style": self.style,
            "density": self.density,
            "gameplay_profile": self.gameplay_profile,
            "performance_profile": self.performance_profile,
            "grid": self.grid.to_dict(),
            "parameters": self.parameters,
            "version": self.version,
        }
