"""
UniversalGeometryPackage encapsulates complete, production-ready static meshes, collision representations, and LODs for Unreal Engine.
UAF-81.53 Sections 138, 165.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import UniversalMeshSpecification
from ..validation.universal_geometry_validator import UniversalGeometryValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class UniversalGeometryPackage:
    mesh_id: str
    spec: UniversalMeshSpecification
    static_mesh_path: str = "/Game/Geometry/Meshes/Default/SM_Default"
    collision_mesh_path: str = "/Game/Geometry/Meshes/Default/Collision/UCX_Default"
    lod_mesh_path: str = "/Game/Geometry/Meshes/Default/LODs/LOD_Default"
    validation_report: Optional[UniversalGeometryValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mesh_id": self.mesh_id,
            "spec": self.spec.to_dict(),
            "static_mesh_path": self.static_mesh_path,
            "collision_mesh_path": self.collision_mesh_path,
            "lod_mesh_path": self.lod_mesh_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
