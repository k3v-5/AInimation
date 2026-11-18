from typing import Dict, Any
from ..core.reference_types import CameraPerspective
from ..core.reference_schema import CameraEstimation

class CameraViewEstimator:
    @classmethod
    def estimate_camera(cls, image_metadata: Dict[str, Any]) -> CameraEstimation:
        view_str = image_metadata.get("camera_view", "ISOMETRIC_THREE_QUARTERS").upper()
        view = getattr(CameraPerspective, view_str, CameraPerspective.ISOMETRIC_THREE_QUARTERS)
        elev = float(image_metadata.get("elevation_deg", 25.0))
        azim = float(image_metadata.get("azimuth_deg", 45.0))
        fov = float(image_metadata.get("fov", 50.0))

        return CameraEstimation(
            estimated_view=view,
            elevation_deg=elev,
            azimuth_deg=azim,
            field_of_view=fov
        )
