"""
CharacterAssemblyPackage encapsulates complete, production-ready rigged, skinned, and retargeted characters for Unreal Engine.
UAF-81.42 Sections 144, 148, 163.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import CharacterAssemblySpecification
from ..validation.character_assembly_validator import CharacterAssemblyValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterAssemblyPackage:
    character_id: str
    spec: CharacterAssemblySpecification
    skeletal_mesh_path: str = "/Game/Characters/Meshes/SK_Default"
    anim_blueprint_path: str = "/Game/Characters/Animations/ABP_Default"
    physics_asset_path: str = "/Game/Characters/Physics/PHYS_Default"
    validation_report: Optional[CharacterAssemblyValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "spec": self.spec.to_dict(),
            "skeletal_mesh_path": self.skeletal_mesh_path,
            "anim_blueprint_path": self.anim_blueprint_path,
            "physics_asset_path": self.physics_asset_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
