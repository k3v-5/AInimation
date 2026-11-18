from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from ..capture.camera_manager import ViewOrientation

class ReferenceType(str, Enum):
    SPECIFICATION_ONLY = "specification_only"
    IMAGE = "image"
    MULTIPLE_IMAGES = "multiple_images"

@dataclass
class ReferenceView:
    orientation: ViewOrientation
    weight: float = 1.0
    expected_aspect_ratio: Optional[float] = None
    expected_components: List[str] = field(default_factory=list)
    grid_occupancy: Optional[List[List[int]]] = None

@dataclass
class VisualReference:
    reference_id: str
    ref_type: ReferenceType = ReferenceType.SPECIFICATION_ONLY
    views: Dict[ViewOrientation, ReferenceView] = field(default_factory=dict)
    expected_dimensions: Dict[str, Dict[str, float]] = field(default_factory=dict) # comp_id -> {width, height, depth}
    expected_structure: List[str] = field(default_factory=list) # lista de componentes obligatorios
    style_metadata: Dict[str, Any] = field(default_factory=dict)
