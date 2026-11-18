"""
PBRSurfacePackage encapsulates complete, production-ready PBR materials, master shaders, instances, and textures for Unreal Engine.
UAF-81.43 Sections 166, 178.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import PBRSurfaceSpecification
from ..validation.pbr_surface_validator import PBRSurfaceValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class PBRSurfacePackage:
    material_id: str
    spec: PBRSurfaceSpecification
    master_material_path: str = "/Game/Materials/Masters/M_Default"
    material_instance_path: str = "/Game/Materials/Instances/MI_Default"
    texture_set_path: str = "/Game/Textures/Sets/T_Default"
    validation_report: Optional[PBRSurfaceValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_id": self.material_id,
            "spec": self.spec.to_dict(),
            "master_material_path": self.master_material_path,
            "material_instance_path": self.material_instance_path,
            "texture_set_path": self.texture_set_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
