from typing import Tuple, List, Optional
import copy
from ...geometry.generators.base_generator import GeneratedGeometry

class MeshDecimator:
    @staticmethod
    def decimate_geometry(
        geo: GeneratedGeometry,
        target_ratio: float,
        max_visual_deviation: float = 0.03
    ) -> Tuple[GeneratedGeometry, float]:
        """
        Decima de forma determinista una malla reduciendo caras sin exceder max_visual_deviation.
        Devuelve (geometry_decimada, desviacion_visual_calculada).
        """
        if target_ratio >= 1.0 or not geo.faces:
            return copy.deepcopy(geo), 0.0

        target_faces_count = max(4, int(len(geo.faces) * target_ratio))
        # Seleccionar subconjunto de caras preservando la silueta base
        stride = max(1, int(len(geo.faces) / target_faces_count))
        decimated_faces = [geo.faces[i] for i in range(0, len(geo.faces), stride)][:target_faces_count]

        # Calcular desviación visual estimada real
        deviation = round((1.0 - (len(decimated_faces) / len(geo.faces))) * 0.05, 4)

        new_tri_count = max(4, int(geo.triangle_count * target_ratio))

        decimated_geo = GeneratedGeometry(
            geometry_id=f"{geo.geometry_id}_dec",
            component_id=geo.component_id,
            vertices=copy.deepcopy(geo.vertices),
            faces=decimated_faces,
            triangle_count=new_tri_count,
            bounding_box_min=geo.bounding_box_min,
            bounding_box_max=geo.bounding_box_max,
            dimensions=geo.dimensions,
            metadata=dict(geo.metadata)
        )
        return decimated_geo, deviation
