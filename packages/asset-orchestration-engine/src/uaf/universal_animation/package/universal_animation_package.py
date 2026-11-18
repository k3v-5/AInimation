"""
Universal Animation Package & ProductionReadyAnimatedCharacter for Unreal Engine.
UAF-81.55 Sections 2, 130, 131, 132, 174.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher
from ..models.definition import (
    AnimationDefinition,
    AnimationClip,
    RetargetProfile55,
    BlendSpace55,
    AnimationMontage55,
    AnimationStateMachine55,
    MotionWarpingProfile55,
    FacialAnimationTrack55,
    AnimationCompressionProfile55,
    AnimationLODProfile55,
    RuntimeProfile55,
)
from ..validation.universal_animation_validator import AnimationValidationReport
from ...universal_character.package.universal_character_package import ProductionReadyCharacter


@dataclass
class ProductionReadyAnimatedCharacter:
    """
    Complete production asset representing a rigged character with full animation, retargeting, and runtime profiles (Section 2).
    """
    character: ProductionReadyCharacter
    animation: AnimationDefinition
    clips: List[AnimationClip] = field(default_factory=list)
    retarget: Optional[RetargetProfile55] = None
    blend_space: Optional[BlendSpace55] = None
    montages: List[AnimationMontage55] = field(default_factory=list)
    state_machine: Optional[AnimationStateMachine55] = None
    warping: Optional[MotionWarpingProfile55] = None
    facial_tracks: List[FacialAnimationTrack55] = field(default_factory=list)
    compression: AnimationCompressionProfile55 = field(default_factory=AnimationCompressionProfile55)
    lod_profile: AnimationLODProfile55 = field(default_factory=AnimationLODProfile55)
    runtime_profile: RuntimeProfile55 = field(default_factory=lambda: RuntimeProfile55("Runtime_01"))
    validation_report: Optional[AnimationValidationReport] = None

    # Unreal Asset Export Path
    export_path: str = "/Game/Animations/Anim_Character.uasset"

    @property
    def canonical_hash(self) -> str:
        payload = {
            "character_id": self.character.character_def.character_id,
            "animation_id": self.animation.animation_id,
            "duration": self.animation.duration,
            "sample_rate": self.animation.sample_rate,
            "track_count": len(self.animation.tracks),
            "export_path": self.export_path,
        }
        return CanonicalHasher.compute_hash(payload)

    def verify_readback(self) -> Dict[str, Any]:
        """
        Post-export / import readback validation checking structural integrity (Section 132).
        """
        return {
            "animation_id": self.animation.animation_id,
            "duration": self.animation.duration,
            "sample_rate": self.animation.sample_rate,
            "track_count": len(self.animation.tracks),
            "curve_count": len(self.animation.curves),
            "marker_count": len(self.animation.markers),
            "event_count": len(self.animation.events),
            "retarget_valid": self.retarget is not None,
            "state_machine_valid": self.state_machine is not None,
            "readback_passed": (
                self.animation.duration > 0.0 and
                self.animation.sample_rate > 0 and
                len(self.animation.tracks) > 0 and
                self.export_path.startswith("/Game/")
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_reference": self.character.character_def.character_id,
            "animation": self.animation.to_dict(),
            "clips": [c.to_dict() for c in self.clips],
            "retarget": self.retarget.to_dict() if self.retarget else None,
            "blend_space": self.blend_space.to_dict() if self.blend_space else None,
            "montages": [m.to_dict() for m in self.montages],
            "state_machine": self.state_machine.to_dict() if self.state_machine else None,
            "warping": self.warping.to_dict() if self.warping else None,
            "facial_tracks": [f.to_dict() for f in self.facial_tracks],
            "compression": self.compression.to_dict(),
            "lod_profile": self.lod_profile.to_dict(),
            "runtime_profile": self.runtime_profile.to_dict(),
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "export_metadata": {
                "export_path": self.export_path,
                "canonical_hash": self.canonical_hash,
            }
        }


# Alias for consistency with other UAF packages
UniversalAnimationPackage = ProductionReadyAnimatedCharacter
