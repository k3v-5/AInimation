"""
Universal Asset Factory (UAF) - Character Rigging, Skinning & Animation Fabrication System (UAF-81.17)
"""

from .models import (
    BoneRole,
    BoneNode,
    SkeletonHierarchy,
    IKSolverType,
    IKChain,
    SkinningMethod,
    SkinningWeightData,
)

from .engine import (
    CharacterAnimationFabricator,
)

from .validation import (
    CharacterAnimationQualityScore,
    CharacterAnimationValidationReport,
    CharacterAnimationValidator,
)

from .package import (
    CharacterAnimationPackage,
)

__all__ = [
    "BoneRole",
    "BoneNode",
    "SkeletonHierarchy",
    "IKSolverType",
    "IKChain",
    "SkinningMethod",
    "SkinningWeightData",
    "CharacterAnimationFabricator",
    "CharacterAnimationQualityScore",
    "CharacterAnimationValidationReport",
    "CharacterAnimationValidator",
    "CharacterAnimationPackage",
]
