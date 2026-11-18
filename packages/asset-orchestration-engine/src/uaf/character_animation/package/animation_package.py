"""
CharacterAnimationPackage encapsulates complete, production-ready character animation packages for Unreal Engine.
UAF-81.17 Sections 213, 217, 219.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.skeleton import SkeletonHierarchy
from ..models.ik import IKChain
from ..models.skinning import SkinningWeightData
from ...animation.models.clip import AnimationClip
from ..validation.animation_validator import CharacterAnimationValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class CharacterAnimationPackage:
    asset_id: str
    skeleton: SkeletonHierarchy
    ik_chains: List[IKChain] = field(default_factory=list)
    skinning: Optional[SkinningWeightData] = None
    clips: Dict[str, AnimationClip] = field(default_factory=dict)
    physics_bodies: List[str] = field(default_factory=list)
    validation_report: Optional[CharacterAnimationValidationReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "skeleton": self.skeleton.to_dict(),
            "ik_chains": [ik.to_dict() for ik in self.ik_chains],
            "skinning": self.skinning.to_dict() if self.skinning else None,
            "clips": {k: v.to_dict() for k, v in sorted(self.clips.items())},
            "physics_bodies": self.physics_bodies,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
