from typing import Dict, Any, List, Optional, Tuple
from ..generators.base_generator import GeneratedGeometry

class GeometryValidator:
    @staticmethod
    def validate_geometry(geo: GeneratedGeometry) -> Tuple[bool, List[str]]:
        errors = []
        if not geo.vertices or len(geo.vertices) == 0:
            errors.append("Geometry has zero vertices.")
        if not geo.faces or len(geo.faces) == 0:
            errors.append("Geometry has zero faces.")
        if geo.triangle_count <= 0:
            errors.append("Geometry has invalid triangle count (<=0).")

        return len(errors) == 0, errors
