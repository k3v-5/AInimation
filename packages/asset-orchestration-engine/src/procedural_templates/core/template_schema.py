from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class ParameterType(str, Enum):
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    RATIO = "RATIO"
    DISTANCE = "DISTANCE"
    COLOR = "COLOR"

@dataclass
class ParameterDefinition:
    name: str
    param_type: ParameterType
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str = "meters"
    required: bool = True
    description: str = ""

@dataclass
class ComponentDefinition:
    component_id: str
    semantic_role: str
    required: bool = True
    dependencies: List[str] = field(default_factory=list)
