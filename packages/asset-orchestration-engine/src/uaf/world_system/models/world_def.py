"""
WorldBounds and WorldDefinition models.
UAF-81.16 Sections 3, 4, 5, 6, 7, 8, 9, 10.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldBounds:
    min_x: float = -1000.0
    max_x: float = 1000.0
    min_y: float = -1000.0
    max_y: float = 1000.0
    min_z: float = 0.0
    max_z: float = 300.0

    @property
    def area_m2(self) -> float:
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
            "min_z": self.min_z,
            "max_z": self.max_z,
            "area_m2": self.area_m2,
        }


@dataclass
class WorldDefinition:
    world_id: str
    seed: int = 42
    bounds: WorldBounds = field(default_factory=WorldBounds)
    origin: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    generator_version: str = "1.0.0"

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "seed": self.seed,
            "bounds": self.bounds.to_dict(),
            "origin": self.origin,
            "generator_version": self.generator_version,
        }
