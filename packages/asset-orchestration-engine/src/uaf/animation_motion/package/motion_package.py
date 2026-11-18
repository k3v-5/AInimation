"""
AnimationMotionPackage encapsulates complete, production-ready animation and motion packages for Unreal Engine.
UAF-81.23 Sections 111, 112, 116, 122.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.skeleton import CharacterRigDefinition
from ..models.motion import MotionClip
from ..validation.motion_validator import AnimationMotionValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class AnimationMotionPackage:
    asset_id: str
    rig_def: CharacterRigDefinition
    clips: List[MotionClip] = field(default_factory=list)
    physics_asset_ref: str = "PHYS_Default"
    control_rig_ref: str = "CR_Default"
    validation_report: Optional[AnimationMotionValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "rig_def": self.rig_def.to_dict(),
            "clips": [c.to_dict() for c in self.clips],
            "physics_asset_ref": self.physics_asset_ref,
            "control_rig_ref": self.control_rig_ref,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
