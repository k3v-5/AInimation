import math
import uuid
from typing import Dict, Any, Optional, Tuple, List
from .base_generator import IGeometryGenerator, GeneratedGeometry

class ProfileGenerator(IGeometryGenerator):
    """
    Generador de geometría extruida a partir de perfiles 2D con biselado (bevel) y ahusamiento (tip_ratio).
    Ideal para hojas de espadas, paneles, escudos y placas metálicas.
    """
    def __init__(self):
        super().__init__(name="profile", version="1.0")

    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        l = float(parameters.get("length", parameters.get("height", 0.85)))
        w = float(parameters.get("width", 0.05))
        t = float(parameters.get("thickness", parameters.get("depth", 0.015)))

        if l <= 0 or w <= 0 or t <= 0:
            return False, f"INVALID_PARAMETER: Profile dimensions must be positive (>0), got length={l}, width={w}, thickness={t}."

        tip_ratio = float(parameters.get("tip_ratio", 0.15))
        if tip_ratio < 0.0 or tip_ratio > 1.0:
            return False, f"PARAMETER_OUT_OF_RANGE: tip_ratio must be in [0.0, 1.0], got {tip_ratio}."

        return True, None

    def build(self, component_id: str, parameters: Dict[str, Any], context: Optional[Any] = None) -> GeneratedGeometry:
        l = float(parameters.get("length", parameters.get("height", 0.85)))
        w = float(parameters.get("width", 0.05))
        t = float(parameters.get("thickness", parameters.get("depth", 0.015)))
        tip_ratio = float(parameters.get("tip_ratio", 0.15))

        geo_id = f"geo_prof_{uuid.uuid4().hex[:8]}"

        hw = w / 2.0
        ht = t / 2.0
        # Base section (Z = -l/2)
        v0 = (-hw, 0.0, -l / 2)
        v1 = (0.0, -ht, -l / 2)
        v2 = (hw, 0.0, -l / 2)
        v3 = (0.0, ht, -l / 2)

        # Mid section before tip (Z = l/2 - l*tip_ratio)
        z_mid = l / 2 - (l * tip_ratio)
        v4 = (-hw, 0.0, z_mid)
        v5 = (0.0, -ht, z_mid)
        v6 = (hw, 0.0, z_mid)
        v7 = (0.0, ht, z_mid)

        # Tip point (Z = l/2)
        v8 = (0.0, 0.0, l / 2)

        vertices = [v0, v1, v2, v3, v4, v5, v6, v7, v8]

        # Faces
        faces = [
            # Base cap
            [0, 1, 2, 3],
            # Lower body sides
            [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],
            # Tip faces
            [4, 5, 8], [5, 6, 8], [6, 7, 8], [7, 4, 8]
        ]
        tri_count = 2 + 8 + 4

        return GeneratedGeometry(
            geometry_id=geo_id,
            component_id=component_id,
            vertices=vertices,
            faces=faces,
            triangle_count=tri_count,
            bounding_box_min=(-hw, -ht, -l/2),
            bounding_box_max=(hw, ht, l/2),
            dimensions=(w, t, l),
            metadata={"generator": self.name, "tip_ratio": tip_ratio}
        )
