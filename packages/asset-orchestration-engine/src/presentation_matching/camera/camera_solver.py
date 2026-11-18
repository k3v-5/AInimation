import math
from typing import Dict, Any, Optional, Tuple
from ..core.presentation_types import ProjectionType, InferenceConfidenceLevel
from ..core.presentation_schema import CameraConfiguration

class CameraSolver:
    @classmethod
    def solve_camera(
        cls,
        bounds: Dict[str, Any],
        reference_analysis: Optional[Any] = None,
        projection: ProjectionType = ProjectionType.PERSPECTIVE
    ) -> CameraConfiguration:
        dims = bounds.get("dimensions", {"x": 1.0, "y": 1.0, "z": 1.0})
        max_dim = max(dims.get("x", 1.0), dims.get("y", 1.0), dims.get("z", 1.0))
        target_z = dims.get("z", 1.0) * 0.5

        if projection == ProjectionType.ORTHOGRAPHIC:
            ortho_scale = max_dim * 1.5
            return CameraConfiguration(
                projection=ProjectionType.ORTHOGRAPHIC,
                orthographic_scale=round(ortho_scale, 2),
                distance=max_dim * 3.0,
                position=(max_dim * 2.0, -max_dim * 2.0, target_z + max_dim),
                rotation=(60.0, 0.0, 45.0),
                target_position=(0.0, 0.0, target_z),
                confidence=0.95,
                inference_level=InferenceConfidenceLevel.KNOWN
            )

        # Perspectiva
        focal = 50.0 # 50mm estándar
        sensor_w = 36.0
        fov = round(2.0 * math.atan((sensor_w / 2.0) / focal) * (180.0 / math.pi), 1)

        # Distancia requerida para encuadre del sujeto al 78% del frame
        occupancy = 0.78
        distance = round((max_dim / (2.0 * math.tan(math.radians(fov / 2.0)) * occupancy)), 2)
        distance = max(distance, max_dim * 1.8)

        # Posicionamiento en 3/4 isométrica suave
        azimuth = 45.0
        elevation = 30.0
        rad_az = math.radians(azimuth)
        rad_el = math.radians(elevation)

        pos_x = round(distance * math.cos(rad_el) * math.sin(rad_az), 2)
        pos_y = round(-distance * math.cos(rad_el) * math.cos(rad_az), 2)
        pos_z = round(target_z + distance * math.sin(rad_el), 2)

        return CameraConfiguration(
            projection=ProjectionType.PERSPECTIVE,
            focal_length=focal,
            sensor_width=sensor_w,
            field_of_view=fov,
            distance=distance,
            position=(pos_x, pos_y, pos_z),
            rotation=(60.0, 0.0, azimuth),
            target_position=(0.0, 0.0, target_z),
            confidence=0.95,
            inference_level=InferenceConfidenceLevel.KNOWN
        )
