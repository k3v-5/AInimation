"""
BoneRoleType, RigBoneNode, StandardSkeletonHierarchy, and CharacterRigDefinition models.
UAF-81.23 Sections 3, 4, 5, 7, 8, 12, 13.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from collections import deque
from ...core.hashing.canonical_hasher import CanonicalHasher


class BoneRoleType(str, Enum):
    ROOT = "ROOT"
    PELVIS = "PELVIS"
    SPINE = "SPINE"
    CHEST = "CHEST"
    NECK = "NECK"
    HEAD = "HEAD"
    CLAVICLE = "CLAVICLE"
    LIMB_UPPER = "LIMB_UPPER"
    LIMB_LOWER = "LIMB_LOWER"
    HAND = "HAND"
    FOOT = "FOOT"
    TOE = "TOE"
    WEAPON = "WEAPON"
    FACIAL = "FACIAL"
    SECONDARY = "SECONDARY"
    HELPER = "HELPER"


@dataclass
class RigBoneNode:
    bone_id: str
    role: BoneRoleType
    parent: Optional[str] = None
    is_deform: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone_id": self.bone_id,
            "role": self.role.value,
            "parent": self.parent,
            "is_deform": self.is_deform,
        }


@dataclass
class StandardSkeletonHierarchy:
    bones: Dict[str, RigBoneNode] = field(default_factory=dict)

    def add_bone(self, bone: RigBoneNode) -> None:
        self.bones[bone.bone_id] = bone

    def find_root(self) -> Optional[RigBoneNode]:
        roots = [b for b in self.bones.values() if b.parent is None]
        return roots[0] if len(roots) == 1 else None

    def has_cycles(self) -> bool:
        visited = set()
        in_stack = set()

        def dfs(bone_id: str) -> bool:
            visited.add(bone_id)
            in_stack.add(bone_id)
            for child in [b.bone_id for b in self.bones.values() if b.parent == bone_id]:
                if child not in visited:
                    if dfs(child):
                        return True
                elif child in in_stack:
                    return True
            in_stack.remove(bone_id)
            return False

        for b_id in self.bones:
            if b_id not in visited:
                if dfs(b_id):
                    return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {k: v.to_dict() for k, v in sorted(self.bones.items())}


@dataclass
class CharacterRigDefinition:
    character_id: str
    rig_profile: str = "HUMANOID_STANDARD"
    skeleton: StandardSkeletonHierarchy = field(default_factory=StandardSkeletonHierarchy)
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "rig_profile": self.rig_profile,
            "skeleton": self.skeleton.to_dict(),
            "seed": self.seed,
        }
