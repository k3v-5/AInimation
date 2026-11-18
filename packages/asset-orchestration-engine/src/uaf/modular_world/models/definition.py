"""
EnvironmentType, ModularKitProfile, and EnvironmentDefinition models.
UAF-81.19 Sections 3, 4, 6, 7, 8, 9, 18.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class EnvironmentType(str, Enum):
    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"
    URBAN = "URBAN"
    INDUSTRIAL = "INDUSTRIAL"
    MILITARY = "MILITARY"
    SCI_FI = "SCI_FI"
    FANTASY = "FANTASY"
    DUNGEON = "DUNGEON"
    CAVE = "CAVE"
    RUINS = "RUINS"
    CUSTOM = "CUSTOM"


@dataclass
class ModularKitProfile:
    kit_id: str
    grid_size_xyz: List[float] = field(default_factory=lambda: [100.0, 100.0, 300.0])  # cm (X, Y, Z)
    supported_module_types: List[str] = field(default_factory=lambda: [
        "WALL", "FLOOR", "CEILING", "DOOR", "WINDOW", "STAIR", "COLUMN", "PROP", "COVER"
    ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kit_id": self.kit_id,
            "grid_size_xyz": self.grid_size_xyz,
            "supported_module_types": self.supported_module_types,
        }


@dataclass
class EnvironmentDefinition:
    environment_id: str
    environment_type: EnvironmentType = EnvironmentType.INDUSTRIAL
    kit_profile: ModularKitProfile = field(default_factory=lambda: ModularKitProfile("Kit_Standard_100x300"))
    world_scale: float = 1.0
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment_id": self.environment_id,
            "environment_type": self.environment_type.value,
            "kit_profile": self.kit_profile.to_dict(),
            "world_scale": self.world_scale,
            "seed": self.seed,
        }
