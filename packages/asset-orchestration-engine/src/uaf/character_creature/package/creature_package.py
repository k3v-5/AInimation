"""
CharacterCreaturePackage encapsulates complete, production-ready character and creature packages for Unreal Engine.
UAF-81.21 Sections 152, 169, 171.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.definition import CharacterDefinition21
from ..models.equipment import BodyPartType, ModularEquipmentLayer
from ..validation.creature_validator import CharacterCreatureValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterCreaturePackage:
    asset_id: str
    character_def: CharacterDefinition21
    body_parts: List[BodyPartType] = field(default_factory=list)
    equipment_layers: List[ModularEquipmentLayer] = field(default_factory=list)
    skeleton_ref: str = "SKEL_Humanoid_Mannequin"
    validation_report: Optional[CharacterCreatureValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "character_def": self.character_def.to_dict(),
            "body_parts": [p.value for p in self.body_parts],
            "equipment_layers": [l.to_dict() for l in self.equipment_layers],
            "skeleton_ref": self.skeleton_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
