"""
CharacterSuitePackage encapsulates complete production-ready character asset packages for Unreal Engine.
UAF-81.14 Sections 200, 208, 211.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.profile import CharacterProfile
from ..models.deformation import DeformationProfile, FaceProfile, CharacterLayer
from ..validation.suite_validator import CharacterValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterSuitePackage:
    asset_id: str
    profile: CharacterProfile
    deformation: DeformationProfile
    face: FaceProfile
    layers: List[CharacterLayer] = field(default_factory=list)
    validation_report: Optional[CharacterValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "profile": self.profile.to_dict(),
            "deformation": self.deformation.to_dict(),
            "face": self.face.to_dict(),
            "layers": [l.to_dict() for l in self.layers],
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
