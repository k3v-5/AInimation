"""
NaturalEcosystemPackage encapsulates complete, production-ready natural landscapes, biomes, foliage, and water systems for Unreal Engine.
UAF-81.51 Sections 139, 142.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import NaturalEcosystemSpecification
from ..validation.natural_ecosystem_validator import NaturalEcosystemValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class NaturalEcosystemPackage:
    ecosystem_id: str
    spec: NaturalEcosystemSpecification
    landscape_asset_path: str = "/Game/Environments/Natural/Default/Landscape_Default"
    foliage_asset_path: str = "/Game/Environments/Natural/Default/Foliage/Foliage_Default"
    water_mesh_path: str = "/Game/Environments/Natural/Default/Water/WaterMesh_Default"
    navmesh_path: str = "/Game/Environments/Natural/Default/Navigation/Nav_Default"
    validation_report: Optional[NaturalEcosystemValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ecosystem_id": self.ecosystem_id,
            "spec": self.spec.to_dict(),
            "landscape_asset_path": self.landscape_asset_path,
            "foliage_asset_path": self.foliage_asset_path,
            "water_mesh_path": self.water_mesh_path,
            "navmesh_path": self.navmesh_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
