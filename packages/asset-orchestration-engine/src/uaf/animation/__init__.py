"""
Universal Asset Factory (UAF) - Animation, Rigging, Skinning & Character Runtime Fabric (UAF-81.9)
"""

from .models import (
    CharacterClassification,
    RigProfile,
    Keyframe,
    AnimationTrack,
    AnimationEventType,
    AnimationEvent,
    AnimationClip,
    AnimState,
    AnimTransition,
    AnimStateMachine,
    MontageDefinition,
    AnimationBlueprintContract,
    AnimationLODLevel,
    AnimationLODProfile,
)

from .validation import (
    CharacterBuildState,
    AnimatedCharacterQualityScore,
    AnimatedCharacterQualityReport,
    AnimatedCharacterValidator,
)

from .package import (
    AnimatedCharacterPackage,
)

__all__ = [
    "CharacterClassification",
    "RigProfile",
    "Keyframe",
    "AnimationTrack",
    "AnimationEventType",
    "AnimationEvent",
    "AnimationClip",
    "AnimState",
    "AnimTransition",
    "AnimStateMachine",
    "MontageDefinition",
    "AnimationBlueprintContract",
    "AnimationLODLevel",
    "AnimationLODProfile",
    "CharacterBuildState",
    "AnimatedCharacterQualityScore",
    "AnimatedCharacterQualityReport",
    "AnimatedCharacterValidator",
    "AnimatedCharacterPackage",
]
