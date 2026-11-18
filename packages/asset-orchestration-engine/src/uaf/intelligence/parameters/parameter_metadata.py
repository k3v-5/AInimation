"""
ParameterMetadata describes typed parameter constraints, defaults, and provenance.
UAF-81.1 Section 17.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from .parameter_type import ParameterType, ParameterProvenance


@dataclass(frozen=True)
class ParameterMetadata:
    name: str
    param_type: ParameterType
    default: Any = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    unit: Optional[str] = None
    description: str = ""
    required: bool = False
    exposed: bool = True
    provenance: ParameterProvenance = ParameterProvenance.USER_DEFINED
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "param_type": self.param_type.value,
            "default": self.default,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "unit": self.unit,
            "description": self.description,
            "required": self.required,
            "exposed": self.exposed,
            "provenance": self.provenance.value,
            "confidence": self.confidence,
        }
