"""
CharacterCreatureRigPackage encapsulates complete, production-ready procedural characters, creatures, and rigs for Unreal Engine.
UAF-81.33 Sections 124, 125, 141.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import CharacterCreatureRigDefinition
from ..validation.character_creature_validator import CharacterCreatureRigValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterCreatureRigPackage:
    asset_id: str
    character_def: CharacterCreatureRigDefinition
    skeletal_mesh_ref: str = "SK_Default"
    skeleton_ref: str = "SKEL_Default"
    physics_asset_ref: str = "PHYS_Default"
    validation_report: Optional[CharacterCreatureRigValidationReport] = None
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
            "physics_asset_ref": self.physics_asset_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
