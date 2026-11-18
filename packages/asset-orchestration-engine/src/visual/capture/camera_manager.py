from enum import Enum
from dataclasses import dataclass
from typing import Tuple

class ViewOrientation(str, Enum):
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

@dataclass
class CameraConfig:
    orientation: ViewOrientation = ViewOrientation.FRONT
    projection: str = "orthographic" # orthographic / perspective
    position: Tuple[float, float, float] = (0.0, -2.5, 0.0)
    target: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    ortho_scale: float = 2.0
    resolution: Tuple[int, int] = (512, 512)
