"""Animation Sequence and blend space bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AnimNotifyEvent:
    name: str = ""
    trigger_time_s: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)
    notify_name: Optional[str] = None
    trigger_time_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if self.notify_name is not None:
            self.name = self.notify_name
        else:
            self.notify_name = self.name

        if self.trigger_time_seconds is not None:
            self.trigger_time_s = self.trigger_time_seconds
        else:
            self.trigger_time_seconds = self.trigger_time_s


@dataclass
class AnimationBridgePayload:
    asset_id: str = ""
    semantic_name: str = ""
    skeleton_asset_id: str = ""
    duration_s: float = 0.0
    fps: float = 30.0
    enable_root_motion: bool = False
    notifies: List[AnimNotifyEvent] = field(default_factory=list)
    curve_names: List[str] = field(default_factory=list)
    animation_id: Optional[str] = None
    sequence_name: Optional[str] = None
    duration_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if self.animation_id is not None:
            self.asset_id = self.animation_id
        else:
            self.animation_id = self.asset_id

        if self.sequence_name is not None:
            self.semantic_name = self.sequence_name
        else:
            self.sequence_name = self.semantic_name

        if self.duration_seconds is not None:
            self.duration_s = self.duration_seconds
        else:
            self.duration_seconds = self.duration_s

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "animation_id": self.animation_id,
            "semantic_name": self.semantic_name,
            "sequence_name": self.sequence_name,
            "skeleton_asset_id": self.skeleton_asset_id,
            "duration_s": self.duration_s,
            "duration_seconds": self.duration_s,
            "fps": self.fps,
            "enable_root_motion": self.enable_root_motion,
            "notifies": [{"name": n.name, "time": n.trigger_time_s, "payload": n.payload} for n in self.notifies],
            "curve_names": self.curve_names,
        }
