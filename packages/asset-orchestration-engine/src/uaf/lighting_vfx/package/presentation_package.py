"""
LightingVFXPackage encapsulates complete, production-ready lighting and VFX presentation packages for Unreal Engine.
UAF-81.25 Sections 157, 163, 164.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..models.presentation import PresentationDefinition25
from ..validation.presentation_validator import LightingVFXValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class LightingVFXPackage:
    asset_id: str
    presentation_def: PresentationDefinition25
    post_process_ref: str = "PP_Default"
    validation_report: Optional[LightingVFXValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "presentation_def": self.presentation_def.to_dict(),
            "post_process_ref": self.post_process_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
