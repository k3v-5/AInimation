"""
WorldFabricationPackage encapsulates complete production-ready world asset packages for Unreal Engine.
UAF-81.16 Sections 2, 235, 240.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.world_def import WorldDefinition
from ..models.features import WaterBody, RoadNetwork, WorldDistrict, GameplayZone
from ...world_surface.biomes.biome import BiomeProfile
from ..validation.world_validator import WorldValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldFabricationPackage:
    asset_id: str
    world_definition: WorldDefinition
    biomes: List[BiomeProfile] = field(default_factory=list)
    water_bodies: List[WaterBody] = field(default_factory=list)
    road_network: Optional[RoadNetwork] = None
    districts: List[WorldDistrict] = field(default_factory=list)
    gameplay_zones: List[GameplayZone] = field(default_factory=list)
    validation_report: Optional[WorldValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "world_definition": self.world_definition.to_dict(),
            "biomes": [b.to_dict() for b in self.biomes],
            "water_bodies": [wb.to_dict() for wb in self.water_bodies],
            "road_network": self.road_network.to_dict() if self.road_network else None,
            "districts": [d.to_dict() for d in self.districts],
            "gameplay_zones": [z.to_dict() for z in self.gameplay_zones],
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
