"""
UAF Animation Models Package
"""

from .classification import CharacterClassification, RigProfile
from .clip import Keyframe, AnimationTrack, AnimationEventType, AnimationEvent, AnimationClip
from .state_machine import AnimState, AnimTransition, AnimStateMachine, MontageDefinition, AnimationBlueprintContract
from .lod import AnimationLODLevel, AnimationLODProfile

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
]
