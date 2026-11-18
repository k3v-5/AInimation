"""Actor lifecycle, transforms, and ECS representation bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ActorBridgePayload:
    uaf_object_id: str
    actor_class: str = "Actor"
    actor_name: str = ""
    transform: Dict[str, Any] = field(default_factory=lambda: {
        "location": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],  # Roll, Pitch, Yaw
        "scale": [1.0, 1.0, 1.0],
    })
    mobility: str = "Movable"  # Static, Stationary, Movable
    components: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    owner: str = "UAF"
    revision: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uaf_object_id": self.uaf_object_id,
            "actor_class": self.actor_class,
            "actor_name": self.actor_name,
            "transform": self.transform,
            "mobility": self.mobility,
            "components": self.components,
            "tags": self.tags,
            "owner": self.owner,
            "revision": self.revision,
        }
