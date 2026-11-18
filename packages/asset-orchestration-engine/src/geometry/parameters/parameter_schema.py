from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List, Union

class ParameterType(str, Enum):
    FLOAT = "float"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING = "string"
    VECTOR2 = "vector2"
    VECTOR3 = "vector3"
    EXPRESSION = "expression"

@dataclass
class ParameterSpec:
    name: str
    param_type: ParameterType = ParameterType.FLOAT
    required: bool = False
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str = "meters"
    description: str = ""

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        if value is None:
            if self.required:
                return False, f"Missing required parameter '{self.name}'"
            return True, None

        if self.param_type == ParameterType.FLOAT:
            if not isinstance(value, (int, float)):
                return False, f"Parameter '{self.name}' must be a float, got {type(value).__name__}"
            if self.min_value is not None and value < self.min_value:
                return False, f"Parameter '{self.name}' ({value}) is below minimum allowed ({self.min_value})"
            if self.max_value is not None and value > self.max_value:
                return False, f"Parameter '{self.name}' ({value}) exceeds maximum allowed ({self.max_value})"

        elif self.param_type == ParameterType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                return False, f"Parameter '{self.name}' must be an integer, got {type(value).__name__}"
            if self.min_value is not None and value < self.min_value:
                return False, f"Parameter '{self.name}' ({value}) is below minimum allowed ({self.min_value})"
            if self.max_value is not None and value > self.max_value:
                return False, f"Parameter '{self.name}' ({value}) exceeds maximum allowed ({self.max_value})"

        elif self.param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"Parameter '{self.name}' must be a boolean, got {type(value).__name__}"

        elif self.param_type in [ParameterType.VECTOR2, ParameterType.VECTOR3]:
            expected_len = 2 if self.param_type == ParameterType.VECTOR2 else 3
            if not isinstance(value, (tuple, list)) or len(value) != expected_len:
                return False, f"Parameter '{self.name}' must be a {self.param_type.value} of length {expected_len}"

        return True, None
