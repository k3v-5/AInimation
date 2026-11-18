"""
RuntimeSocketDefinition and SocketType models for gameplay attachments.
UAF-81.8 Sections 17, 18, 19.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class SocketType(str, Enum):
    WEAPON = "WEAPON"
    MUZZLE = "MUZZLE"
    GRIP = "GRIP"
    MAGAZINE = "MAGAZINE"
    HAND = "HAND"
    HEAD = "HEAD"
    BACK = "BACK"
    SHOULDER = "SHOULDER"
    ROOT = "ROOT"
    CUSTOM = "CUSTOM"


@dataclass
class RuntimeSocketDefinition:
    socket_id: str
    parent_attachment: str  # bone name or component name
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    socket_type: SocketType = SocketType.CUSTOM

    def to_dict(self) -> Dict[str, Any]:
        return {
            "socket_id": self.socket_id,
            "parent_attachment": self.parent_attachment,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "socket_type": self.socket_type.value,
        }
