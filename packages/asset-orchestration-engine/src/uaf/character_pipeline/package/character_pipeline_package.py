"""
CharacterPipelinePackage encapsulates production-ready skeletal characters, rigs, physics assets, and metadata for Unreal Engine.
UAF-81.37 Sections 153, 155.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.definition import CharacterProductionSpecification
from ..validation.character_pipeline_validator import CharacterPipelineValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterPipelinePackage:
    character_id: str
    spec: CharacterProductionSpecification
    skeletal_mesh_path: str = "/Game/Characters/Meshes/SK_Default"
    physics_asset_path: str = "/Game/Characters/Physics/PHYS_Default"
    validation_report: Optional[CharacterPipelineValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "spec": self.spec.to_dict(),
            "skeletal_mesh_path": self.skeletal_mesh_path,
            "physics_asset_path": self.physics_asset_path,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
