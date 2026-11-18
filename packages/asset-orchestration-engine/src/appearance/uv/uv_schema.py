from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any

class UVMethod(str, Enum):
    BOX = "BOX"
    PLANAR = "PLANAR"
    CYLINDRICAL = "CYLINDRICAL"
    SPHERICAL = "SPHERICAL"
    SMART = "SMART"

@dataclass
class UVSet:
    uv_set_id: str
    component_id: str
    channel: str = "UV0" # UV0 (surface), UV1 (lightmap)
    method: UVMethod = UVMethod.BOX
    coordinates: List[Tuple[float, float]] = field(default_factory=list) # U, V coords por vertice/loop
    version: int = 1
