from typing import Tuple, Optional, List
from .collision_generator import CollisionHull
from .collision_profile import CollisionProfile

class CollisionValidator:
    @staticmethod
    def validate_collision(
        hulls: List[CollisionHull],
        profile: CollisionProfile
    ) -> Tuple[bool, Optional[str]]:
        if len(hulls) > profile.max_convex_hulls:
            return False, f"COLLISION_BUDGET_EXCEEDED: Asset has {len(hulls)} hulls, exceeding limit of {profile.max_convex_hulls}."

        for h in hulls:
            if len(h.vertices) > profile.max_vertices_per_hull:
                return False, f"COLLISION_BUDGET_EXCEEDED: Hull '{h.hull_name}' has {len(h.vertices)} vertices, exceeding limit of {profile.max_vertices_per_hull}."

        return True, None
