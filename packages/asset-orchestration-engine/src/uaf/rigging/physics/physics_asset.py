"""
PhysicsAssetDefinition and ragdoll dynamics models.
UAF-81.5 Section 54.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class PhysicsBody:
    body_id: str
    bone_id: str
    shape_type: str = "CAPSULE"  # CAPSULE, BOX, SPHERE
    dimensions: List[float] = field(default_factory=lambda: [0.1, 0.1, 0.3])
    mass_kg: float = 5.0
    linear_damping: float = 0.1
    angular_damping: float = 0.05

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body_id": self.body_id,
            "bone_id": self.bone_id,
            "shape_type": self.shape_type,
            "dimensions": self.dimensions,
            "mass_kg": self.mass_kg,
            "linear_damping": self.linear_damping,
            "angular_damping": self.angular_damping,
        }


@dataclass
class PhysicsConstraint:
    constraint_id: str
    parent_bone: str
    child_bone: str
    angular_limit_degrees: float = 45.0
    twist_limit_degrees: float = 30.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "parent_bone": self.parent_bone,
            "child_bone": self.child_bone,
            "angular_limit_degrees": self.angular_limit_degrees,
            "twist_limit_degrees": self.twist_limit_degrees,
        }


@dataclass
class PhysicsAssetDefinition:
    physics_id: str
    skeleton_id: str
    bodies: List[PhysicsBody] = field(default_factory=list)
    constraints: List[PhysicsConstraint] = field(default_factory=list)

    @property
    def total_mass_kg(self) -> float:
        return sum(b.mass_kg for b in self.bodies)

    @property
    def physics_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "physics_id": self.physics_id,
            "skeleton_id": self.skeleton_id,
            "bodies": [b.to_dict() for b in self.bodies],
            "constraints": [c.to_dict() for c in self.constraints],
            "total_mass_kg": self.total_mass_kg,
        }

    @classmethod
    def create_standard_ragdoll(cls, physics_id: str, skeleton_id: str) -> "PhysicsAssetDefinition":
        bodies = [
            PhysicsBody("B_Pelvis", "pelvis", "CAPSULE", [0.15, 0.15, 0.2], mass_kg=15.0),
            PhysicsBody("B_Spine", "spine_01", "CAPSULE", [0.14, 0.14, 0.25], mass_kg=15.0),
            PhysicsBody("B_Chest", "chest", "CAPSULE", [0.16, 0.16, 0.25], mass_kg=20.0),
            PhysicsBody("B_Head", "head", "SPHERE", [0.12, 0.12, 0.12], mass_kg=5.0),
            PhysicsBody("B_UpperArm_L", "upperarm_L", "CAPSULE", [0.06, 0.06, 0.3], mass_kg=3.5),
            PhysicsBody("B_UpperArm_R", "upperarm_R", "CAPSULE", [0.06, 0.06, 0.3], mass_kg=3.5),
            PhysicsBody("B_LowerArm_L", "lowerarm_L", "CAPSULE", [0.05, 0.05, 0.25], mass_kg=2.0),
            PhysicsBody("B_LowerArm_R", "lowerarm_R", "CAPSULE", [0.05, 0.05, 0.25], mass_kg=2.0),
            PhysicsBody("B_Thigh_L", "thigh_L", "CAPSULE", [0.09, 0.09, 0.4], mass_kg=8.0),
            PhysicsBody("B_Thigh_R", "thigh_R", "CAPSULE", [0.09, 0.09, 0.4], mass_kg=8.0),
            PhysicsBody("B_Calf_L", "calf_L", "CAPSULE", [0.07, 0.07, 0.35], mass_kg=4.0),
            PhysicsBody("B_Calf_R", "calf_R", "CAPSULE", [0.07, 0.07, 0.35], mass_kg=4.0),
        ]
        constraints = [
            PhysicsConstraint("C_Pelvis_Spine", "pelvis", "spine_01", 30.0, 20.0),
            PhysicsConstraint("C_Spine_Chest", "spine_01", "chest", 30.0, 20.0),
            PhysicsConstraint("C_Chest_Head", "chest", "head", 45.0, 45.0),
            PhysicsConstraint("C_Chest_Arm_L", "chest", "upperarm_L", 80.0, 45.0),
            PhysicsConstraint("C_Chest_Arm_R", "chest", "upperarm_R", 80.0, 45.0),
            PhysicsConstraint("C_Elbow_L", "upperarm_L", "lowerarm_L", 130.0, 0.0),
            PhysicsConstraint("C_Elbow_R", "upperarm_R", "lowerarm_R", 130.0, 0.0),
            PhysicsConstraint("C_Pelvis_Thigh_L", "pelvis", "thigh_L", 70.0, 30.0),
            PhysicsConstraint("C_Pelvis_Thigh_R", "pelvis", "thigh_R", 70.0, 30.0),
            PhysicsConstraint("C_Knee_L", "thigh_L", "calf_L", 130.0, 0.0),
            PhysicsConstraint("C_Knee_R", "thigh_R", "calf_R", 130.0, 0.0),
        ]
        return cls(physics_id=physics_id, skeleton_id=skeleton_id, bodies=bodies, constraints=constraints)
