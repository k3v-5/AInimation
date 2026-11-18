"""
Universal Asset Factory (UAF) - Procedural Rigging, Animation & Motion Fabrication System (UAF-81.23)
"""

from .models import (
    BoneRoleType,
    RigBoneNode,
    StandardSkeletonHierarchy,
    CharacterRigDefinition,
    MotionClipType,
    MotionClip,
)

from .engine import (
    AnimationMotionFabricationPlatform,
)

from .validation import (
    AnimationMotionQualityScore,
    AnimationMotionValidationReport,
    AnimationMotionValidator,
)

from .package import (
    AnimationMotionPackage,
)

__all__ = [
    "BoneRoleType",
    "RigBoneNode",
    "StandardSkeletonHierarchy",
    "CharacterRigDefinition",
    "MotionClipType",
    "MotionClip",
    "AnimationMotionFabricationPlatform",
    "AnimationMotionQualityScore",
    "AnimationMotionValidationReport",
    "AnimationMotionValidator",
    "AnimationMotionPackage",
]
