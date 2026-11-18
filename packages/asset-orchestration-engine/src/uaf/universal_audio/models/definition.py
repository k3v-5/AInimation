"""
UAF-81.59 Universal Audio, Music, Voice, Ambience, 3D Audio & Audio Simulation System.
Normative Data Models and Types.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
import hashlib
import json
import math
import uuid
import time


# ============================================================================
# ENUMS
# ============================================================================

class AudioCategory(str, Enum):
    MASTER = "MASTER"
    MUSIC = "MUSIC"
    SFX = "SFX"
    FOLEY = "FOLEY"
    VOICE = "VOICE"
    DIALOGUE = "DIALOGUE"
    AMBIENCE = "AMBIENCE"
    UI = "UI"
    RADIO = "RADIO"
    VEHICLE = "VEHICLE"
    WEAPON = "WEAPON"
    ENVIRONMENT = "ENVIRONMENT"


class AudioClipType(str, Enum):
    ONE_SHOT = "ONE_SHOT"
    LOOP = "LOOP"
    MUSIC = "MUSIC"
    VOICE = "VOICE"
    AMBIENCE = "AMBIENCE"
    DIALOGUE = "DIALOGUE"
    UI = "UI"


class AudioFormat(str, Enum):
    WAV = "WAV"
    OGG = "OGG"
    FLAC = "FLAC"
    MP3 = "MP3"
    PROCEDURAL = "PROCEDURAL"


class AttenuationCurveType(str, Enum):
    LINEAR = "LINEAR"
    INVERSE = "INVERSE"
    INVERSE_SQUARE = "INVERSE_SQUARE"
    CUSTOM = "CUSTOM"


class AudioEventType(str, Enum):
    PLAY = "PLAY"
    STOP = "STOP"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    SET_PARAMETER = "SET_PARAMETER"
    SET_STATE = "SET_STATE"
    MUSIC_TRANSITION = "MUSIC_TRANSITION"
    DIALOGUE_START = "DIALOGUE_START"
    DIALOGUE_END = "DIALOGUE_END"
    RADIO_START = "RADIO_START"
    RADIO_END = "RADIO_END"


class AudioCommandType(str, Enum):
    PLAY = "PLAY"
    STOP = "STOP"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    SET_PARAMETER = "SET_PARAMETER"
    SET_VOLUME = "SET_VOLUME"
    SET_POSITION = "SET_POSITION"
    SET_BUS = "SET_BUS"
    SET_STATE = "SET_STATE"
    LOAD = "LOAD"
    UNLOAD = "UNLOAD"


class CommandFailureCode(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    FALLBACK = "FALLBACK"
    DEFERRED = "DEFERRED"
    ASSET_MISSING = "ASSET_MISSING"
    VOICE_LIMIT_REACHED = "VOICE_LIMIT_REACHED"
    INVALID_BUS = "INVALID_BUS"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    DEVICE_LOST = "DEVICE_LOST"


class AudioBusType(str, Enum):
    MASTER = "MASTER"
    MUSIC = "MUSIC"
    SFX = "SFX"
    FOLEY = "FOLEY"
    VOICE = "VOICE"
    DIALOGUE = "DIALOGUE"
    AMBIENCE = "AMBIENCE"
    UI = "UI"
    RADIO = "RADIO"
    VEHICLE = "VEHICLE"
    WEAPON = "WEAPON"
    ENVIRONMENT = "ENVIRONMENT"
    CUSTOM = "CUSTOM"


class MusicState(str, Enum):
    EXPLORATION = "EXPLORATION"
    COMBAT = "COMBAT"
    DANGER = "DANGER"
    VICTORY = "VICTORY"
    DEFEAT = "DEFEAT"
    MENU = "MENU"
    CINEMATIC = "CINEMATIC"
    CUSTOM = "CUSTOM"


class MusicTransitionType(str, Enum):
    CROSSFADE = "CROSSFADE"
    FADE_OUT_FADE_IN = "FADE_OUT_FADE_IN"
    BEAT_SYNC = "BEAT_SYNC"
    BAR_SYNC = "BAR_SYNC"
    IMMEDIATE = "IMMEDIATE"


class MusicLayerType(str, Enum):
    BASE = "BASE"
    RHYTHM = "RHYTHM"
    MELODY = "MELODY"
    TENSION = "TENSION"
    PERCUSSION = "PERCUSSION"
    STINGER = "STINGER"


class ZoneShape(str, Enum):
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    POLYGON = "POLYGON"
    VOLUME = "VOLUME"


class ReverbPreset(str, Enum):
    ROOM = "ROOM"
    HALL = "HALL"
    CAVE = "CAVE"
    TUNNEL = "TUNNEL"
    OUTDOOR = "OUTDOOR"
    UNDERWATER = "UNDERWATER"
    CUSTOM = "CUSTOM"


class OcclusionModel(str, Enum):
    RAYCAST = "RAYCAST"
    SHAPE_CAST = "SHAPE_CAST"
    PORTAL_GRAPH = "PORTAL_GRAPH"
    APPROXIMATION = "APPROXIMATION"


class SurfaceType(str, Enum):
    CONCRETE = "CONCRETE"
    DIRT = "DIRT"
    METAL = "METAL"
    WOOD = "WOOD"
    WATER = "WATER"
    GRASS = "GRASS"
    FLESH = "FLESH"


class MovementType(str, Enum):
    WALK = "WALK"
    RUN = "RUN"
    SPRINT = "SPRINT"
    CROUCH = "CROUCH"
    JUMP = "JUMP"
    LAND = "LAND"
    SWIM = "SWIM"
    CUSTOM = "CUSTOM"


class AudioParameterType(str, Enum):
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    ENUM = "ENUM"


class AudioLODLevel(str, Enum):
    FULL = "FULL"
    REDUCED = "REDUCED"
    AMBIENT_ONLY = "AMBIENT_ONLY"
    DISABLED = "DISABLED"


class StreamingPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    BACKGROUND = "BACKGROUND"


class VoiceStealingPolicy(str, Enum):
    OLDEST = "OLDEST"
    QUIETEST = "QUIETEST"
    LOWEST_PRIORITY = "LOWEST_PRIORITY"
    FARTHEST = "FARTHEST"
    LEAST_IMPORTANT = "LEAST_IMPORTANT"


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class AudioAsset:
    """Represents a digital audio asset."""
    asset_id: str
    source: str
    format: AudioFormat = AudioFormat.WAV
    duration: float = 1.0
    channels: int = 2
    sample_rate: int = 44100
    streaming: bool = False
    compression: str = "PCM"
    loopable: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def canonical_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "source": self.source,
            "format": self.format.value,
            "duration": round(self.duration, 4),
            "channels": self.channels,
            "sample_rate": self.sample_rate,
            "streaming": self.streaming,
            "compression": self.compression,
            "loopable": self.loopable,
        }


@dataclass
class AttenuationSettings:
    """Distance-based 3D sound attenuation properties."""
    min_distance: float = 1.0
    max_distance: float = 50.0
    curve_type: AttenuationCurveType = AttenuationCurveType.LINEAR
    custom_curve: Optional[List[Tuple[float, float]]] = None
    inner_cone_angle: float = 90.0
    outer_cone_angle: float = 180.0
    outer_cone_gain: float = 0.2

    def calculate_attenuation(self, distance: float) -> float:
        if distance <= self.min_distance:
            return 1.0
        if distance >= self.max_distance:
            return 0.0

        ratio = (distance - self.min_distance) / (self.max_distance - self.min_distance)
        if self.curve_type == AttenuationCurveType.LINEAR:
            return max(0.0, 1.0 - ratio)
        elif self.curve_type == AttenuationCurveType.INVERSE:
            return self.min_distance / max(0.001, distance)
        elif self.curve_type == AttenuationCurveType.INVERSE_SQUARE:
            return (self.min_distance / max(0.001, distance)) ** 2
        elif self.curve_type == AttenuationCurveType.CUSTOM and self.custom_curve:
            for i in range(len(self.custom_curve) - 1):
                d1, g1 = self.custom_curve[i]
                d2, g2 = self.custom_curve[i + 1]
                if d1 <= ratio <= d2:
                    t = (ratio - d1) / max(1e-5, (d2 - d1))
                    return g1 + t * (g2 - g1)
            return self.custom_curve[-1][1]
        return max(0.0, 1.0 - ratio)


@dataclass
class AudioEmitter:
    """3D or 2D entity emitting sound into the audio environment."""
    emitter_id: str
    owner: str = "world"
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    audio_events: List[str] = field(default_factory=list)
    attenuation: AttenuationSettings = field(default_factory=AttenuationSettings)
    priority: int = 50
    bus: str = AudioBusType.SFX.value
    spatialized: bool = True
    active: bool = True
    current_voice_id: Optional[str] = None


@dataclass
class AudioListener:
    """Virtual ear capturing spatialized audio."""
    listener_id: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    up_vector: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    forward_vector: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    priority: int = 100
    active: bool = True


@dataclass
class AudioEvent:
    """An event triggering audio playback or state modulation."""
    event_id: str
    audio_asset_id: str
    emitter_id: Optional[str] = None
    priority: int = 50
    volume: float = 1.0
    pitch: float = 1.0
    bus: str = AudioBusType.SFX.value
    spatialization: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    variations: List[str] = field(default_factory=list)
    randomize_pitch: float = 0.0
    randomize_volume: float = 0.0
    loop: bool = False


@dataclass
class AudioBus:
    """Audio bus mixing and routing channel."""
    bus_id: str
    parent_id: Optional[str] = None
    volume: float = 1.0
    mute: bool = False
    solo: bool = False
    ducking_target: Optional[str] = None
    ducking_db: float = 0.0
    send_levels: Dict[str, float] = field(default_factory=dict)


@dataclass
class AudioDucking:
    """Rule for ducking a bus when another bus is active."""
    source_bus: str
    target_bus: str
    ducking_db: float = -12.0
    attack_time: float = 0.1
    release_time: float = 0.5
    active: bool = False


@dataclass
class AudioSnapshot:
    """Preset mix snapshot defining bus volume overrides."""
    snapshot_id: str
    bus_volumes: Dict[str, float] = field(default_factory=dict)
    blend_time: float = 1.0
    priority: int = 10
    active: bool = False


@dataclass
class MixerNode:
    node_id: str
    bus_id: str
    connected_targets: List[str] = field(default_factory=list)


@dataclass
class AudioMixerGraph:
    nodes: Dict[str, MixerNode] = field(default_factory=dict)

    def add_connection(self, source_node: str, target_node: str) -> bool:
        if source_node not in self.nodes or target_node not in self.nodes:
            return False
        self.nodes[source_node].connected_targets.append(target_node)
        return True

    def has_cycle(self) -> bool:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.nodes[node].connected_targets:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        return False


@dataclass
class MusicTrack:
    track_id: str
    audio_asset_id: str
    length: float = 120.0
    loop_points: Tuple[float, float] = (0.0, 120.0)
    layers: Dict[str, str] = field(default_factory=dict)
    mood: str = "NEUTRAL"
    intensity: float = 0.5


@dataclass
class MusicTransition:
    from_state: MusicState
    to_state: MusicState
    transition_type: MusicTransitionType = MusicTransitionType.CROSSFADE
    duration: float = 2.0


@dataclass
class MusicStateMachine:
    current_state: MusicState = MusicState.EXPLORATION
    target_state: Optional[MusicState] = None
    tracks: Dict[MusicState, MusicTrack] = field(default_factory=dict)
    transitions: List[MusicTransition] = field(default_factory=list)
    active_layers: Set[str] = field(default_factory=set)
    current_intensity: float = 0.5


@dataclass
class AudioZone:
    zone_id: str
    shape: ZoneShape = ZoneShape.BOX
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    extents: Tuple[float, float, float] = (10.0, 10.0, 10.0)
    priority: int = 10
    layers: List[str] = field(default_factory=list)
    reverb_preset: ReverbPreset = ReverbPreset.OUTDOOR

    def contains(self, point: Tuple[float, float, float]) -> bool:
        px, py, pz = point
        cx, cy, cz = self.center
        if self.shape == ZoneShape.BOX:
            ex, ey, ez = self.extents
            return abs(px - cx) <= ex and abs(py - cy) <= ey and abs(pz - cz) <= ez
        elif self.shape == ZoneShape.SPHERE:
            r = self.extents[0]
            dist_sq = (px - cx)**2 + (py - cy)**2 + (pz - cz)**2
            return dist_sq <= r**2
        return True


@dataclass
class AudioPortal:
    portal_id: str
    room_a: str
    room_b: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    dimensions: Tuple[float, float] = (2.0, 3.0)
    open_factor: float = 1.0
    transmission_loss: float = 0.1


@dataclass
class ReverbSettings:
    room_size: float = 0.5
    decay: float = 1.5
    pre_delay: float = 0.02
    early_reflections: float = 0.7
    wet_level: float = 0.3
    dry_level: float = 0.7


@dataclass
class OcclusionResult:
    occlusion_factor: float = 0.0
    obstruction_factor: float = 0.0
    low_pass_cutoff: float = 20000.0
    volume_attenuation: float = 1.0


@dataclass
class VoiceProfile:
    voice_id: str
    speaker_name: str
    language: str = "en"
    pitch_range: Tuple[float, float] = (0.9, 1.1)
    priority: int = 70


@dataclass
class DialogueLineAudio:
    line_id: str
    speaker: str
    audio_asset_id: str
    duration: float = 3.0
    subtitle: str = ""
    priority: int = 80
    interruptible: bool = True


@dataclass
class RadioChannel:
    channel_id: str
    station_name: str
    music_playlist: List[str] = field(default_factory=list)
    voice_clips: List[str] = field(default_factory=list)
    current_track_index: int = 0
    static_level: float = 0.05
    active: bool = False


@dataclass
class FootstepAudioConfig:
    surface_sound_map: Dict[SurfaceType, List[str]] = field(default_factory=dict)
    movement_pitch_map: Dict[MovementType, float] = field(default_factory=lambda: {
        MovementType.WALK: 1.0,
        MovementType.RUN: 1.1,
        MovementType.SPRINT: 1.25,
        MovementType.CROUCH: 0.85,
        MovementType.JUMP: 1.15,
        MovementType.LAND: 0.95,
        MovementType.SWIM: 0.9,
    })


@dataclass
class AudioParameter:
    name: str
    param_type: AudioParameterType = AudioParameterType.FLOAT
    value: Any = 0.0
    min_value: float = 0.0
    max_value: float = 1.0


@dataclass
class AudioCommand:
    command_id: str
    command_type: AudioCommandType
    target_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class AudioVoice:
    """An actively synthesized or playing voice instance."""
    voice_id: str
    event_id: str
    asset_id: str
    emitter_id: Optional[str]
    volume: float = 1.0
    pitch: float = 1.0
    priority: int = 50
    start_time: float = field(default_factory=time.time)
    duration: float = 1.0
    virtual: bool = False
    bus: str = AudioBusType.SFX.value


@dataclass
class AudioState:
    """Central reproducible runtime state of the audio engine."""
    master_volume: float = 1.0
    music_volume: float = 1.0
    sfx_volume: float = 1.0
    dialogue_volume: float = 1.0
    ambience_volume: float = 1.0
    voice_volume: float = 1.0
    ui_volume: float = 1.0
    audio_mute_state: bool = False
    bus_volumes: Dict[str, float] = field(default_factory=lambda: {
        AudioBusType.MASTER.value: 1.0,
        AudioBusType.MUSIC.value: 1.0,
        AudioBusType.SFX.value: 1.0,
        AudioBusType.DIALOGUE.value: 1.0,
        AudioBusType.AMBIENCE.value: 1.0,
        AudioBusType.UI.value: 1.0,
        AudioBusType.RADIO.value: 1.0,
    })
    active_emitters: Dict[str, AudioEmitter] = field(default_factory=dict)
    active_listeners: Dict[str, AudioListener] = field(default_factory=dict)
    music_state: MusicState = MusicState.EXPLORATION
    parameters: Dict[str, AudioParameter] = field(default_factory=dict)
    snapshots: Dict[str, AudioSnapshot] = field(default_factory=dict)
    active_voices: Dict[str, AudioVoice] = field(default_factory=dict)
    voice_limit: int = 64
    stealing_policy: VoiceStealingPolicy = VoiceStealingPolicy.LOWEST_PRIORITY


@dataclass
class AudioDiagnosticReport:
    """Report generated for telemetry, profiling and debugging."""
    active_voices: int = 0
    voice_limit: int = 64
    active_emitters: int = 0
    active_buses: int = 0
    streaming_assets: int = 0
    cache_usage_mb: float = 0.0
    memory_usage_mb: float = 0.0
    dropped_events: int = 0
    culled_events: int = 0
    device_latency_ms: float = 10.0


@dataclass
class AudioSaveState:
    """Serializable snapshot of audio runtime state."""
    state_dict: Dict[str, Any]
    state_hash: str
    timestamp: float = field(default_factory=time.time)
