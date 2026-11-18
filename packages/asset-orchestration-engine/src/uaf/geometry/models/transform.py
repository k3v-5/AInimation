"""
Transform3D contract for unambiguous component positioning and parenting.
UAF-81.3 Sections 14, 15, 16.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Transform3D:
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # Euler angles in degrees
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    pivot: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    parent_id: Optional[str] = None
    up_axis: str = "Z"
    forward_axis: str = "Y"
    unit_scale: float = 1.0  # 1.0 = meters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "pivot": self.pivot,
            "parent_id": self.parent_id,
            "up_axis": self.up_axis,
            "forward_axis": self.forward_axis,
            "unit_scale": self.unit_scale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transform3D":
        return cls(
            position=data.get("position", [0.0, 0.0, 0.0]),
            rotation=data.get("rotation", [0.0, 0.0, 0.0]),
            scale=data.get("scale", [1.0, 1.0, 1.0]),
            pivot=data.get("pivot", [0.0, 0.0, 0.0]),
            parent_id=data.get("parent_id"),
            up_axis=data.get("up_axis", "Z"),
            forward_axis=data.get("forward_axis", "Y"),
            unit_scale=float(data.get("unit_scale", 1.0)),
        )
