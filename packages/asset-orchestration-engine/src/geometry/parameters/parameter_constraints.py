from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import math

class ParameterConstraints:
    @staticmethod
    def validate_positive_dimension(name: str, val: float) -> Tuple[bool, Optional[str]]:
        if val <= 0:
            return False, f"INVALID_PARAMETER: Parameter '{name}' must be strictly positive (>0), got {val}."
        return True, None

    @staticmethod
    def validate_range(name: str, val: float, min_val: float, max_val: float) -> Tuple[bool, Optional[str]]:
        if val < min_val or val > max_val:
            return False, f"PARAMETER_OUT_OF_RANGE: Parameter '{name}' ({val}) is out of range [{min_val}, {max_val}]."
        return True, None
