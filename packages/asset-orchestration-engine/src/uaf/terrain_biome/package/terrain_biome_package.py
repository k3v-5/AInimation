"""
TerrainBiomePackage encapsulates production-ready procedural landscapes, biomes, foliage, and heightmaps for Unreal Engine.
UAF-81.36 Sections 126, 127.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import TerrainBiomeSpecification
from ..validation.terrain_biome_validator import TerrainBiomeValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class TerrainBiomePackage:
    terrain_id: str
    spec: TerrainBiomeSpecification
    landscape_asset_path: str = "/Game/Environments/Landscapes/DefaultLandscape"
    validation_report: Optional[TerrainBiomeValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "terrain_id": self.terrain_id,
            "spec": self.spec.to_dict(),
            "landscape_asset_path": self.landscape_asset_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
