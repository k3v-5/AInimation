"""
ModularArchitecturePackage encapsulates complete, production-ready modular architectural kits for Unreal Engine.
UAF-81.31 Sections 145, 146.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from ..models.definition import ModularArchitectureKitDefinition
from ..validation.architecture_validator import ModularArchitectureValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ModularArchitecturePackage:
    asset_id: str
    kit_def: ModularArchitectureKitDefinition
    static_mesh_refs: List[str] = field(default_factory=list)
    master_material_ref: str = "M_Master_ModularArchitecture"
    validation_report: Optional[ModularArchitectureValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "kit_def": self.kit_def.to_dict(),
            "static_mesh_refs": self.static_mesh_refs,
            "master_material_ref": self.master_material_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
