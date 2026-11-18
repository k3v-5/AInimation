"""
CharacterCreaturePackage encapsulates complete, production-ready characters, creatures, rigs, and physics for Unreal Engine.
UAF-81.49 Sections 141, 157.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import CharacterCreatureSpecification
from ..validation.character_creature_validator import CharacterCreatureValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterCreaturePackage:
    character_id: str
    spec: CharacterCreatureSpecification
    skeletal_mesh_path: str = "/Game/Characters/Production/Meshes/SK_Default"
    anim_blueprint_path: str = "/Game/Characters/Production/Animations/ABP_Default"
    physics_asset_path: str = "/Game/Characters/Production/Physics/PHYS_Default"
    validation_report: Optional[CharacterCreatureValidationReport] = None
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
