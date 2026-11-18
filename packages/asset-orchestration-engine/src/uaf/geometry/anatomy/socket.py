"""
AttachmentSocket defines precise anchor points for props, armor, accessories, and weapons.
UAF-81.3 Sections 37, 38.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AttachmentSocket:
    socket_id: str
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    allowed_categories: List[str] = field(default_factory=list)
    clearance_meters: float = 0.02
    scale_policy: str = "inherit"  # "inherit", "fixed", "proportional"

    def can_attach(self, category: str) -> bool:
        if not self.allowed_categories:
            return True
        return category in self.allowed_categories

    def to_dict(self) -> Dict[str, Any]:
        return {
            "socket_id": self.socket_id,
            "position": self.position,
            "rotation": self.rotation,
            "allowed_categories": self.allowed_categories,
            "clearance_meters": self.clearance_meters,
            "scale_policy": self.scale_policy,
        }
