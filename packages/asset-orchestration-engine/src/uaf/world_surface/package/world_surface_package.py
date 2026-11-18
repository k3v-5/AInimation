"""
WorldSurfacePackage encapsulates complete territorial, biome, and surface data for Unreal Engine.
UAF-81.13 Sections 190, 191, 201.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..terrain.territory import TerritoryModel
from ..terrain.landmark import NaturalLandmark
from ..biomes.biome import BiomeProfile
from ..validation.world_surface_validator import WorldSurfaceValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldSurfacePackage:
    asset_id: str
    world_type: str
    territory: TerritoryModel
    biomes: List[BiomeProfile] = field(default_factory=list)
    landmarks: List[NaturalLandmark] = field(default_factory=list)
    validation_report: Optional[WorldSurfaceValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "world_type": self.world_type,
            "territory": self.territory.to_dict(),
            "biomes": [b.to_dict() for b in self.biomes],
            "landmarks": [lm.to_dict() for lm in self.landmarks],
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
