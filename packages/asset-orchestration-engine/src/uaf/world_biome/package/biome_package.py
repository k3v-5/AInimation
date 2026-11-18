"""
WorldBiomePackage encapsulates complete, production-ready procedural worlds, terrains, biomes, and Unreal levels.
UAF-81.32 Sections 128, 129, 130.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import BiomeWorldDefinition
from ..validation.biome_validator import WorldBiomeValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldBiomePackage:
    asset_id: str
    world_def: BiomeWorldDefinition
    terrain_ref: str = "TR_Default"
    level_ref: str = "LV_Default"
    validation_report: Optional[WorldBiomeValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "world_def": self.world_def.to_dict(),
            "terrain_ref": self.terrain_ref,
            "level_ref": self.level_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
