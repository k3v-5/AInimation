"""
BoneRole, BoneNode, and SkeletonHierarchy models.
UAF-81.17 Sections 8, 9, 10, 11, 12, 13, 14, 15, 18.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class BoneRole(str, Enum):
    ROOT = "ROOT"
    SPINE = "SPINE"
    CHEST = "CHEST"
    NECK = "NECK"
    HEAD = "HEAD"
    CLAVICLE = "CLAVICLE"
    UPPER_ARM = "UPPER_ARM"
    LOWER_ARM = "LOWER_ARM"
    HAND = "HAND"
    FINGER = "FINGER"
    UPPER_LEG = "UPPER_LEG"
    LOWER_LEG = "LOWER_LEG"
    FOOT = "FOOT"
    TOE = "TOE"
    WEAPON = "WEAPON"
    TAIL = "TAIL"
    WING = "WING"
    TENTACLE = "TENTACLE"
    FACIAL = "FACIAL"
    CUSTOM = "CUSTOM"


@dataclass
class BoneNode:
    name: str
    role: BoneRole
    parent: Optional[str] = None
    local_position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    local_rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role.value,
            "parent": self.parent,
            "local_position": self.local_position,
            "local_rotation": self.local_rotation,
        }


@dataclass
class SkeletonHierarchy:
    skeleton_id: str
    root_bone: str = "root"
    bones: Dict[str, BoneNode] = field(default_factory=dict)
    reference_pose: str = "T_POSE"  # "T_POSE", "A_POSE"

    def add_bone(self, bone: BoneNode) -> None:
        self.bones[bone.name] = bone

    def has_cycles(self) -> bool:
        """Verifies that the bone hierarchy forms a valid directed tree without cycles."""
        for bone_name in self.bones:
            visited = set()
            curr = bone_name
            while curr is not None:
                if curr in visited:
                    return True
                visited.add(curr)
                parent = self.bones[curr].parent if curr in self.bones else None
                curr = parent
        return False

    @property
    def skeleton_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_id": self.skeleton_id,
            "root_bone": self.root_bone,
            "bones": {k: v.to_dict() for k, v in sorted(self.bones.items())},
            "reference_pose": self.reference_pose,
        }

    @classmethod
    def create_standard_humanoid_skeleton(cls, skeleton_id: str = "SK_Humanoid_Standard") -> "SkeletonHierarchy":
        skel = cls(skeleton_id=skeleton_id, root_bone="root")
        skel.add_bone(BoneNode("root", BoneRole.ROOT, None))
        skel.add_bone(BoneNode("pelvis", BoneRole.SPINE, "root", [0.0, 0.0, 1.0]))
        skel.add_bone(BoneNode("spine_01", BoneRole.SPINE, "pelvis", [0.0, 0.0, 0.2]))
        skel.add_bone(BoneNode("chest", BoneRole.CHEST, "spine_01", [0.0, 0.0, 0.3]))
        skel.add_bone(BoneNode("neck_01", BoneRole.NECK, "chest", [0.0, 0.0, 0.2]))
        skel.add_bone(BoneNode("head", BoneRole.HEAD, "neck_01", [0.0, 0.0, 0.15]))

        # Arms
        skel.add_bone(BoneNode("upperarm_l", BoneRole.UPPER_ARM, "chest", [0.2, 0.0, 0.0]))
        skel.add_bone(BoneNode("lowerarm_l", BoneRole.LOWER_ARM, "upperarm_l", [0.3, 0.0, 0.0]))
        skel.add_bone(BoneNode("hand_l", BoneRole.HAND, "lowerarm_l", [0.25, 0.0, 0.0]))

        skel.add_bone(BoneNode("upperarm_r", BoneRole.UPPER_ARM, "chest", [-0.2, 0.0, 0.0]))
        skel.add_bone(BoneNode("lowerarm_r", BoneRole.LOWER_ARM, "upperarm_r", [-0.3, 0.0, 0.0]))
        skel.add_bone(BoneNode("hand_r", BoneRole.HAND, "lowerarm_r", [-0.25, 0.0, 0.0]))

        # Legs
        skel.add_bone(BoneNode("thigh_l", BoneRole.UPPER_LEG, "pelvis", [0.1, 0.0, -0.1]))
        skel.add_bone(BoneNode("calf_l", BoneRole.LOWER_LEG, "thigh_l", [0.0, 0.0, -0.45]))
        skel.add_bone(BoneNode("foot_l", BoneRole.FOOT, "calf_l", [0.0, 0.0, -0.45]))

        skel.add_bone(BoneNode("thigh_r", BoneRole.UPPER_LEG, "pelvis", [-0.1, 0.0, -0.1]))
        skel.add_bone(BoneNode("calf_r", BoneRole.LOWER_LEG, "thigh_r", [0.0, 0.0, -0.45]))
        skel.add_bone(BoneNode("foot_r", BoneRole.FOOT, "calf_r", [0.0, 0.0, -0.45]))

        return skel
