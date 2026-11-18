from enum import Enum
from dataclasses import dataclass

class CollisionType(str, Enum):
    NONE = "NONE"
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    CONVEX = "CONVEX"
    AUTO_CONVEX = "AUTO_CONVEX"

@dataclass
class CollisionProfile:
    collision_type: CollisionType = CollisionType.CONVEX
    max_convex_hulls: int = 4
    max_vertices_per_hull: int = 32
