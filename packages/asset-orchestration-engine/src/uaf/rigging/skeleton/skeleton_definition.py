"""
CharacterSkeletonDefinition and BindPose models.
UAF-81.5 Sections 4, 8, 9, 14, 15.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .bone import BoneDefinition, BoneRole
from ...core.hashing.canonical_hasher import CanonicalHasher


class BindPoseType(str, Enum):
    A_POSE = "A_POSE"
    T_POSE = "T_POSE"
    RELAXED = "RELAXED"
    CUSTOM = "CUSTOM"


class SkeletonArchetype(str, Enum):
    HUMANOID = "HUMANOID"
    QUADRUPED = "QUADRUPED"
    ROBOT = "ROBOT"
    CREATURE = "CREATURE"
    INSECTOID = "INSECTOID"
    CUSTOM = "CUSTOM"


@dataclass
class CharacterSkeletonDefinition:
    skeleton_id: str
    root_bone_id: str
    archetype: SkeletonArchetype = SkeletonArchetype.HUMANOID
    bind_pose: BindPoseType = BindPoseType.A_POSE
    bones: Dict[str, BoneDefinition] = field(default_factory=dict)
    version: str = "1.0.0"
    scale: float = 1.0  # meters
    axis_conventions: Dict[str, str] = field(
        default_factory=lambda: {"up_axis": "Z", "forward_axis": "Y", "right_axis": "X"}
    )

    @property
    def bone_count(self) -> int:
        return len(self.bones)

    def get_bone(self, bone_id: str) -> Optional[BoneDefinition]:
        return self.bones.get(bone_id)

    def get_children_of(self, parent_id: str) -> List[BoneDefinition]:
        return [b for b in self.bones.values() if b.parent_id == parent_id]

    @property
    def skeleton_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_id": self.skeleton_id,
            "root_bone_id": self.root_bone_id,
            "archetype": self.archetype.value,
            "bind_pose": self.bind_pose.value,
            "bones": {k: v.to_dict() for k, v in self.bones.items()},
            "version": self.version,
            "scale": self.scale,
            "axis_conventions": self.axis_conventions,
        }
