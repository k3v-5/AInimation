"""
Universal Animation, Motion, Retargeting & Character Runtime System Domain Models.
UAF-81.55 Sections 1-132, 174.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from ...core.hashing.canonical_hasher import CanonicalHasher


# --- ENUMS ---

class AnimationType55(str, Enum):
    IDLE = "IDLE"
    WALK = "WALK"
    RUN = "RUN"
    SPRINT = "SPRINT"
    JUMP = "JUMP"
    FALL = "FALL"
    LAND = "LAND"
    TURN = "TURN"
    STRAFE = "STRAFE"
    CROUCH = "CROUCH"
    AIM = "AIM"
    ATTACK = "ATTACK"
    DAMAGE = "DAMAGE"
    DEATH = "DEATH"
    INTERACTION = "INTERACTION"
    CUSTOM = "CUSTOM"


class ChannelType55(str, Enum):
    TRANSLATION = "TRANSLATION"
    ROTATION = "ROTATION"
    SCALE = "SCALE"


class CurveInterpolation55(str, Enum):
    LINEAR = "LINEAR"
    STEP = "STEP"
    CUBIC = "CUBIC"
    HERMITE = "HERMITE"
    BEZIER = "BEZIER"


class MarkerType55(str, Enum):
    SYNC = "SYNC"
    NOTIFY = "NOTIFY"
    AUDIO = "AUDIO"
    VFX = "VFX"
    HIT = "HIT"
    FOOTSTEP = "FOOTSTEP"
    CUSTOM = "CUSTOM"


class ResamplingMode55(str, Enum):
    NEAREST = "NEAREST"
    LINEAR = "LINEAR"
    CUBIC = "CUBIC"
    HERMITE = "HERMITE"


class BlendType55(str, Enum):
    LINEAR = "LINEAR"
    HERMITE = "HERMITE"
    INERTIAL = "INERTIAL"
    SPHERICAL = "SPHERICAL"


class LayerType55(str, Enum):
    OVERRIDE = "OVERRIDE"
    ADDITIVE = "ADDITIVE"
    MASKED = "MASKED"
    POSTURE = "POSTURE"


class LocomotionMode55(str, Enum):
    IN_PLACE = "IN_PLACE"
    ROOT_MOTION = "ROOT_MOTION"
    PROCEDURAL = "PROCEDURAL"
    HYBRID = "HYBRID"


class RootMotionMode55(str, Enum):
    EXTRACT = "EXTRACT"
    LOCK_XZ = "LOCK_XZ"
    FULL = "FULL"
    NONE = "NONE"


class CompressionMethod55(str, Enum):
    KEYFRAME_REDUCTION = "KEYFRAME_REDUCTION"
    ACL = "ACL"
    BITPACKING = "BITPACKING"
    LINEAR_TOLERANCE = "LINEAR_TOLERANCE"
    CUSTOM = "CUSTOM"


# --- DATACLASSES ---

@dataclass
class Keyframe55:
    time_sec: float
    value: Tuple[float, ...]  # 3 floats for pos/scale, 4 for quat rot, or 1 for scalar

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_sec": self.time_sec,
            "value": list(self.value),
        }


@dataclass
class AnimationTrack:
    bone_name: str
    channel: ChannelType55
    keyframes: List[Keyframe55] = field(default_factory=list)
    interpolation: CurveInterpolation55 = CurveInterpolation55.LINEAR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone_name": self.bone_name,
            "channel": self.channel.value,
            "keyframe_count": len(self.keyframes),
            "keyframes": [k.to_dict() for k in self.keyframes],
            "interpolation": self.interpolation.value,
        }


@dataclass
class AnimationCurve:
    name: str
    curve_type: str = "FLOAT"  # FLOAT, BOOL, INT
    keys: List[Tuple[float, float]] = field(default_factory=list)  # (time, value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "curve_type": self.curve_type,
            "keys": self.keys,
        }


@dataclass
class AnimationMarker:
    name: str
    marker_type: MarkerType55
    time_sec: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "marker_type": self.marker_type.value,
            "time_sec": self.time_sec,
        }


@dataclass
class AnimationEvent:
    name: str
    time_sec: float
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "time_sec": self.time_sec,
            "payload": self.payload,
        }


@dataclass
class AnimationClip:
    clip_id: str
    start_time: float = 0.0
    end_time: float = 1.0
    loop: bool = True
    rate: float = 1.0
    mirror: bool = False
    additive: bool = False
    root_motion: bool = False

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "loop": self.loop,
            "rate": self.rate,
            "mirror": self.mirror,
            "additive": self.additive,
            "root_motion": self.root_motion,
        }


@dataclass
class AnimationDefinition:
    animation_id: str
    name: str
    anim_type: AnimationType55
    duration: float = 1.0
    sample_rate: int = 30
    skeleton_reference: str = "SKEL_Humanoid"
    source_reference: str = "SRC_Default"
    tracks: List[AnimationTrack] = field(default_factory=list)
    curves: List[AnimationCurve] = field(default_factory=list)
    markers: List[AnimationMarker] = field(default_factory=list)
    events: List[AnimationEvent] = field(default_factory=list)
    root_motion_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.animation_id) and
            self.duration > 0.0 and
            self.sample_rate > 0 and
            bool(self.skeleton_reference) and
            len(self.tracks) > 0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "animation_id": self.animation_id,
            "name": self.name,
            "anim_type": self.anim_type.value,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "skeleton_reference": self.skeleton_reference,
            "source_reference": self.source_reference,
            "track_count": len(self.tracks),
            "tracks": [t.to_dict() for t in self.tracks],
            "curves": [c.to_dict() for c in self.curves],
            "markers": [m.to_dict() for m in self.markers],
            "events": [e.to_dict() for e in self.events],
            "root_motion_enabled": self.root_motion_enabled,
            "metadata": self.metadata,
        }


@dataclass
class RetargetProfile55:
    profile_id: str
    source_skeleton: str
    target_skeleton: str
    bone_mapping: Dict[str, str] = field(default_factory=dict)
    translation_policy: str = "ABSOLUTE"
    rotation_policy: str = "ORIENTATION"
    scale_policy: str = "UNIFORM"
    twist_bones: List[str] = field(default_factory=list)
    ik_goals: List[str] = field(default_factory=lambda: ["IK_Foot_L", "IK_Foot_R"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "source_skeleton": self.source_skeleton,
            "target_skeleton": self.target_skeleton,
            "bone_mapping": self.bone_mapping,
            "translation_policy": self.translation_policy,
            "rotation_policy": self.rotation_policy,
            "scale_policy": self.scale_policy,
            "twist_bones": self.twist_bones,
            "ik_goals": self.ik_goals,
        }


@dataclass
class PoseLibrary55:
    library_id: str
    poses: Dict[str, Dict[str, Tuple[float, float, float]]] = field(default_factory=dict)
    tags: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "library_id": self.library_id,
            "pose_count": len(self.poses),
            "tags": self.tags,
        }


@dataclass
class BlendSpace55:
    blend_id: str
    dimensions: int = 1  # 1D or 2D
    param_x_name: str = "Speed"
    param_x_range: Tuple[float, float] = (0.0, 600.0)
    param_y_name: Optional[str] = None
    param_y_range: Optional[Tuple[float, float]] = None
    samples: List[Tuple[float, str]] = field(default_factory=list)  # (val_x, animation_id)
    blend_type: BlendType55 = BlendType55.LINEAR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blend_id": self.blend_id,
            "dimensions": self.dimensions,
            "param_x_name": self.param_x_name,
            "param_x_range": self.param_x_range,
            "param_y_name": self.param_y_name,
            "param_y_range": self.param_y_range,
            "samples": self.samples,
            "blend_type": self.blend_type.value,
        }


@dataclass
class MontageSection55:
    name: str
    start_time: float
    length: float
    next_section: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "start_time": self.start_time,
            "length": self.length,
            "next_section": self.next_section,
        }


@dataclass
class AnimationMontage55:
    montage_id: str
    animation_id: str
    sections: List[MontageSection55] = field(default_factory=list)
    notifies: List[AnimationMarker] = field(default_factory=list)
    blend_in_sec: float = 0.25
    blend_out_sec: float = 0.25

    def to_dict(self) -> Dict[str, Any]:
        return {
            "montage_id": self.montage_id,
            "animation_id": self.animation_id,
            "sections": [s.to_dict() for s in self.sections],
            "notifies": [n.to_dict() for n in self.notifies],
            "blend_in_sec": self.blend_in_sec,
            "blend_out_sec": self.blend_out_sec,
        }


@dataclass
class StateTransition55:
    from_state: str
    to_state: str
    condition: str
    duration_sec: float = 0.2
    priority: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "condition": self.condition,
            "duration_sec": self.duration_sec,
            "priority": self.priority,
        }


@dataclass
class AnimationStateMachine55:
    machine_id: str
    states: List[str] = field(default_factory=list)
    transitions: List[StateTransition55] = field(default_factory=list)
    default_state: str = "IDLE"
    allow_cycles: bool = True

    def has_cycle(self) -> bool:
        adj = {}
        for t in self.transitions:
            adj.setdefault(t.from_state, []).append(t.to_state)

        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for s in self.states:
            if s not in visited:
                if dfs(s):
                    return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "states": self.states,
            "transitions": [t.to_dict() for t in self.transitions],
            "default_state": self.default_state,
            "allow_cycles": self.allow_cycles,
        }


@dataclass
class MotionWarpingProfile55:
    profile_id: str
    warp_target_bone: str = "PELVIS"
    max_translation_warp_cm: float = 50.0
    max_rotation_warp_deg: float = 45.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "warp_target_bone": self.warp_target_bone,
            "max_translation_warp_cm": self.max_translation_warp_cm,
            "max_rotation_warp_deg": self.max_rotation_warp_deg,
        }


@dataclass
class FacialAnimationTrack55:
    morph_name: str
    keys: List[Tuple[float, float]] = field(default_factory=list)  # (time, weight)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "morph_name": self.morph_name,
            "keys": self.keys,
        }


@dataclass
class AnimationCompressionProfile55:
    method: CompressionMethod55 = CompressionMethod55.KEYFRAME_REDUCTION
    max_error_cm: float = 0.05
    budget_kb: float = 512.0
    compressed_size_kb: float = 128.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method.value,
            "max_error_cm": self.max_error_cm,
            "budget_kb": self.budget_kb,
            "compressed_size_kb": self.compressed_size_kb,
        }


@dataclass
class AnimationLODProfile55:
    lod_levels: int = 4
    update_rates_hz: List[int] = field(default_factory=lambda: [60, 30, 15, 5])
    distance_thresholds_m: List[float] = field(default_factory=lambda: [5.0, 15.0, 30.0, 60.0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lod_levels": self.lod_levels,
            "update_rates_hz": self.update_rates_hz,
            "distance_thresholds_m": self.distance_thresholds_m,
        }


@dataclass
class RuntimeProfile55:
    profile_id: str
    memory_budget_mb: float = 32.0
    max_active_bones: int = 80
    enable_streaming: bool = True
    streaming_chunk_size_kb: int = 64

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "memory_budget_mb": self.memory_budget_mb,
            "max_active_bones": self.max_active_bones,
            "enable_streaming": self.enable_streaming,
            "streaming_chunk_size_kb": self.streaming_chunk_size_kb,
        }


@dataclass
class AnimationDiff55:
    diff_id: str
    duration_changed: bool = False
    tracks_changed: bool = False
    events_changed: bool = False
    compression_changed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diff_id": self.diff_id,
            "duration_changed": self.duration_changed,
            "tracks_changed": self.tracks_changed,
            "events_changed": self.events_changed,
            "compression_changed": self.compression_changed,
        }
