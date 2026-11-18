import math
from typing import Tuple, List
from ..generators.base_generator import GeneratedGeometry

class DimensionValidator:
    @staticmethod
    def validate_dimensions(
        geo: GeneratedGeometry,
        expected_w: float,
        expected_d: float,
        expected_h: float,
        tolerance: float = 0.005
    ) -> Tuple[bool, List[str]]:
        errors = []
        actual_w, actual_d, actual_h = geo.dimensions

        if not math.isclose(actual_w, expected_w, abs_tol=tolerance):
            errors.append(f"Width mismatch: expected {expected_w}m, got {actual_w}m (tol={tolerance})")
        if not math.isclose(actual_d, expected_d, abs_tol=tolerance):
            errors.append(f"Depth mismatch: expected {expected_d}m, got {actual_d}m (tol={tolerance})")
        if not math.isclose(actual_h, expected_h, abs_tol=tolerance):
            errors.append(f"Height mismatch: expected {expected_h}m, got {actual_h}m (tol={tolerance})")

        return len(errors) == 0, errors
