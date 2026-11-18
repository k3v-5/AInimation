"""
MapAuthoringPackage encapsulates complete, production-ready levels, partitions, and navigation for Unreal Engine.
UAF-81.44 Sections 130, 146.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import MapAuthoringSpecification
from ..validation.map_authoring_validator import MapAuthoringValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class MapAuthoringPackage:
    map_id: str
    spec: MapAuthoringSpecification
    level_asset_path: str = "/Game/Maps/DefaultMap/Level_DefaultMap"
    world_partition_path: str = "/Game/Maps/DefaultMap/Partition/WP_DefaultMap"
    navmesh_path: str = "/Game/Maps/DefaultMap/Navigation/Nav_DefaultMap"
    validation_report: Optional[MapAuthoringValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_id": self.map_id,
            "spec": self.spec.to_dict(),
            "level_asset_path": self.level_asset_path,
            "world_partition_path": self.world_partition_path,
            "navmesh_path": self.navmesh_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
