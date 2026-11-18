"""
Collision mesh and simplified physics primitive generation.
UAF-81.3 Sections 62, 63.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.mesh_data import MeshData
from ..models.bounding_volume import AABB


class CollisionType(str, Enum):
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    CONVEX_HULL = "CONVEX_HULL"
    COMPLEX = "COMPLEX"


@dataclass
class CollisionShape:
    shape_type: CollisionType
    dimensions: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    center: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    policy: str = "world_static"  # "world_static", "character", "physics", "weapon"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape_type": self.shape_type.value,
            "dimensions": self.dimensions,
            "center": self.center,
            "policy": self.policy,
        }


class CollisionGenerator:
    """
    Generates simplified collision volumes from detailed render geometry.
    """
    @classmethod
    def generate_from_mesh(
        cls,
        mesh: MeshData,
        collision_type: CollisionType = CollisionType.BOX,
        policy: str = "world_static",
    ) -> CollisionShape:
        aabb = mesh.calculate_aabb()

        if collision_type == CollisionType.SPHERE:
            radius = max(aabb.dimensions) / 2.0
            return CollisionShape(
                shape_type=CollisionType.SPHERE,
                dimensions=[radius, radius, radius],
                center=aabb.center,
                policy=policy,
            )
        elif collision_type == CollisionType.CAPSULE:
            radius = max(aabb.dimensions[0], aabb.dimensions[1]) / 2.0
            height = max(0.1, aabb.dimensions[2])
            return CollisionShape(
                shape_type=CollisionType.CAPSULE,
                dimensions=[radius, radius, height],
                center=aabb.center,
                policy=policy,
            )
        else:  # BOX or CONVEX default
            return CollisionShape(
                shape_type=CollisionType.BOX,
                dimensions=aabb.dimensions,
                center=aabb.center,
                policy=policy,
            )
