"""
Area Lights Implementation (Rect, Disk, Line) for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .core import LightType, ensure_finite_scalar
from .lights import Light


@dataclass
class RectAreaLight(Light):
    """
    Rectangular area light source (e.g. windows, LED panels, studio lightboxes).
    """
    source_width: float = 1.0           # Width in meters
    source_height: float = 1.0          # Height in meters
    barn_door_angle: float = 88.0       # Angle in degrees
    barn_door_length: float = 0.2       # Length in meters

    def __post_init__(self) -> None:
        self.light_type = LightType.RECT_AREA
        super().__post_init__()
        self.source_width = max(0.01, ensure_finite_scalar(self.source_width, "source_width", 1.0))
        self.source_height = max(0.01, ensure_finite_scalar(self.source_height, "source_height", 1.0))
        self.barn_door_angle = max(0.0, min(89.0, ensure_finite_scalar(self.barn_door_angle, "barn_door_angle", 88.0)))
        self.barn_door_length = max(0.0, ensure_finite_scalar(self.barn_door_length, "barn_door_length", 0.2))

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "source_width": self.source_width,
            "source_height": self.source_height,
            "barn_door_angle": self.barn_door_angle,
            "barn_door_length": self.barn_door_length,
        })
        return d


@dataclass
class DiskAreaLight(Light):
    """
    Circular disk area light source.
    """
    source_radius: float = 0.5          # Radius in meters

    def __post_init__(self) -> None:
        self.light_type = LightType.DISK_AREA
        super().__post_init__()
        self.source_radius = max(0.01, ensure_finite_scalar(self.source_radius, "source_radius", 0.5))

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "source_radius": self.source_radius,
        })
        return d


@dataclass
class LineAreaLight(Light):
    """
    Linear tube or filament light source.
    """
    source_length: float = 1.0          # Length in meters

    def __post_init__(self) -> None:
        self.light_type = LightType.LINE_AREA
        super().__post_init__()
        self.source_length = max(0.01, ensure_finite_scalar(self.source_length, "source_length", 1.0))

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "source_length": self.source_length,
        })
        return d
