"""
ConnectorDefinition and ConnectorType models for modular snapping.
UAF-81.6 Sections 10, 11, 12, 13.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class ConnectorType(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    DOOR = "DOOR"
    STAIR = "STAIR"
    CORRIDOR = "CORRIDOR"
    PIPE = "PIPE"
    BRIDGE = "BRIDGE"
    CUSTOM = "CUSTOM"


@dataclass
class ConnectorDefinition:
    connector_id: str
    connector_type: ConnectorType
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # Relative to module origin
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])  # Euler degrees
    size: List[float] = field(default_factory=lambda: [2.0, 3.0])           # Width, Height in meters
    compatibility_tags: List[str] = field(default_factory=list)

    def is_compatible_with(self, other: "ConnectorDefinition") -> bool:
        if self.connector_type != other.connector_type:
            return False
        # If either declares tags, there must be an intersection
        if self.compatibility_tags and other.compatibility_tags:
            return bool(set(self.compatibility_tags) & set(other.compatibility_tags))
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connector_id": self.connector_id,
            "connector_type": self.connector_type.value,
            "position": self.position,
            "rotation": self.rotation,
            "size": self.size,
            "compatibility_tags": self.compatibility_tags,
        }
