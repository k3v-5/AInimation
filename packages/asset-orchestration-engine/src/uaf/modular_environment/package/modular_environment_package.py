"""
ModularEnvironmentPackage encapsulates complete, production-ready modular rooms, buildings, facilities, and levels for Unreal Engine.
UAF-81.47 Sections 151, 167.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import ModularEnvironmentSpecification
from ..validation.modular_environment_validator import ModularEnvironmentValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ModularEnvironmentPackage:
    environment_id: str
    spec: ModularEnvironmentSpecification
    level_asset_path: str = "/Game/Environments/Modular/Levels/L_Default"
    navmesh_path: str = "/Game/Environments/Modular/Nav/Nav_Default"
    collision_asset_path: str = "/Game/Environments/Modular/Collision/COL_Default"
    validation_report: Optional[ModularEnvironmentValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment_id": self.environment_id,
            "spec": self.spec.to_dict(),
            "level_asset_path": self.level_asset_path,
            "navmesh_path": self.navmesh_path,
            "collision_asset_path": self.collision_asset_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
