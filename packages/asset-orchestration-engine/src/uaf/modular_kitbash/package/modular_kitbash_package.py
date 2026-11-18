"""
ModularKitbashPackage encapsulates complete, production-ready modular kits, assemblies, meshes, and blueprints for Unreal Engine.
UAF-81.39 Sections 140, 146.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import ModularKitbashSpecification
from ..validation.modular_kitbash_validator import ModularKitbashValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ModularKitbashPackage:
    kitbash_id: str
    spec: ModularKitbashSpecification
    static_mesh_path: str = "/Game/ModularKits/Meshes/SM_Default"
    blueprint_path: str = "/Game/ModularKits/Blueprints/BP_Default"
    validation_report: Optional[ModularKitbashValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kitbash_id": self.kitbash_id,
            "spec": self.spec.to_dict(),
            "static_mesh_path": self.static_mesh_path,
            "blueprint_path": self.blueprint_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
