"""
CharacterProdV2Package encapsulates complete, production-ready 2.0 characters with high-fidelity meshes, clothing, hair, facial rigs, and physics for Unreal Engine.
UAF-81.45 Sections 120, 152.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import CharacterProdV2Specification
from ..validation.character_prod_v2_validator import CharacterProdV2ValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterProdV2Package:
    character_id: str
    spec: CharacterProdV2Specification
    skeletal_mesh_path: str = "/Game/Characters/V2/Meshes/SK_Default"
    facial_anim_blueprint_path: str = "/Game/Characters/V2/Animations/FABP_Default"
    physics_asset_path: str = "/Game/Characters/V2/Physics/PHYS_Default"
    validation_report: Optional[CharacterProdV2ValidationReport] = None
    version: str = "2.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "spec": self.spec.to_dict(),
            "skeletal_mesh_path": self.skeletal_mesh_path,
            "facial_anim_blueprint_path": self.facial_anim_blueprint_path,
            "physics_asset_path": self.physics_asset_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
