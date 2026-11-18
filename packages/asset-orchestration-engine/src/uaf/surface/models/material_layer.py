"""
Material layers, blending modes, and first-class mask models.
UAF-81.4 Sections 8, 9, 10, 11, 12, 13.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class MaskType(str, Enum):
    MATERIAL = "MATERIAL"
    WEAR = "WEAR"
    DIRT = "DIRT"
    DAMAGE = "DAMAGE"
    EDGE = "EDGE"
    REGION = "REGION"
    PAINT = "PAINT"
    SELECTION = "SELECTION"


class MaskSource(str, Enum):
    GEOMETRY = "GEOMETRY"
    CURVATURE = "CURVATURE"
    AO = "AO"
    NORMAL = "NORMAL"
    VERTEX_COLOR = "VERTEX_COLOR"
    PROCEDURAL_NOISE = "PROCEDURAL_NOISE"
    SEMANTIC = "SEMANTIC"


class BlendMode(str, Enum):
    OVERLAY = "OVERLAY"
    MULTIPLY = "MULTIPLY"
    ADD = "ADD"
    LERP = "LERP"
    ALPHA_BLEND = "ALPHA_BLEND"


@dataclass
class SurfaceMask:
    mask_id: str
    mask_type: MaskType
    source: MaskSource
    parameters: Dict[str, Any] = field(default_factory=dict)
    resolution: int = 2048

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mask_id": self.mask_id,
            "mask_type": self.mask_type.value,
            "source": self.source.value,
            "parameters": self.parameters,
            "resolution": self.resolution,
        }


@dataclass
class MaterialLayer:
    layer_id: str
    priority: int  # Ordering in stack (0 = base, higher = top)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    mask: Optional[SurfaceMask] = None
    blend_mode: BlendMode = BlendMode.LERP
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "priority": self.priority,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "mask": self.mask.to_dict() if self.mask else None,
            "blend_mode": self.blend_mode.value,
            "parameters": self.parameters,
        }
