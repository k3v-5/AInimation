"""
Keyframe, AnimationTrack, AnimationEvent, and AnimationClip models.
UAF-81.9 Sections 60, 61, 62, 70, 129, 130.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class AnimationEventType(str, Enum):
    FOOTSTEP = "FOOTSTEP"
    ATTACK = "ATTACK"
    IMPACT = "IMPACT"
    RELOAD = "RELOAD"
    WEAPON_FIRE = "WEAPON_FIRE"
    DEATH = "DEATH"
    INTERACTION = "INTERACTION"


@dataclass
class Keyframe:
    time_seconds: float
    translation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])  # Quaternion
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_seconds": round(self.time_seconds, 4),
            "translation": self.translation,
            "rotation": self.rotation,
            "scale": self.scale,
        }


@dataclass
class AnimationTrack:
    bone_name: str
    keyframes: List[Keyframe] = field(default_factory=list)

    def add_keyframe(self, keyframe: Keyframe) -> None:
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.time_seconds)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone_name": self.bone_name,
            "keyframes": [k.to_dict() for k in self.keyframes],
        }


@dataclass
class AnimationEvent:
    event_id: str
    event_type: AnimationEventType
    trigger_time_seconds: float
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "trigger_time_seconds": round(self.trigger_time_seconds, 4),
            "payload": self.payload,
        }


@dataclass
class AnimationClip:
    clip_id: str
    duration_seconds: float = 1.0
    frame_rate: float = 30.0
    is_looping: bool = True
    tracks: Dict[str, AnimationTrack] = field(default_factory=dict)
    events: List[AnimationEvent] = field(default_factory=list)
    version: str = "1.0.0"

    def add_track(self, track: AnimationTrack) -> None:
        self.tracks[track.bone_name] = track

    def add_event(self, event: AnimationEvent) -> None:
        self.events.append(event)
        self.events.sort(key=lambda e: e.trigger_time_seconds)

    @property
    def clip_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "duration_seconds": self.duration_seconds,
            "frame_rate": self.frame_rate,
            "is_looping": self.is_looping,
            "tracks": {k: v.to_dict() for k, v in sorted(self.tracks.items())},
            "events": [e.to_dict() for e in self.events],
            "version": self.version,
        }

    @classmethod
    def create_idle_clip(cls, clip_id: str = "A_Hero_Idle") -> "AnimationClip":
        clip = cls(clip_id=clip_id, duration_seconds=2.0, is_looping=True)
        # Root track
        root_track = AnimationTrack(bone_name="root")
        root_track.add_keyframe(Keyframe(0.0, [0.0, 0.0, 0.0]))
        root_track.add_keyframe(Keyframe(1.0, [0.0, 0.0, 0.01]))
        root_track.add_keyframe(Keyframe(2.0, [0.0, 0.0, 0.0]))
        clip.add_track(root_track)
        return clip

    @classmethod
    def create_walk_clip(cls, clip_id: str = "A_Hero_Walk") -> "AnimationClip":
        clip = cls(clip_id=clip_id, duration_seconds=1.0, is_looping=True)
        # Add footstep events
        clip.add_event(AnimationEvent("evt_step_L", AnimationEventType.FOOTSTEP, 0.25, {"foot": "foot_L"}))
        clip.add_event(AnimationEvent("evt_step_R", AnimationEventType.FOOTSTEP, 0.75, {"foot": "foot_R"}))
        return clip
