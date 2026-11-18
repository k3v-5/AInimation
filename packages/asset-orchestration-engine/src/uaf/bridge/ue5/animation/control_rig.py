"""Control Rig effector and IK bone manipulation bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple


@dataclass
class RigControlValue:
    control_name: str
    control_type: str = "Transform"  # Transform, Float, Vector, Bool
    value: Any = None
    location: Optional[Tuple[float, float, float]] = None
    rotation: Optional[Tuple[float, float, float]] = None
    scale: Optional[Tuple[float, float, float]] = None

    def __post_init__(self) -> None:
        if self.location is not None and self.value is None:
            self.value = {"location": list(self.location), "rotation": list(self.rotation or (0, 0, 0))}


@dataclass
class ControlRigBridgePayload:
    rig_id: str
    target_actor_id: str = ""
    rig_asset_path: Optional[str] = None
    controls: Union[List[RigControlValue], Dict[str, RigControlValue]] = field(default_factory=list)
    is_evaluating: bool = True

    def to_dict(self) -> Dict[str, Any]:
        ctrl_list = list(self.controls.values()) if isinstance(self.controls, dict) else self.controls
        return {
            "rig_id": self.rig_id,
            "target_actor_id": self.target_actor_id,
            "rig_asset_path": self.rig_asset_path,
            "controls": [{"name": c.control_name, "type": c.control_type, "value": c.value} for c in ctrl_list],
            "is_evaluating": self.is_evaluating,
        }
