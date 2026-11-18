from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from .collision_profile import CollisionProfile, CollisionType
from ...geometry.generators.base_generator import GeneratedGeometry

@dataclass
class CollisionHull:
    hull_name: str
    hull_type: CollisionType
    vertices: List[Tuple[float, float, float]]
    dimensions: Tuple[float, float, float]

class CollisionGenerator:
    @staticmethod
    def generate_collision(
        asset_name: str,
        components_geometry: Dict[str, GeneratedGeometry],
        profile: CollisionProfile
    ) -> List[CollisionHull]:
        if profile.collision_type == CollisionType.NONE:
            return []

        # Calcular bounding box global acumulado
        all_verts = []
        for geo in components_geometry.values():
            all_verts.extend(geo.vertices)

        if not all_verts:
            return []

        min_x = min(v[0] for v in all_verts)
        max_x = max(v[0] for v in all_verts)
        min_y = min(v[1] for v in all_verts)
        max_y = max(v[1] for v in all_verts)
        min_z = min(v[2] for v in all_verts)
        max_z = max(v[2] for v in all_verts)

        w = max_x - min_x
        d = max_y - min_y
        h = max_z - min_z

        # Generar caja envolvente simplificada UCX_
        hull_verts = [
            (min_x, min_y, min_z), (max_x, min_y, min_z), (max_x, max_y, min_z), (min_x, max_y, min_z),
            (min_x, min_y, max_z), (max_x, min_y, max_z), (max_x, max_y, max_z), (min_x, max_y, max_z)
        ]

        hull_name = f"UCX_{asset_name}_01"
        return [CollisionHull(
            hull_name=hull_name,
            hull_type=profile.collision_type,
            vertices=hull_verts,
            dimensions=(w, d, h)
        )]
