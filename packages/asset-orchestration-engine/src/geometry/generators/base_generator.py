from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class GeneratedGeometry:
    geometry_id: str
    component_id: str
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    faces: List[List[int]] = field(default_factory=list)
    normals: List[Tuple[float, float, float]] = field(default_factory=list)
    triangle_count: int = 0
    bounding_box_min: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounding_box_max: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    dimensions: Tuple[float, float, float] = (0.0, 0.0, 0.0) # (w, d, h)
    metadata: Dict[str, Any] = field(default_factory=dict)

class IGeometryGenerator(ABC):
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version

    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        pass

    @abstractmethod
    def build(self, component_id: str, parameters: Dict[str, Any], context: Optional[Any] = None) -> GeneratedGeometry:
        pass
