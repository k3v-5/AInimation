"""
Universal Audio World Models (UAF-81.76).
Normative dataclasses and enumerations for runtime audio sources, listeners, clips,
voices, streaming, buses, effects, spatialization, and deterministic snapshots.
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class AudioWorldState(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    DEVICE_LOST = "DEVICE_LOST"
    RECOVERING = "RECOVERING"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class AudioDeviceState(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    LOST = "LOST"
    RECOVERING = "RECOVERING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class AudioSourceState(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    FAILED = "FAILED"


class AudioSourceType(str, Enum):
    POINT = "POINT"
    DIRECTIONAL = "DIRECTIONAL"
    AMBIENT = "AMBIENT"
    CONE = "CONE"


class AudioDistanceModel(str, Enum):
    LINEAR = "LINEAR"
    INVERSE = "INVERSE"
    EXPONENTIAL = "EXPONENTIAL"
    LOGARITHMIC = "LOGARITHMIC"
    CUSTOM = "CUSTOM"


class VoiceStealingPolicy(str, Enum):
    REJECT = "REJECT"
    STEAL_LOWEST_PRIORITY = "STEAL_LOWEST_PRIORITY"
    STEAL_OLDEST = "STEAL_OLDEST"
    STEAL_QUIETEST = "STEAL_QUIETEST"
    CUSTOM = "CUSTOM"


class VoiceState(str, Enum):
    STOPPED = "STOPPED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    VIRTUAL = "VIRTUAL"
    RELEASED = "RELEASED"


class LoopMode(str, Enum):
    NO_LOOP = "NO_LOOP"
    LOOP = "LOOP"
    LOOP_REGION = "LOOP_REGION"


class AudioCommandType(str, Enum):
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    STOP = "STOP"
    SEEK = "SEEK"
    SET_VOLUME = "SET_VOLUME"
    SET_PITCH = "SET_PITCH"
    SET_POSITION = "SET_POSITION"
    SET_VELOCITY = "SET_VELOCITY"
    SET_BUS = "SET_BUS"
    SET_EFFECT_PARAMETER = "SET_EFFECT_PARAMETER"


class AudioEventType(str, Enum):
    PLAY_STARTED = "PLAY_STARTED"
    PLAY_PAUSED = "PLAY_PAUSED"
    PLAY_RESUMED = "PLAY_RESUMED"
    PLAY_STOPPED = "PLAY_STOPPED"
    PLAY_FINISHED = "PLAY_FINISHED"
    VOICE_STOLEN = "VOICE_STOLEN"
    DEVICE_LOST = "DEVICE_LOST"
    DEVICE_RECOVERED = "DEVICE_RECOVERED"


class AudioEffectType(str, Enum):
    GAIN = "GAIN"
    LOW_PASS = "LOW_PASS"
    LOWPASS = "LOW_PASS"
    HIGH_PASS = "HIGH_PASS"
    HIGHPASS = "HIGH_PASS"
    EQUALIZER = "EQUALIZER"
    REVERB = "REVERB"
    COMPRESSOR = "COMPRESSOR"
    LIMITER = "LIMITER"


def copy_dict_deterministic(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: copy_dict_deterministic(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [copy_dict_deterministic(x) for x in data]
    return copy.deepcopy(data)


@dataclass
class AudioClip:
    clip_id: str
    duration_seconds: float = 1.0
    channels: int = 2
    sample_rate: int = 44100
    format: str = "PCM"
    loop_mode: LoopMode = LoopMode.NO_LOOP
    loop_start: float = 0.0
    loop_end: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "duration_seconds": round(float(self.duration_seconds), 6),
            "channels": self.channels,
            "sample_rate": self.sample_rate,
            "format": self.format,
            "loop_mode": self.loop_mode.value,
            "loop_start": round(float(self.loop_start), 6),
            "loop_end": round(float(self.loop_end), 6),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioStream:
    stream_id: str
    buffer_size_bytes: int = 65536
    prebuffered_seconds: float = 0.5
    is_exhausted: bool = False
    is_open: bool = True
    bytes_buffered: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "buffer_size_bytes": self.buffer_size_bytes,
            "prebuffered_seconds": round(float(self.prebuffered_seconds), 6),
            "is_exhausted": self.is_exhausted,
            "is_open": self.is_open,
            "bytes_buffered": self.bytes_buffered,
            "metadata": copy_dict_deterministic(self.metadata),
        }

    @property
    def buffer_size(self) -> int:
        return self.buffer_size_bytes

    @property
    def buffered_bytes(self) -> int:
        return self.bytes_buffered


@dataclass
class AudioDevice:
    device_id: str
    sample_rate: int = 44100
    channel_count: int = 2
    format: str = "FLOAT32"
    state: AudioDeviceState = AudioDeviceState.READY
    latency: float = 0.01
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "sample_rate": self.sample_rate,
            "channel_count": self.channel_count,
            "format": self.format,
            "state": self.state.value,
            "latency": round(float(self.latency), 6),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioEffect:
    effect_id: str
    effect_type: AudioEffectType
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_bypassed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "effect_id": self.effect_id,
            "effect_type": self.effect_type.value,
            "parameters": copy_dict_deterministic(self.parameters),
            "is_bypassed": self.is_bypassed,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioBus:
    bus_id: str
    parent_bus_id: Optional[str] = None
    volume: float = 1.0
    is_muted: bool = False
    is_solo: bool = False
    ducking_factor: float = 1.0
    duck_target_bus_id: Optional[str] = None
    effects: List[AudioEffect] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bus_id": self.bus_id,
            "parent_bus_id": self.parent_bus_id,
            "volume": round(float(self.volume), 6),
            "is_muted": self.is_muted,
            "is_solo": self.is_solo,
            "ducking_factor": round(float(self.ducking_factor), 6),
            "duck_target_bus_id": self.duck_target_bus_id,
            "effects": [e.to_dict() for e in self.effects],
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioVoice:
    voice_id: str
    source_id: str
    clip_id: str
    priority: int = 128
    playback_time: float = 0.0
    state: VoiceState = VoiceState.PLAYING
    computed_gain: float = 1.0
    computed_pitch: float = 1.0
    panning: float = 0.0
    creation_order: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voice_id": self.voice_id,
            "source_id": self.source_id,
            "clip_id": self.clip_id,
            "priority": self.priority,
            "playback_time": round(float(self.playback_time), 6),
            "state": self.state.value,
            "computed_gain": round(float(self.computed_gain), 6),
            "computed_pitch": round(float(self.computed_pitch), 6),
            "panning": round(float(self.panning), 6),
            "creation_order": self.creation_order,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioSource:
    source_id: str
    entity_id: str = ""
    clip_id: str = ""
    stream_id: str = ""
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    direction: List[float] = field(default_factory=lambda: [0.0, 0.0, 1.0])
    volume: float = 1.0
    pitch: float = 1.0
    min_distance: float = 1.0
    max_distance: float = 100.0
    distance_model: AudioDistanceModel = AudioDistanceModel.INVERSE
    rolloff_factor: float = 1.0
    cone_inner_angle: float = 360.0
    cone_outer_angle: float = 360.0
    cone_outer_gain: float = 0.0
    loop: bool = False
    priority: int = 128
    bus_id: str = "SFX"
    spatialized: bool = True
    enabled: bool = True
    state: AudioSourceState = AudioSourceState.STOPPED
    playback_position: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "entity_id": self.entity_id,
            "clip_id": self.clip_id,
            "stream_id": self.stream_id,
            "position": [round(float(v), 6) for v in self.position],
            "velocity": [round(float(v), 6) for v in self.velocity],
            "direction": [round(float(v), 6) for v in self.direction],
            "volume": round(float(self.volume), 6),
            "pitch": round(float(self.pitch), 6),
            "min_distance": round(float(self.min_distance), 6),
            "max_distance": round(float(self.max_distance), 6),
            "distance_model": self.distance_model.value,
            "rolloff_factor": round(float(self.rolloff_factor), 6),
            "cone_inner_angle": round(float(self.cone_inner_angle), 6),
            "cone_outer_angle": round(float(self.cone_outer_angle), 6),
            "cone_outer_gain": round(float(self.cone_outer_gain), 6),
            "loop": self.loop,
            "priority": self.priority,
            "bus_id": self.bus_id,
            "spatialized": self.spatialized,
            "enabled": self.enabled,
            "state": self.state.value,
            "playback_position": round(float(self.playback_position), 6),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioListener:
    listener_id: str
    entity_id: str = ""
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    forward: List[float] = field(default_factory=lambda: [0.0, 0.0, 1.0])
    up: List[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    gain: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "listener_id": self.listener_id,
            "entity_id": self.entity_id,
            "position": [round(float(v), 6) for v in self.position],
            "velocity": [round(float(v), 6) for v in self.velocity],
            "forward": [round(float(v), 6) for v in self.forward],
            "up": [round(float(v), 6) for v in self.up],
            "gain": round(float(self.gain), 6),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioCommand:
    command_id: str
    command_type: AudioCommandType
    target_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command_type": self.command_type.value,
            "target_id": self.target_id,
            "parameters": copy_dict_deterministic(self.parameters),
            "timestamp": round(float(self.timestamp), 6),
        }


@dataclass
class AudioEvent:
    event_id: str
    event_type: AudioEventType
    source_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source_id": self.source_id,
            "payload": copy_dict_deterministic(self.payload),
            "timestamp": round(float(self.timestamp), 6),
        }


@dataclass
class AudioSnapshot:
    snapshot_id: str
    world_id: str = ""
    timestamp: float = 0.0
    sources: Dict[str, Any] = field(default_factory=dict)
    voices: Dict[str, Any] = field(default_factory=dict)
    buses: Dict[str, Any] = field(default_factory=dict)
    snapshot_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "world_id": self.world_id,
            "timestamp": round(float(self.timestamp), 6),
            "sources": copy_dict_deterministic(self.sources),
            "voices": copy_dict_deterministic(self.voices),
            "buses": copy_dict_deterministic(self.buses),
            "snapshot_hash": self.snapshot_hash,
        }


@dataclass
class AudioReplayCommand:
    command_id: str
    command_type: str
    target_id: str
    params: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command_type": self.command_type,
            "target_id": self.target_id,
            "params": copy_dict_deterministic(self.params),
            "timestamp": round(float(self.timestamp), 6),
        }


@dataclass
class AudioReplay:
    replay_id: str
    commands: List[AudioReplayCommand] = field(default_factory=list)
    is_finished: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "commands": [c.to_dict() for c in self.commands],
            "is_finished": self.is_finished,
        }


@dataclass
class AudioMixer:
    mixer_id: str = "master_mixer"
    master_bus_id: str = "MASTER"
    buses: Dict[str, AudioBus] = field(default_factory=dict)
    active_voices: Dict[str, AudioVoice] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mixer_id": self.mixer_id,
            "master_bus_id": self.master_bus_id,
            "buses": {k: v.to_dict() for k, v in sorted(self.buses.items())},
            "active_voices": {k: v.to_dict() for k, v in sorted(self.active_voices.items())},
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioWorldSettings:
    max_voices: int = 64
    max_sources: int = 1000
    max_clips: int = 500
    max_streams: int = 64
    max_buses: int = 32
    max_commands: int = 1000
    max_stream_memory_bytes: int = 67108864  # 64 MB
    sample_rate: int = 44100
    speed_of_sound: float = 343.3
    doppler_scale: float = 1.0
    doppler_min_pitch: float = 0.1
    doppler_max_pitch: float = 4.0
    master_volume: float = 1.0
    voice_stealing_policy: VoiceStealingPolicy = VoiceStealingPolicy.STEAL_LOWEST_PRIORITY
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_voices": self.max_voices,
            "max_sources": self.max_sources,
            "max_clips": self.max_clips,
            "max_streams": self.max_streams,
            "max_buses": self.max_buses,
            "max_commands": self.max_commands,
            "max_stream_memory_bytes": self.max_stream_memory_bytes,
            "sample_rate": self.sample_rate,
            "speed_of_sound": round(float(self.speed_of_sound), 4),
            "doppler_scale": round(float(self.doppler_scale), 4),
            "doppler_min_pitch": round(float(self.doppler_min_pitch), 4),
            "doppler_max_pitch": round(float(self.doppler_max_pitch), 4),
            "master_volume": round(float(self.master_volume), 4),
            "voice_stealing_policy": self.voice_stealing_policy.value,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AudioWorld:
    audio_world_id: str
    runtime_world_id: str = ""
    state: AudioWorldState = AudioWorldState.CREATED
    settings: AudioWorldSettings = field(default_factory=AudioWorldSettings)
    devices: Dict[str, AudioDevice] = field(default_factory=dict)
    active_device_id: Optional[str] = None
    listeners: Dict[str, AudioListener] = field(default_factory=dict)
    active_listener_id: Optional[str] = None
    sources: Dict[str, AudioSource] = field(default_factory=dict)
    clips: Dict[str, AudioClip] = field(default_factory=dict)
    streams: Dict[str, AudioStream] = field(default_factory=dict)
    mixer: AudioMixer = field(default_factory=AudioMixer)
    command_queue: List[AudioCommand] = field(default_factory=list)
    events: List[AudioEvent] = field(default_factory=list)
    time_seconds: float = 0.0
    frames_rendered: int = 0
    content_fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audio_world_id": self.audio_world_id,
            "runtime_world_id": self.runtime_world_id,
            "state": self.state.value,
            "settings": self.settings.to_dict(),
            "devices": {k: v.to_dict() for k, v in sorted(self.devices.items())},
            "active_device_id": self.active_device_id,
            "listeners": {k: v.to_dict() for k, v in sorted(self.listeners.items())},
            "active_listener_id": self.active_listener_id,
            "sources": {k: v.to_dict() for k, v in sorted(self.sources.items())},
            "clips": {k: v.to_dict() for k, v in sorted(self.clips.items())},
            "streams": {k: v.to_dict() for k, v in sorted(self.streams.items())},
            "mixer": self.mixer.to_dict(),
            "time_seconds": round(float(self.time_seconds), 6),
            "frames_rendered": self.frames_rendered,
        }

    def compute_fingerprint(self) -> str:
        data = self.to_dict()
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
