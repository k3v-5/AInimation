"""
CharacterOrganicPackage encapsulates complete, production-ready organic characters for Unreal Engine.
UAF-81.26 Sections 123, 140, 141.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import OrganicCharacterDefinition
from ..validation.organic_validator import CharacterOrganicValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterOrganicPackage:
    asset_id: str
    character_def: OrganicCharacterDefinition
    skeletal_mesh_ref: str = "SK_Default"
    skeleton_ref: str = "SKEL_Default"
    lod_count: int = 4
    validation_report: Optional[CharacterOrganicValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "character_def": self.character_def.to_dict(),
            "skeletal_mesh_ref": self.skeletal_mesh_ref,
            "skeleton_ref": self.skeleton_ref,
            "lod_count": self.lod_count,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
