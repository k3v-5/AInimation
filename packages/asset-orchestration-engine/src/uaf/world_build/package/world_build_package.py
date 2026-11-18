"""
WorldBuildPackage encapsulates complete, production-ready procedural worlds, levels, partitions, and streaming manifests for Unreal Engine.
UAF-81.40 Sections 149, 150, 176.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import WorldBuildSpecification
from ..validation.world_build_validator import WorldBuildValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldBuildPackage:
    world_id: str
    spec: WorldBuildSpecification
    level_asset_path: str = "/Game/Worlds/DefaultWorld/Level_DefaultWorld"
    world_partition_data_path: str = "/Game/Worlds/DefaultWorld/Partition/WP_DefaultWorld"
    validation_report: Optional[WorldBuildValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "spec": self.spec.to_dict(),
            "level_asset_path": self.level_asset_path,
            "world_partition_data_path": self.world_partition_data_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
