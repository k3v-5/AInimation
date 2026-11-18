"""Component bridge for translating ECS components into UActorComponent equivalents."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ComponentBridgePayload:
    component_name: str
    component_type: str  # StaticMeshComponent, PointLightComponent, etc.
    relative_transform: Dict[str, Any] = field(default_factory=lambda: {
        "location": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    })
    properties: Dict[str, Any] = field(default_factory=dict)
    is_root: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "component_type": self.component_type,
            "relative_transform": self.relative_transform,
            "properties": self.properties,
            "is_root": self.is_root,
        }
