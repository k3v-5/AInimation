from enum import Enum
from typing import Tuple, List, Dict
from ...geometry.generators.base_generator import GeneratedGeometry

class PivotType(str, Enum):
    ORIGIN = "ORIGIN"
    CENTER = "CENTER"
    BOTTOM_CENTER = "BOTTOM_CENTER"
    CUSTOM = "CUSTOM"

class PivotManager:
    @staticmethod
    def adjust_pivot(
        components_geometry: Dict[str, GeneratedGeometry],
        pivot_type: PivotType = PivotType.BOTTOM_CENTER
    ) -> Tuple[Dict[str, GeneratedGeometry], Tuple[float, float, float]]:
        """
        Ajusta el origen y los vértices de las geometrías según el PivotType.
        Devuelve (geometrias_ajustadas, offset_aplicado).
        """
        all_verts = []
        for geo in components_geometry.values():
            all_verts.extend(geo.vertices)

        if not all_verts or pivot_type == PivotType.ORIGIN:
            return components_geometry, (0.0, 0.0, 0.0)

        min_z = min(v[2] for v in all_verts)
        max_z = max(v[2] for v in all_verts)
        center_x = (min(v[0] for v in all_verts) + max(v[0] for v in all_verts)) / 2.0
        center_y = (min(v[1] for v in all_verts) + max(v[1] for v in all_verts)) / 2.0
        center_z = (min_z + max_z) / 2.0

        if pivot_type == PivotType.BOTTOM_CENTER:
            offset = (-center_x, -center_y, -min_z)
        elif pivot_type == PivotType.CENTER:
            offset = (-center_x, -center_y, -center_z)
        else:
            offset = (0.0, 0.0, 0.0)

        adjusted_geos = {}
        for cid, geo in components_geometry.items():
            new_verts = [(v[0] + offset[0], v[1] + offset[1], v[2] + offset[2]) for v in geo.vertices]
            adj_geo = GeneratedGeometry(
                geometry_id=geo.geometry_id,
                component_id=geo.component_id,
                vertices=new_verts,
                faces=geo.faces,
                triangle_count=geo.triangle_count,
                bounding_box_min=(geo.bounding_box_min[0] + offset[0], geo.bounding_box_min[1] + offset[1], geo.bounding_box_min[2] + offset[2]),
                bounding_box_max=(geo.bounding_box_max[0] + offset[0], geo.bounding_box_max[1] + offset[1], geo.bounding_box_max[2] + offset[2]),
                dimensions=geo.dimensions,
                metadata=geo.metadata
            )
            adjusted_geos[cid] = adj_geo

        return adjusted_geos, offset
