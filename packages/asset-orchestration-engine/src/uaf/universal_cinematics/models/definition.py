"""
Universal Cinematic, Cutscene, Camera, Sequencer, Facial Performance, Lip-Sync & Presentation Models (UAF-81.60).
Normative domain models, enums, data contracts, and presentation state definitions.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class PlaybackState(str, Enum):
    """Playback states for a cinematic instance (§6)."""
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    SEEKING = "SEEKING"
    FAST_FORWARD = "FAST_FORWARD"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


class CinematicCommandType(str, Enum):
    """Commands for timeline and presentation control (§7, §141)."""
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    STOP = "STOP"
    RESTART = "RESTART"
    SEEK = "SEEK"
    FAST_FORWARD = "FAST_FORWARD"
    SKIP = "SKIP"
    ABORT = "ABORT"
    SET_PROPERTY = "SET_PROPERTY"
    TRIGGER_EVENT = "TRIGGER_EVENT"
    SET_QUEST_STATE = "SET_QUEST_STATE"
    SET_ENTITY_STATE = "SET_ENTITY_STATE"
    SET_WORLD_STATE = "SET_WORLD_STATE"
    PLAY_AUDIO = "PLAY_AUDIO"
    PLAY_VFX = "PLAY_VFX"
    SET_LIGHTING = "SET_LIGHTING"
    SET_CAMERA = "SET_CAMERA"


class SeekMode(str, Enum):
    """Seek modes for timeline evaluation (§12)."""
    CONTINUOUS = "CONTINUOUS"
    SNAP = "SNAP"
    MARKER = "MARKER"
    CHECKPOINT = "CHECKPOINT"


class TrackType(str, Enum):
    """Types of cinematic tracks (§14)."""
    CAMERA = "CAMERA"
    ANIMATION = "ANIMATION"
    FACIAL = "FACIAL"
    AUDIO = "AUDIO"
    DIALOGUE = "DIALOGUE"
    SUBTITLE = "SUBTITLE"
    VFX = "VFX"
    LIGHTING = "LIGHTING"
    TRANSFORM = "TRANSFORM"
    ACTOR = "ACTOR"
    PROPERTY = "PROPERTY"
    EVENT = "EVENT"
    UI = "UI"
    GAMEPLAY = "GAMEPLAY"


class ClipOverlapPolicy(str, Enum):
    """Policies for overlapping clips on a track (§18)."""
    OVERRIDE = "OVERRIDE"
    BLEND = "BLEND"
    STACK = "STACK"
    QUEUE = "QUEUE"
    REJECT = "REJECT"


class BindingType(str, Enum):
    """Binding reference types for cinematic targets (§22)."""
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"
    RUNTIME = "RUNTIME"
    NETWORK = "NETWORK"
    PLAYER = "PLAYER"
    QUEST = "QUEST"


class BindingFailurePolicy(str, Enum):
    """Policy when a target binding cannot be resolved (§23)."""
    FAIL = "FAIL"
    SKIP_TRACK = "SKIP_TRACK"
    USE_FALLBACK = "USE_FALLBACK"
    WAIT = "WAIT"
    RETRY = "RETRY"


class CameraRigType(str, Enum):
    """Camera rig archetypes (§29)."""
    STATIC = "STATIC"
    FOLLOW = "FOLLOW"
    LOOK_AT = "LOOK_AT"
    ORBIT = "ORBIT"
    DOLLY = "DOLLY"
    CRANE = "CRANE"
    HANDHELD = "HANDHELD"
    RAIL = "RAIL"
    SPLINE = "SPLINE"
    CUSTOM = "CUSTOM"


class CameraInterpolationType(str, Enum):
    """Camera interpolation curves (§31)."""
    LINEAR = "LINEAR"
    SMOOTH = "SMOOTH"
    CUBIC = "CUBIC"
    BEZIER = "BEZIER"
    CATMULL_ROM = "CATMULL_ROM"
    CUSTOM = "CUSTOM"


class CameraPriority(str, Enum):
    """Priority resolution when multiple systems request camera (§35)."""
    DEBUG = "DEBUG"              # 100
    CINEMATIC = "CINEMATIC"      # 80
    PHOTO_MODE = "PHOTO_MODE"    # 70
    AIM = "AIM"                  # 50
    VEHICLE = "VEHICLE"          # 30
    GAMEPLAY = "GAMEPLAY"        # 10


class ReleasePolicy(str, Enum):
    """Policy for releasing ownership on finish/abort (§36, §67)."""
    RESTORE_PREVIOUS = "RESTORE_PREVIOUS"
    KEEP_CURRENT = "KEEP_CURRENT"
    RESET_DEFAULT = "RESET_DEFAULT"
    PASS_TO_NEXT = "PASS_TO_NEXT"


class PerformanceChannel(str, Enum):
    """Performance channels for characters (§40)."""
    BODY = "BODY"
    FACE = "FACE"
    EYES = "EYES"
    HEAD = "HEAD"
    HANDS = "HANDS"
    GESTURE = "GESTURE"
    POSTURE = "POSTURE"
    VOICE = "VOICE"


class AnimationLayer(str, Enum):
    """Animation layering slots (§43)."""
    BASE = "BASE"
    UPPER_BODY = "UPPER_BODY"
    LOWER_BODY = "LOWER_BODY"
    FACE = "FACE"
    ADDITIVE = "ADDITIVE"
    GESTURE = "GESTURE"


class RootMotionPolicy(str, Enum):
    """Root motion extraction and application policies (§44)."""
    IGNORE = "IGNORE"
    APPLY = "APPLY"
    CONVERT_TO_WORLD = "CONVERT_TO_WORLD"
    CONVERT_TO_ENTITY = "CONVERT_TO_ENTITY"
    GAMEPLAY_AUTHORITATIVE = "GAMEPLAY_AUTHORITATIVE"


class FacialInputType(str, Enum):
    """Facial animation inputs (§47)."""
    FACIAL_ANIMATION = "FACIAL_ANIMATION"
    BLENDSHAPE = "BLENDSHAPE"
    EXPRESSION = "EXPRESSION"
    POSE = "POSE"
    EMOTION = "EMOTION"
    EYE_DIRECTION = "EYE_DIRECTION"
    BROW = "BROW"
    MOUTH = "MOUTH"


class LipSyncSource(str, Enum):
    """Sources for lip-sync calculation (§50)."""
    PHONEME_DATA = "PHONEME_DATA"
    VISEME_DATA = "VISEME_DATA"
    AUDIO_ANALYSIS = "AUDIO_ANALYSIS"
    PREAUTHORED_TIMING = "PREAUTHORED_TIMING"
    RUNTIME_PROVIDER = "RUNTIME_PROVIDER"


class LipSyncFallback(str, Enum):
    """Fallback policies when phoneme data is unavailable (§52)."""
    AUDIO_ANALYSIS = "AUDIO_ANALYSIS"
    GENERIC_VISEMES = "GENERIC_VISEMES"
    NEUTRAL_MOUTH = "NEUTRAL_MOUTH"


class GameplayLockType(str, Enum):
    """Independent locks for gameplay subsystems (§66)."""
    MOVEMENT = "MOVEMENT"
    COMBAT = "COMBAT"
    INTERACTION = "INTERACTION"
    CAMERA = "CAMERA"
    INPUT = "INPUT"
    UI_CONTROL = "UI_CONTROL"


class BranchConditionType(str, Enum):
    """Condition types for cinematic branching (§72)."""
    CHOICE = "CHOICE"
    QUEST_STATE = "QUEST_STATE"
    PARAMETER = "PARAMETER"
    FLAG = "FLAG"
    ACTOR_STATE = "ACTOR_STATE"
    GAMEPLAY_STATE = "GAMEPLAY_STATE"


class ChoiceTimeoutPolicy(str, Enum):
    """Policy when a player choice times out (§75)."""
    DEFAULT = "DEFAULT"
    CANCEL = "CANCEL"
    BRANCH = "BRANCH"
    PAUSE = "PAUSE"


class SkipPolicy(str, Enum):
    """Policies governing cutscene skip availability (§76)."""
    DISABLED = "DISABLED"
    ANYTIME = "ANYTIME"
    AFTER_CHECKPOINT = "AFTER_CHECKPOINT"
    AFTER_FIRST_VIEW = "AFTER_FIRST_VIEW"
    PLAYER_ONLY = "PLAYER_ONLY"


class FastForwardMultiplier(int, Enum):
    """Speed multipliers for fast-forward mode (§79)."""
    FF_2X = 2
    FF_4X = 4
    FF_8X = 8
    FF_16X = 16


class FastForwardEventPolicy(str, Enum):
    """Policy for events during fast forward (§80)."""
    EXECUTE = "EXECUTE"
    SKIP = "SKIP"
    COALESCE = "COALESCE"
    EXECUTE_ONCE = "EXECUTE_ONCE"


class PauseType(str, Enum):
    """Independent pause domains (§81)."""
    GAME_PAUSE = "GAME_PAUSE"
    CINEMATIC_PAUSE = "CINEMATIC_PAUSE"
    AUDIO_PAUSE = "AUDIO_PAUSE"
    NETWORK_PAUSE = "NETWORK_PAUSE"
    DEBUG_PAUSE = "DEBUG_PAUSE"


class NetworkAuthority(str, Enum):
    """Network authority model for cinematics (§92)."""
    SERVER_AUTHORITATIVE = "SERVER_AUTHORITATIVE"
    CLIENT_AUTHORITATIVE = "CLIENT_AUTHORITATIVE"
    LOCAL_ONLY = "LOCAL_ONLY"
    SHARED = "SHARED"


class JoinInProgressPolicy(str, Enum):
    """Handling players joining during an active cutscene (§95)."""
    JOIN_CURRENT_TIME = "JOIN_CURRENT_TIME"
    RESTART = "RESTART"
    SKIP_LOCAL = "SKIP_LOCAL"
    WAIT_FOR_NEXT = "WAIT_FOR_NEXT"


class EventExecutionPolicy(str, Enum):
    """Idempotency and repetition policy for track events (§98, §149)."""
    ONCE = "ONCE"
    PER_LOOP = "PER_LOOP"
    PER_ENTRY = "PER_ENTRY"
    PER_SEEK = "PER_SEEK"
    MANUAL = "MANUAL"


class RollbackPolicy(str, Enum):
    """Rollback strategy for reversible cinematic commands (§142)."""
    NO_ROLLBACK = "NO_ROLLBACK"
    RESTORE_PREVIOUS = "RESTORE_PREVIOUS"
    RESET_TO_DEFAULT = "RESET_TO_DEFAULT"
    CUSTOM_REVERT = "CUSTOM_REVERT"


# ==============================================================================
# DATA STRUCTURES & VALUE OBJECTS
# ==============================================================================

@dataclass
class CinematicClip:
    """A bounded segment of animation, audio, camera, or event on a track (§15)."""
    clip_id: str
    start: float
    duration: float
    source: str = ""
    blend_in: float = 0.0
    blend_out: float = 0.0
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    layer: AnimationLayer = AnimationLayer.BASE
    root_motion_policy: RootMotionPolicy = RootMotionPolicy.IGNORE
    speed: float = 1.0
    loop: bool = False

    def is_active_at(self, time_val: float) -> bool:
        """Checks whether the clip is active at a given timeline time."""
        if not self.enabled:
            return False
        return self.start <= time_val < (self.start + self.duration)

    def evaluate_weight(self, time_val: float) -> float:
        """Calculates blend weight taking blend_in and blend_out into account."""
        if not self.is_active_at(time_val):
            return 0.0
        local_time = time_val - self.start
        w = self.weight
        if self.blend_in > 0.0 and local_time < self.blend_in:
            w *= (local_time / self.blend_in)
        time_until_end = (self.start + self.duration) - time_val
        if self.blend_out > 0.0 and time_until_end < self.blend_out:
            w *= (time_until_end / self.blend_out)
        return max(0.0, min(1.0, w))


@dataclass
class CinematicMarker:
    """Timeline marker for events, checkpoints, cues, and branches (§19)."""
    marker_id: str
    time: float
    marker_type: str = "event"
    payload: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Dict[str, Any]] = None


@dataclass
class CinematicTrack:
    """A lane containing ordered, synchronized clips (§13, §14)."""
    track_id: str
    track_type: TrackType
    order: int = 0
    enabled: bool = True
    overlap_policy: ClipOverlapPolicy = ClipOverlapPolicy.OVERRIDE
    clips: List[CinematicClip] = field(default_factory=list)
    target_binding: str = ""

    def get_active_clips(self, time_val: float) -> List[CinematicClip]:
        """Returns clips that are active at the given timeline time."""
        if not self.enabled:
            return []
        active = [c for c in self.clips if c.is_active_at(time_val)]
        if self.overlap_policy == ClipOverlapPolicy.OVERRIDE and active:
            # Most recently started clip overrides
            return [max(active, key=lambda c: c.start)]
        return active


@dataclass
class Timeline:
    """Authoritative time ruler for the cinematic (§8, §9, §10)."""
    start_time: float = 0.0
    end_time: float = 10.0
    duration: float = 10.0
    tracks: List[CinematicTrack] = field(default_factory=list)
    markers: List[CinematicMarker] = field(default_factory=list)
    tempo: float = 120.0
    time_resolution: float = 0.01  # Fixed evaluation step in seconds

    def __post_init__(self):
        if self.duration <= 0.0 and self.end_time > self.start_time:
            self.duration = self.end_time - self.start_time
        elif self.end_time <= self.start_time and self.duration > 0.0:
            self.end_time = self.start_time + self.duration


@dataclass
class CinematicBinding:
    """Resolves an abstract cinematic actor/camera/light to a runtime entity (§21, §22)."""
    binding_id: str
    binding_type: BindingType = BindingType.STATIC
    target_reference: str = ""
    fallback_reference: str = ""
    failure_policy: BindingFailurePolicy = BindingFailurePolicy.USE_FALLBACK
    resolved_object_id: str = ""
    retry_count: int = 3


@dataclass
class CinematicCamera:
    """Cine-camera parameters and optics (§27)."""
    camera_id: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # Quaternion (x, y, z, w)
    fov: float = 60.0
    near_clip: float = 0.1
    far_clip: float = 1000.0
    focus_target: str = ""
    aperture: float = 2.8
    focus_distance: float = 5.0


@dataclass
class CameraRig:
    """Camera motion rig with constraints or spline paths (§28, §29, §30)."""
    rig_id: str
    rig_type: CameraRigType = CameraRigType.STATIC
    camera_id: str = ""
    target_id: str = ""
    offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    damping: float = 0.5
    spline_points: List[Tuple[float, float, float]] = field(default_factory=list)
    interpolation: CameraInterpolationType = CameraInterpolationType.SMOOTH


@dataclass
class CameraBlend:
    """Smooth transition between two cameras or camera states (§33)."""
    blend_id: str
    source_camera_id: str
    target_camera_id: str
    duration: float = 1.0
    curve: CameraInterpolationType = CameraInterpolationType.SMOOTH
    priority: CameraPriority = CameraPriority.CINEMATIC


@dataclass
class CameraCut:
    """Instant cut to a designated camera at an exact timeline mark (§34)."""
    cut_id: str
    time: float
    target_camera_id: str


@dataclass
class FacialState:
    """Runtime facial blendshapes, emotional expression and eye gaze (§46, §47, §53)."""
    expressions: Dict[str, float] = field(default_factory=dict)
    blendshapes: Dict[str, float] = field(default_factory=dict)
    emotion: str = "neutral"
    eye_target: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    look_weight: float = 1.0
    look_speed: float = 5.0
    blink_phase: float = 0.0


@dataclass
class LipSyncData:
    """Phoneme/viseme timing and audio sync (§49, §50, §51)."""
    source: LipSyncSource = LipSyncSource.PHONEME_DATA
    phonemes: List[Dict[str, Any]] = field(default_factory=list)
    visemes: List[Dict[str, Any]] = field(default_factory=list)
    current_viseme: str = "neutral"
    audio_sync_time: float = 0.0
    fallback: LipSyncFallback = LipSyncFallback.AUDIO_ANALYSIS


@dataclass
class DialogueClip:
    """Voice line playback synced with subtitle and facial performances (§55, §56)."""
    line_id: str
    speaker: str
    audio_asset_id: str = ""
    subtitle_text: str = ""
    start: float = 0.0
    duration: float = 3.0
    interrupt_policy: str = "ALLOW"
    voice_profile: str = ""


@dataclass
class SubtitleClip:
    """Subtitle presentation segment with accessibility styling (§58, §60)."""
    subtitle_id: str
    text_reference: str
    speaker: str
    start: float = 0.0
    duration: float = 3.0
    style: str = "default"
    position: Tuple[float, float] = (0.5, 0.9)
    color: str = "#FFFFFF"
    size: int = 18
    language: str = "en"
    sound_description: str = ""


@dataclass
class GameplayLock:
    """Stackable, owned reservation of a gameplay control capability (§66, §67, §68)."""
    lock_id: str
    lock_type: GameplayLockType
    owner: str
    reason: str = "cutscene"
    priority: int = 100
    acquired_at: float = 0.0
    release_policy: ReleasePolicy = ReleasePolicy.RESTORE_PREVIOUS


@dataclass
class CinematicChoice:
    """Branching decision prompt presented to player (§74, §75)."""
    choice_id: str
    prompt: str = ""
    options: List[str] = field(default_factory=list)
    default_option: str = ""
    timeout: float = 10.0
    timeout_policy: ChoiceTimeoutPolicy = ChoiceTimeoutPolicy.DEFAULT
    selected_option: str = ""


@dataclass
class CinematicBranch:
    """Conditional flow diverter based on gameplay flags or choices (§71, §72, §73)."""
    branch_id: str
    condition_type: BranchConditionType = BranchConditionType.CHOICE
    condition_key: str = ""
    condition_value: Any = None
    target_timeline_or_marker: str = ""


@dataclass
class CinematicCheckpoint:
    """Snapshot of timeline and runtime state for deterministic recovery (§82, §83)."""
    checkpoint_id: str
    timeline_time: float
    branch_state: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    bindings: Dict[str, str] = field(default_factory=dict)
    camera_state: Dict[str, Any] = field(default_factory=dict)
    actor_state: Dict[str, Any] = field(default_factory=dict)
    locks: List[GameplayLock] = field(default_factory=list)
    dialogue_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CinematicReplay:
    """Deterministic recording of choices, seeds, and timeline events (§85, §86)."""
    replay_id: str
    cinematic_id: str
    seed: int = 42
    timeline_events: List[Dict[str, Any]] = field(default_factory=list)
    branch_choices: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    binding_resolution: Dict[str, str] = field(default_factory=dict)


@dataclass
class CinematicCommand:
    """Discrete state mutation issued by a timeline event or script (§140)."""
    command_id: str
    command_type: CinematicCommandType
    payload: Dict[str, Any] = field(default_factory=dict)
    authority: NetworkAuthority = NetworkAuthority.SERVER_AUTHORITATIVE
    execution_policy: EventExecutionPolicy = EventExecutionPolicy.ONCE
    rollback_policy: RollbackPolicy = RollbackPolicy.RESTORE_PREVIOUS
    is_irreversible: bool = False
    executed: bool = False
    previous_value: Any = None


@dataclass
class CinematicAsset:
    """Immutable, declarative specification of a cinematic cutscene (§4)."""
    cinematic_id: str
    version: str = "1.0.0"
    duration: float = 10.0
    timeline: Timeline = field(default_factory=Timeline)
    bindings: List[CinematicBinding] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    skip_policy: SkipPolicy = SkipPolicy.ANYTIME


@dataclass
class CinematicInstance:
    """Active runtime evaluation instance of a cinematic asset (§5)."""
    instance_id: str
    cinematic_id: str
    current_time: float = 0.0
    playback_state: PlaybackState = PlaybackState.IDLE
    bindings: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    checkpoint: Optional[CinematicCheckpoint] = None
    owner: str = "gameplay"
    network_instance_id: str = ""
    start_tick: int = 0
    fast_forward_multiplier: FastForwardMultiplier = FastForwardMultiplier.FF_2X
    pause_type: Optional[PauseType] = None


@dataclass
class CinematicState:
    """Snapshot of overall cinematic engine state."""
    playback_state: PlaybackState = PlaybackState.IDLE
    current_time: float = 0.0
    active_cameras: List[str] = field(default_factory=list)
    active_locks: List[GameplayLock] = field(default_factory=list)
    active_dialogues: List[str] = field(default_factory=list)
    active_subtitles: List[str] = field(default_factory=list)
    active_vfx: List[str] = field(default_factory=list)
    executed_events: Set[str] = field(default_factory=set)


@dataclass
class CinematicSaveState:
    """Persisted save data for cutscenes in progress (§89)."""
    cinematic_id: str
    instance_id: str
    timeline_time: float
    playback_state: PlaybackState
    branch_state: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    checkpoint_id: str = ""
    asset_hash: str = ""
    version: str = "1.0.0"


@dataclass
class CinematicDiagnosticReport:
    """Diagnostic and performance metrics for cutscene execution (§54, §55)."""
    cinematic_id: str
    instance_id: str
    is_healthy: bool = True
    timeline_evaluation_time_ms: float = 0.0
    active_tracks_count: int = 0
    active_clips_count: int = 0
    active_bindings_count: int = 0
    active_locks_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
