"""
TerrainWorldPackage encapsulates complete, production-ready terrain, biomes, road networks, and world partitions for Unreal Engine.
UAF-81.48 Sections 140, 142.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import TerrainWorldSpecification
from ..validation.terrain_world_validator import TerrainWorldValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class TerrainWorldPackage:
    world_id: str
    spec: TerrainWorldSpecification
    landscape_asset_path: str = "/Game/Worlds/Terrain/DefaultWorld/Landscape_DefaultWorld"
    world_partition_path: str = "/Game/Worlds/Terrain/DefaultWorld/Partition/WP_DefaultWorld"
    navmesh_path: str = "/Game/Worlds/Terrain/DefaultWorld/Navigation/Nav_DefaultWorld"
    validation_report: Optional[TerrainWorldValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "spec": self.spec.to_dict(),
            "landscape_asset_path": self.landscape_asset_path,
            "world_partition_path": self.world_partition_path,
            "navmesh_path": self.navmesh_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
