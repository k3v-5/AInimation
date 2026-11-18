"""
UAF Animation Motion Models Package
"""

from .skeleton import (
    BoneRoleType,
    RigBoneNode,
    StandardSkeletonHierarchy,
    CharacterRigDefinition,
)
from .motion import (
    MotionClipType,
    MotionClip,
)

__all__ = [
    "BoneRoleType",
    "RigBoneNode",
    "StandardSkeletonHierarchy",
    "CharacterRigDefinition",
    "MotionClipType",
    "MotionClip",
]
