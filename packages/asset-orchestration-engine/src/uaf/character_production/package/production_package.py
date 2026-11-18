"""
CharacterProductionPackage encapsulates complete, animation-ready character packages for Unreal Engine.
UAF-81.29 Sections 145, 146.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import ProductionCharacterDefinition
from ..validation.production_validator import CharacterProductionValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterProductionPackage:
    asset_id: str
    char_def: ProductionCharacterDefinition
    skeletal_mesh_ref: str = "SK_Default"
    skeleton_ref: str = "SKEL_Default"
    physics_asset_ref: str = "PHYS_Default"
    lod_count: int = 4
    validation_report: Optional[CharacterProductionValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "char_def": self.char_def.to_dict(),
            "skeletal_mesh_ref": self.skeletal_mesh_ref,
            "skeleton_ref": self.skeleton_ref,
            "physics_asset_ref": self.physics_asset_ref,
            "lod_count": self.lod_count,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
