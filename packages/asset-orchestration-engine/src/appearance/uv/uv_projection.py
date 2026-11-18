import math
import uuid
from typing import List, Tuple, Dict, Any, Optional
from .uv_schema import UVSet, UVMethod
from ...geometry.generators.base_generator import GeneratedGeometry

class UVProjection:
    @staticmethod
    def generate_uv_set(
        component_id: str,
        geometry: GeneratedGeometry,
        method: UVMethod = UVMethod.BOX,
        channel: str = "UV0"
    ) -> UVSet:
        uv_coords: List[Tuple[float, float]] = []

        if not geometry or not geometry.vertices:
            return UVSet(uv_set_id=f"uv_{uuid.uuid4().hex[:6]}", component_id=component_id, channel=channel, method=method, coordinates=[])

        w, d, h = geometry.dimensions
        max_dim = max(w, d, h, 0.001)

        for vx, vy, vz in geometry.vertices:
            if method == UVMethod.PLANAR:
                u = round((vx + (w / 2.0)) / max(w, 0.001), 4)
                v = round((vz + (h / 2.0)) / max(h, 0.001), 4)
            elif method == UVMethod.CYLINDRICAL:
                theta = math.atan2(vy, vx)
                u = round((theta + math.pi) / (2.0 * math.pi), 4)
                v = round((vz + (h / 2.0)) / max(h, 0.001), 4)
            else: # BOX / SMART fallback
                u = round((vx + (max_dim / 2.0)) / max_dim, 4)
                v = round((vz + (max_dim / 2.0)) / max_dim, 4)

            uv_coords.append((u, v))

        return UVSet(
            uv_set_id=f"uv_{uuid.uuid4().hex[:6]}",
            component_id=component_id,
            channel=channel,
            method=method,
            coordinates=uv_coords,
            version=1
        )
