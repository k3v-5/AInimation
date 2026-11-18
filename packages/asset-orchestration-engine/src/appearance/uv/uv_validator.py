import math
from typing import Tuple, Optional, List
from .uv_schema import UVSet

class UVValidator:
    @staticmethod
    def validate_uv_set(uv_set: UVSet) -> Tuple[bool, Optional[str]]:
        if not uv_set.coordinates or len(uv_set.coordinates) == 0:
            return False, "UV_VALIDATION_FAILED: UV coordinates list is empty."

        for idx, (u, v) in enumerate(uv_set.coordinates):
            if math.isnan(u) or math.isnan(v) or math.isinf(u) or math.isinf(v):
                return False, f"UV_VALIDATION_FAILED: Invalid NaN or Inf coordinate at index {idx}: ({u}, {v})."

        return True, None
