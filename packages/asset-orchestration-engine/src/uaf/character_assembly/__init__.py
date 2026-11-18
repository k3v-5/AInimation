"""
Universal Asset Factory (UAF) - Character Rigging, Skinning, Animation, Retargeting & Unreal Character Assembly System (UAF-81.42)
"""

from .models import (
    CharacterClassification42,
    SkeletonProfile42,
    ControlRigType42,
    RetargetProfile42,
    SkeletalDimensions42,
    CharacterAssemblySpecification,
)

from .engine import (
    CharacterAssemblyFabricationPlatform,
)

from .validation import (
    CharacterAssemblyQualityScore,
    CharacterAssemblyValidationReport,
    CharacterAssemblyValidator,
)

from .package import (
    CharacterAssemblyPackage,
)

__all__ = [
    "CharacterClassification42",
    "SkeletonProfile42",
    "ControlRigType42",
    "RetargetProfile42",
    "SkeletalDimensions42",
    "CharacterAssemblySpecification",
    "CharacterAssemblyFabricationPlatform",
    "CharacterAssemblyQualityScore",
    "CharacterAssemblyValidationReport",
    "CharacterAssemblyValidator",
    "CharacterAssemblyPackage",
]
