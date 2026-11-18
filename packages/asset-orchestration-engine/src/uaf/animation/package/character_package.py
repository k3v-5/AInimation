"""
AnimatedCharacterPackage encapsulates fully rigged, skined, and animatable character assets.
UAF-81.9 Sections 145, 148, 160.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.classification import CharacterClassification
from ..models.clip import AnimationClip
from ..models.state_machine import AnimationBlueprintContract
from ..models.lod import AnimationLODProfile
from ..validation.character_validator import AnimatedCharacterQualityReport
from ...rigging.skeleton.skeleton_definition import CharacterSkeletonDefinition
from ...rigging.skinning.skinning_definition import SkinningDefinition
from ...rigging.rig.rig_definition import RigDefinition
from ...rigging.physics.physics_asset import PhysicsAssetDefinition
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class AnimatedCharacterPackage:
    asset_id: str
    classification: CharacterClassification
    skeleton: CharacterSkeletonDefinition
    skinning: SkinningDefinition
    rig: Optional[RigDefinition] = None
    animation_clips: List[AnimationClip] = field(default_factory=list)
    blueprint_contract: Optional[AnimationBlueprintContract] = None
    physics: Optional[PhysicsAssetDefinition] = None
    lod_profile: Optional[AnimationLODProfile] = None
    quality_report: Optional[AnimatedCharacterQualityReport] = None
    version: str = "1.0.0"

    @property
    def package_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "classification": self.classification.value,
            "skeleton": self.skeleton.to_dict(),
            "skinning": self.skinning.to_dict(),
            "rig": self.rig.to_dict() if self.rig else None,
            "animation_clips": [c.to_dict() for c in self.animation_clips],
            "blueprint_contract": self.blueprint_contract.to_dict() if self.blueprint_contract else None,
            "physics": self.physics.to_dict() if self.physics else None,
            "lod_profile": self.lod_profile.to_dict() if self.lod_profile else None,
            "quality_report": self.quality_report.to_dict() if self.quality_report else None,
            "version": self.version,
        }
