"""
UAF Rigging Skeleton Package
"""

from .bone import BoneRole, BoneDefinition
from .skeleton_definition import BindPoseType, SkeletonArchetype, CharacterSkeletonDefinition
from .skeleton_builder import SkeletonBuilder

__all__ = [
    "BoneRole",
    "BoneDefinition",
    "BindPoseType",
    "SkeletonArchetype",
    "CharacterSkeletonDefinition",
    "SkeletonBuilder",
]
