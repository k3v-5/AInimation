import math
import uuid
from typing import Dict, Any, Optional, Tuple, List
from .base_generator import IGeometryGenerator, GeneratedGeometry
from ..parameters.parameter_constraints import ParameterConstraints

class PrimitiveGenerator(IGeometryGenerator):
    def __init__(self):
        super().__init__(name="primitive", version="1.0")

    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        prim_type = parameters.get("primitive", parameters.get("type", "box")).lower()
        if prim_type not in ["box", "cube", "cylinder", "sphere", "cone", "plane"]:
            return False, f"INVALID_PARAMETER: Unsupported primitive type '{prim_type}'."

        w = float(parameters.get("width", 1.0))
        d = float(parameters.get("depth", 1.0))
        h = float(parameters.get("height", 1.0))

        if w <= 0 or d <= 0 or h <= 0:
            return False, f"INVALID_PARAMETER: Primitive dimensions must be positive (>0), got w={w}, d={d}, h={h}."

        return True, None

    def build(self, component_id: str, parameters: Dict[str, Any], context: Optional[Any] = None) -> GeneratedGeometry:
        prim_type = parameters.get("primitive", parameters.get("type", "box")).lower()
        w = float(parameters.get("width", 1.0))
        d = float(parameters.get("depth", 1.0))
        h = float(parameters.get("height", 1.0))

        geo_id = f"geo_{uuid.uuid4().hex[:8]}"

        if prim_type in ["box", "cube"]:
            # Generar cubo centrado
            hw, hd, hh = w / 2.0, d / 2.0, h / 2.0
            vertices = [
                (-hw, -hd, -hh), (hw, -hd, -hh), (hw, hd, -hh), (-hw, hd, -hh),
                (-hw, -hd, hh), (hw, -hd, hh), (hw, hd, hh), (-hw, hd, hh)
            ]
            faces = [
                [0, 1, 2, 3], [4, 5, 6, 7], # Bottom, Top
                [0, 1, 5, 4], [2, 3, 7, 6], # Front, Back
                [0, 3, 7, 4], [1, 2, 6, 5]  # Left, Right
            ]
            tri_count = 12

        elif prim_type == "cylinder":
            radius = w / 2.0
            segments = int(parameters.get("segments", 16))
            vertices = []
            hh = h / 2.0
            # Bottom ring
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments
                vertices.append((radius * math.cos(theta), radius * math.sin(theta), -hh))
            # Top ring
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments
                vertices.append((radius * math.cos(theta), radius * math.sin(theta), hh))

            faces = []
            for i in range(segments):
                nxt = (i + 1) % segments
                faces.append([i, nxt, segments + nxt, segments + i])
            # Caps
            faces.append(list(range(segments)))
            faces.append(list(range(segments, 2 * segments)))
            tri_count = segments * 2 + (segments - 2) * 2

        elif prim_type == "cone":
            radius = w / 2.0
            segments = int(parameters.get("segments", 16))
            hh = h / 2.0
            vertices = [(0.0, 0.0, hh)] # Tip
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments
                vertices.append((radius * math.cos(theta), radius * math.sin(theta), -hh))
            faces = []
            for i in range(segments):
                nxt = 1 + ((i + 1) % segments)
                faces.append([0, 1 + i, nxt])
            faces.append(list(range(1, segments + 1)))
            tri_count = segments * 2

        else: # Default box fallback
            hw, hd, hh = w / 2.0, d / 2.0, h / 2.0
            vertices = [(-hw, -hd, -hh), (hw, -hd, -hh), (hw, hd, -hh), (-hw, hd, -hh),
                        (-hw, -hd, hh), (hw, -hd, hh), (hw, hd, hh), (-hw, hd, hh)]
            faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]]
            tri_count = 12

        return GeneratedGeometry(
            geometry_id=geo_id,
            component_id=component_id,
            vertices=vertices,
            faces=faces,
            triangle_count=tri_count,
            bounding_box_min=(-w/2, -d/2, -h/2),
            bounding_box_max=(w/2, d/2, h/2),
            dimensions=(w, d, h),
            metadata={"primitive": prim_type, "generator": self.name}
        )
