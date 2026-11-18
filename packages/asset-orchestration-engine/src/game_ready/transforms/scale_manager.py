from typing import Tuple, Dict
from ...geometry.generators.base_generator import GeneratedGeometry

class ScaleManager:
    @staticmethod
    def convert_meters_to_centimeters(components_geometry: Dict[str, GeneratedGeometry]) -> Dict[str, GeneratedGeometry]:
        """
        Convierte deterministamente las coordenadas de metros a centímetros Unreal (factor 100.0).
        """
        scaled_geos = {}
        for cid, geo in components_geometry.items():
            new_verts = [(v[0] * 100.0, v[1] * 100.0, v[2] * 100.0) for v in geo.vertices]
            w, d, h = geo.dimensions
            scaled = GeneratedGeometry(
                geometry_id=f"{geo.geometry_id}_uu",
                component_id=geo.component_id,
                vertices=new_verts,
                faces=geo.faces,
                triangle_count=geo.triangle_count,
                bounding_box_min=(geo.bounding_box_min[0] * 100.0, geo.bounding_box_min[1] * 100.0, geo.bounding_box_min[2] * 100.0),
                bounding_box_max=(geo.bounding_box_max[0] * 100.0, geo.bounding_box_max[1] * 100.0, geo.bounding_box_max[2] * 100.0),
                dimensions=(w * 100.0, d * 100.0, h * 100.0),
                metadata=dict(geo.metadata)
            )
            scaled_geos[cid] = scaled
        return scaled_geos
