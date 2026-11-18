"""
ModularAssemblyPackage encapsulates complete, production-ready modular environments, architecture, and world partitions for Unreal Engine.
UAF-81.50 Sections 153, 156.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import ModularAssemblySpecification
from ..validation.modular_assembly_validator import ModularAssemblyValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ModularAssemblyPackage:
    environment_id: str
    spec: ModularAssemblySpecification
    level_asset_path: str = "/Game/Environments/Assembly/Levels/Default/L_Default"
    world_partition_path: str = "/Game/Environments/Assembly/Levels/Default/Partition/WP_Default"
    navmesh_path: str = "/Game/Environments/Assembly/Levels/Default/Navigation/Nav_Default"
    validation_report: Optional[ModularAssemblyValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment_id": self.environment_id,
            "spec": self.spec.to_dict(),
            "level_asset_path": self.level_asset_path,
            "world_partition_path": self.world_partition_path,
            "navmesh_path": self.navmesh_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
