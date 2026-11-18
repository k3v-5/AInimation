"""Cinematic Sequencer track and keyframe animation bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SequencerKeyframe:
    time_s: float = 0.0
    value: Any = None
    interpolation: str = "Linear"  # Linear, Constant, Cubic
    frame: Optional[int] = None

    def __post_init__(self) -> None:
        if self.frame is not None and self.time_s == 0.0:
            self.time_s = self.frame / 30.0


@dataclass
class SequencerTrackPayload:
    track_name: str
    target_object_id: str
    track_type: str = "Generic"  # Transform, FOV, Visibility, Animation, Audio, VFX
    keyframes: List[SequencerKeyframe] = field(default_factory=list)


@dataclass
class SequencerBridgePayload:
    sequence_id: str
    sequence_name: str = ""
    duration_s: float = 0.0
    fps: float = 24.0
    tracks: List[SequencerTrackPayload] = field(default_factory=list)
    duration_frames: Optional[int] = None
    sequence_asset_path: Optional[str] = None

    def __post_init__(self) -> None:
        if self.duration_frames is not None and self.duration_s == 0.0:
            self.duration_s = self.duration_frames / self.fps
        if self.sequence_asset_path is not None and not self.sequence_name:
            self.sequence_name = self.sequence_asset_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sequence_id": self.sequence_id,
            "sequence_name": self.sequence_name,
            "sequence_asset_path": self.sequence_asset_path,
            "duration_s": self.duration_s,
            "duration_frames": self.duration_frames,
            "fps": self.fps,
            "tracks": [
                {
                    "name": t.track_name,
                    "type": t.track_type,
                    "target_object_id": t.target_object_id,
                    "keyframes": [
                        {"time": k.time_s, "value": k.value, "interpolation": k.interpolation, "frame": k.frame}
                        for k in t.keyframes
                    ],
                }
                for t in self.tracks
            ],
        }
