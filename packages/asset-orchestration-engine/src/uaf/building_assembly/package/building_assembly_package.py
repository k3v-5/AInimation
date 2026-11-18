"""
BuildingAssemblyPackage encapsulates validated, production-ready modular environments and levels for Unreal Engine.
UAF-81.35 Sections 136, 138.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import BuildingAssemblySpecification
from ..validation.building_assembly_validator import BuildingAssemblyValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class BuildingAssemblyPackage:
    world_id: str
    spec: BuildingAssemblySpecification
    level_asset_path: str = "/Game/Environments/Levels/DefaultLevel"
    validation_report: Optional[BuildingAssemblyValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "spec": self.spec.to_dict(),
            "level_asset_path": self.level_asset_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
