"""
Universal Runtime Audio Fabricator (UAF-81.76).
Drives the audio world, voice allocation, 3D spatialization, attenuation, Doppler,
hierarchical bus mixing, effect chains, and deterministic snapshots.
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from ..models.definition import (
    AudioWorldState,
    AudioDeviceState,
    AudioSourceState,
    AudioSourceType,
    AudioDistanceModel,
    VoiceStealingPolicy,
    VoiceState,
    LoopMode,
    AudioCommandType,
    AudioEventType,
    AudioEffectType,
    AudioClip,
    AudioStream,
    AudioDevice,
    AudioEffect,
    AudioBus,
    AudioVoice,
    AudioSource,
    AudioListener,
    AudioCommand,
    AudioEvent,
    AudioSnapshot,
    AudioReplayCommand,
    AudioReplay,
    AudioMixer,
    AudioWorldSettings,
    AudioWorld,
)


def _vec3_dist(a: List[float], b: List[float]) -> float:
    return math.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )


def _vec3_dot(a: List[float], b: List[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _vec3_cross(a: List[float], b: List[float]) -> List[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _vec3_norm(a: List[float]) -> List[float]:
    l = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)
    if l <= 1e-9:
        return [0.0, 0.0, 1.0]
    return [a[0] / l, a[1] / l, a[2] / l]


class UniversalRuntimeAudioFabricator:
    """Fabricates and executes the runtime audio world pipeline."""

    def __init__(self):
        self.worlds: Dict[str, AudioWorld] = {}
        self.active_world: Optional[AudioWorld] = None
        self._voice_counter: int = 0
        self._command_counter: int = 0

    # --------------------------------------------------------------------------
    # 1. World Lifecycle
    # --------------------------------------------------------------------------

    def create_world(
        self,
        audio_world_id: str,
        runtime_world_id: str = "",
        settings: Optional[AudioWorldSettings] = None,
    ) -> AudioWorld:
        if not audio_world_id or not audio_world_id.strip():
            raise ValueError("INVALID_AUDIO_WORLD_ID: World ID cannot be empty.")
        if audio_world_id in self.worlds:
            raise ValueError(f"DUPLICATE_AUDIO_WORLD_ID: World '{audio_world_id}' already exists.")

        world = AudioWorld(
            audio_world_id=audio_world_id,
            runtime_world_id=runtime_world_id,
            state=AudioWorldState.CREATED,
            settings=settings or AudioWorldSettings(),
        )
        # Setup standard default buses
        master_bus = AudioBus(bus_id="MASTER")
        sfx_bus = AudioBus(bus_id="SFX", parent_bus_id="MASTER")
        music_bus = AudioBus(bus_id="MUSIC", parent_bus_id="MASTER")
        voice_bus = AudioBus(bus_id="VOICE", parent_bus_id="MASTER")
        ambient_bus = AudioBus(bus_id="AMBIENCE", parent_bus_id="MASTER")
        world.mixer.buses["MASTER"] = master_bus
        world.mixer.buses["SFX"] = sfx_bus
        world.mixer.buses["MUSIC"] = music_bus
        world.mixer.buses["VOICE"] = voice_bus
        world.mixer.buses["AMBIENCE"] = ambient_bus

        self.worlds[audio_world_id] = world
        self.active_world = world
        return world

    create_audio_world = create_world

    def get_world(self, audio_world_id: str) -> Optional[AudioWorld]:
        return self.worlds.get(audio_world_id)

    def initialize_world(self, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (AudioWorldState.CREATED, AudioWorldState.INITIALIZING, AudioWorldState.STOPPED):
            raise ValueError(f"NO_INVALID_AUDIO_WORLD_TRANSITION: Cannot initialize from '{target.state.value}'.")

        target.state = AudioWorldState.READY
        target.content_fingerprint = target.compute_fingerprint()

    def start_playback(self, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (AudioWorldState.READY, AudioWorldState.PAUSED, AudioWorldState.STOPPED):
            raise ValueError(f"NO_INVALID_AUDIO_WORLD_TRANSITION: Cannot start playback from '{target.state.value}'.")

        target.state = AudioWorldState.PLAYING

    def pause_playback(self, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state != AudioWorldState.PLAYING:
            raise ValueError(f"NO_INVALID_AUDIO_WORLD_TRANSITION: Cannot pause from '{target.state.value}'.")

        target.state = AudioWorldState.PAUSED

    def stop_playback(self, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (AudioWorldState.PLAYING, AudioWorldState.PAUSED):
            raise ValueError(f"NO_INVALID_AUDIO_WORLD_TRANSITION: Cannot stop from '{target.state.value}'.")

        target.mixer.active_voices.clear()
        for src in target.sources.values():
            src.state = AudioSourceState.STOPPED
        target.state = AudioWorldState.STOPPED

    def advance_state(self, world_id_or_world: Any, new_state: AudioWorldState) -> None:
        if isinstance(world_id_or_world, str):
            target = self.worlds.get(world_id_or_world)
        else:
            target = world_id_or_world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.state = new_state

    def destroy_world(self, world_or_id: Optional[Union[AudioWorld, str]] = None) -> None:
        if isinstance(world_or_id, str):
            target = self.worlds.get(world_or_id)
            if not target:
                raise ValueError(f"WORLD_NOT_FOUND: '{world_or_id}'")
            del self.worlds[world_or_id]
        else:
            target = world_or_id or self.active_world
            if target and target.audio_world_id in self.worlds:
                del self.worlds[target.audio_world_id]

        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        target.sources.clear()
        target.listeners.clear()
        target.clips.clear()
        target.streams.clear()
        target.devices.clear()
        target.mixer.buses.clear()
        target.mixer.active_voices.clear()
        target.command_queue.clear()
        target.events.clear()
        target.state = AudioWorldState.DESTROYED
        if self.active_world is target:
            self.active_world = None

    def reset(self) -> None:
        self.worlds.clear()
        self.active_world = None
        self._voice_counter = 0
        self._command_counter = 0

    # --------------------------------------------------------------------------
    # 2. Device Management
    # --------------------------------------------------------------------------

    def create_device(
        self,
        device_id: str,
        sample_rate: int = 44100,
        channel_count: int = 2,
        format: str = "FLOAT32",
        world: Optional[AudioWorld] = None,
    ) -> AudioDevice:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not device_id or not device_id.strip():
            raise ValueError("INVALID_DEVICE_ID")
        if sample_rate <= 0:
            raise ValueError(f"INVALID_SAMPLE_RATE: {sample_rate}")
        if channel_count <= 0:
            raise ValueError(f"INVALID_CHANNEL_COUNT: {channel_count}")

        dev = AudioDevice(
            device_id=device_id,
            sample_rate=sample_rate,
            channel_count=channel_count,
            format=format,
            state=AudioDeviceState.READY,
        )
        target.devices[device_id] = dev
        if not target.active_device_id:
            target.active_device_id = device_id
        return dev

    def set_active_device(self, device_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        target.active_device_id = device_id

    def handle_device_loss(self, device_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        dev = target.devices[device_id]
        dev.state = AudioDeviceState.LOST
        target.state = AudioWorldState.DEVICE_LOST
        self.emit_event(AudioEventType.DEVICE_LOST, payload={"device_id": device_id}, world=target)

    def recover_device(self, device_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        dev = target.devices[device_id]
        dev.state = AudioDeviceState.READY
        target.state = AudioWorldState.READY
        self.emit_event(AudioEventType.DEVICE_RECOVERED, payload={"device_id": device_id}, world=target)

    def shutdown_device(self, device_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        target.devices[device_id].state = AudioDeviceState.STOPPED
        if target.active_device_id == device_id:
            target.active_device_id = None

    # --------------------------------------------------------------------------
    # 3. Clip and Stream Management
    # --------------------------------------------------------------------------

    def register_clip(self, clip: AudioClip, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.clips) >= target.settings.max_clips:
            raise ValueError("SECURITY_VIOLATION: Max clips exceeded.")
        if clip.duration_seconds <= 0.0:
            raise ValueError("INVALID_CLIP_DURATION: Duration must be > 0.")
        if clip.sample_rate <= 0:
            raise ValueError("INVALID_SAMPLE_RATE: Sample rate must be > 0.")
        if clip.channels <= 0:
            raise ValueError("INVALID_CHANNELS: Channel count must be > 0.")
        if clip.loop_mode == LoopMode.LOOP_REGION and (clip.loop_start < 0 or clip.loop_end > clip.duration_seconds or clip.loop_start >= clip.loop_end):
            raise ValueError("INVALID_LOOP_RANGE: Loop points out of valid clip bounds.")

        target.clips[clip.clip_id] = clip

    def destroy_clip(self, clip_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or clip_id not in target.clips:
            raise ValueError(f"CLIP_NOT_FOUND: '{clip_id}'")
        # Check active voices using this clip
        active = [v for v in target.mixer.active_voices.values() if v.clip_id == clip_id]
        if active:
            raise ValueError(f"RESOURCE_IN_USE: Clip '{clip_id}' is in use by active voices.")
        del target.clips[clip_id]

    def open_stream(self, stream_id: str, buffer_size_bytes: int = 65536, world: Optional[AudioWorld] = None) -> AudioStream:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.streams) >= target.settings.max_streams:
            raise ValueError("SECURITY_VIOLATION: Max streams exceeded.")
        if buffer_size_bytes <= 0:
            raise ValueError("INVALID_BUFFER_SIZE: buffer_size_bytes must be > 0.")

        stream = AudioStream(
            stream_id=stream_id,
            buffer_size_bytes=buffer_size_bytes,
            is_open=True,
        )
        target.streams[stream_id] = stream
        return stream

    def buffer_stream(self, stream_id: str, bytes_count: int, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or stream_id not in target.streams:
            raise ValueError(f"STREAM_NOT_FOUND: '{stream_id}'")
        s = target.streams[stream_id]
        if s.bytes_buffered + bytes_count > target.settings.max_stream_memory_bytes:
            raise ValueError("SECURITY_VIOLATION: Stream memory limit exceeded.")
        s.bytes_buffered += bytes_count

    def decode_stream(self, stream_id: str, world: Optional[AudioWorld] = None) -> bool:
        target = world or self.active_world
        if not target or stream_id not in target.streams:
            raise ValueError(f"STREAM_NOT_FOUND: '{stream_id}'")
        s = target.streams[stream_id]
        if s.bytes_buffered <= 0:
            s.is_exhausted = True
            return False
        # Consumes buffered bytes
        consumed = min(s.bytes_buffered, s.buffer_size_bytes)
        s.bytes_buffered -= consumed
        return True

    def refill_stream(self, stream_id: str, bytes_count: int, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or stream_id not in target.streams:
            raise ValueError(f"STREAM_NOT_FOUND: '{stream_id}'")
        s = target.streams[stream_id]
        s.bytes_buffered += bytes_count
        s.is_exhausted = False

    def close_stream(self, stream_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or stream_id not in target.streams:
            raise ValueError(f"STREAM_NOT_FOUND: '{stream_id}'")
        target.streams[stream_id].is_open = False
        del target.streams[stream_id]

    # --------------------------------------------------------------------------
    # 4. Source and Listener Management
    # --------------------------------------------------------------------------

    def create_source(
        self,
        source_id: str,
        entity_id: str = "",
        clip_id: str = "",
        stream_id: str = "",
        position: Optional[List[float]] = None,
        velocity: Optional[List[float]] = None,
        volume: float = 1.0,
        pitch: float = 1.0,
        min_distance: float = 1.0,
        max_distance: float = 100.0,
        distance_model: AudioDistanceModel = AudioDistanceModel.INVERSE,
        bus_id: str = "SFX",
        spatialized: bool = True,
        loop: bool = False,
        priority: int = 128,
        world: Optional[AudioWorld] = None,
    ) -> AudioSource:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not source_id or not source_id.strip():
            raise ValueError("INVALID_SOURCE_ID")
        if source_id in target.sources:
            raise ValueError(f"DUPLICATE_SOURCE_ID: '{source_id}'")
        if len(target.sources) >= target.settings.max_sources:
            raise ValueError("SECURITY_VIOLATION: Max sources exceeded.")
        if volume < 0.0:
            raise ValueError(f"INVALID_VOLUME: {volume}")
        if pitch <= 0.0:
            raise ValueError(f"INVALID_PITCH: {pitch}")
        if min_distance < 0.0 or max_distance <= min_distance:
            raise ValueError(f"INVALID_DISTANCE_RANGE: {min_distance} -> {max_distance}")
        if bus_id and bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: Bus '{bus_id}' not found in AudioWorld.")

        src = AudioSource(
            source_id=source_id,
            entity_id=entity_id,
            clip_id=clip_id,
            stream_id=stream_id,
            position=position or [0.0, 0.0, 0.0],
            velocity=velocity or [0.0, 0.0, 0.0],
            volume=volume,
            pitch=pitch,
            min_distance=min_distance,
            max_distance=max_distance,
            distance_model=distance_model,
            bus_id=bus_id,
            spatialized=spatialized,
            loop=loop,
            priority=priority,
            state=AudioSourceState.STOPPED,
        )
        target.sources[source_id] = src
        return src

    def destroy_source(self, source_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")

        # Stop active voice if running
        self.stop_source(source_id, world=target)
        del target.sources[source_id]

    def create_listener(
        self,
        listener_id: str,
        entity_id: str = "",
        position: Optional[List[float]] = None,
        velocity: Optional[List[float]] = None,
        forward: Optional[List[float]] = None,
        up: Optional[List[float]] = None,
        gain: float = 1.0,
        world: Optional[AudioWorld] = None,
    ) -> AudioListener:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not listener_id or not listener_id.strip():
            raise ValueError("INVALID_LISTENER_ID")
        if gain < 0.0:
            raise ValueError(f"INVALID_GAIN: {gain}")

        listener = AudioListener(
            listener_id=listener_id,
            entity_id=entity_id,
            position=position or [0.0, 0.0, 0.0],
            velocity=velocity or [0.0, 0.0, 0.0],
            forward=_vec3_norm(forward or [0.0, 0.0, 1.0]),
            up=_vec3_norm(up or [0.0, 1.0, 0.0]),
            gain=gain,
        )
        target.listeners[listener_id] = listener
        if not target.active_listener_id:
            target.active_listener_id = listener_id
        return listener

    def set_active_listener(self, listener_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or listener_id not in target.listeners:
            raise ValueError(f"LISTENER_NOT_FOUND: '{listener_id}'")
        target.active_listener_id = listener_id

    def destroy_listener(self, listener_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or listener_id not in target.listeners:
            raise ValueError(f"LISTENER_NOT_FOUND: '{listener_id}'")
        del target.listeners[listener_id]
        if target.active_listener_id == listener_id:
            target.active_listener_id = next(iter(target.listeners.keys()), None)

    # --------------------------------------------------------------------------
    # 5. Playback and Voice Control
    # --------------------------------------------------------------------------

    def play_source(self, source_id: str, world: Optional[AudioWorld] = None) -> AudioVoice:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")

        src = target.sources[source_id]
        if not src.clip_id and not src.stream_id:
            raise ValueError(f"NO_RESOURCE: NO_PLAY_WITHOUT_VALID_AUDIO_RESOURCE - Source '{source_id}' has no clip or stream.")
        if src.clip_id and src.clip_id not in target.clips:
            raise ValueError(f"NO_RESOURCE: NO_PLAY_WITHOUT_VALID_AUDIO_RESOURCE - Clip '{src.clip_id}' missing.")
        if src.stream_id and src.stream_id not in target.streams:
            raise ValueError(f"NO_RESOURCE: NO_PLAY_WITHOUT_VALID_AUDIO_RESOURCE - Stream '{src.stream_id}' missing.")

        # Check existing voice for this source
        for vid, v in list(target.mixer.active_voices.items()):
            if v.source_id == source_id:
                v.state = VoiceState.PLAYING
                src.state = AudioSourceState.PLAYING
                return v

        # Check Voice Budget & Stealing
        budget = getattr(target.mixer, "max_voices", None) or target.settings.max_voices
        if len(target.mixer.active_voices) >= budget:
            stolen = self._steal_voice(src.priority, target)
            if not stolen:
                raise ValueError("VOICE_BUDGET_EXHAUSTED: Max voices exceeded and no voice could be stolen.")

        self._voice_counter += 1
        voice_id = f"voice_{self._voice_counter}"

        # Calculate initial spatialization & doppler
        gain, pitch, pan = self.compute_voice_parameters(source_id, target)

        voice = AudioVoice(
            voice_id=voice_id,
            source_id=source_id,
            clip_id=src.clip_id,
            priority=src.priority,
            playback_time=src.playback_position,
            state=VoiceState.PLAYING,
            computed_gain=gain,
            computed_pitch=pitch,
            panning=pan,
            creation_order=self._voice_counter,
        )
        target.mixer.active_voices[voice_id] = voice
        src.state = AudioSourceState.PLAYING
        self.emit_event(AudioEventType.PLAY_STARTED, source_id=source_id, world=target)
        return voice

    def pause_source(self, source_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")
        src = target.sources[source_id]
        src.state = AudioSourceState.PAUSED
        for v in target.mixer.active_voices.values():
            if v.source_id == source_id:
                v.state = VoiceState.PAUSED
                src.playback_position = v.playback_time
        self.emit_event(AudioEventType.PLAY_PAUSED, source_id=source_id, world=target)

    def resume_source(self, source_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")
        src = target.sources[source_id]
        if src.state == AudioSourceState.PAUSED:
            src.state = AudioSourceState.PLAYING
            for v in target.mixer.active_voices.values():
                if v.source_id == source_id:
                    v.state = VoiceState.PLAYING
            self.emit_event(AudioEventType.PLAY_RESUMED, source_id=source_id, world=target)

    def stop_source(self, source_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")
        src = target.sources[source_id]
        src.state = AudioSourceState.STOPPED
        src.playback_position = 0.0

        for vid in list(target.mixer.active_voices.keys()):
            if target.mixer.active_voices[vid].source_id == source_id:
                del target.mixer.active_voices[vid]

        self.emit_event(AudioEventType.PLAY_STOPPED, source_id=source_id, world=target)

    def seek_source(self, source_id: str, position_seconds: float, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")
        src = target.sources[source_id]
        clip = target.clips.get(src.clip_id)
        max_dur = clip.duration_seconds if clip else 1000.0
        pos = max(0.0, min(position_seconds, max_dur))
        src.playback_position = pos
        for v in target.mixer.active_voices.values():
            if v.source_id == source_id:
                v.playback_time = pos

    def set_source_volume(self, source_id: str, volume: float, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")
        if volume < 0.0:
            raise ValueError("INVALID_VOLUME: Volume cannot be negative.")
        target.sources[source_id].volume = volume

    def set_source_pitch(self, source_id: str, pitch: float, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")
        if pitch <= 0.0:
            raise ValueError("INVALID_PITCH: Pitch must be positive.")
        target.sources[source_id].pitch = pitch

    def _steal_voice(self, incoming_priority: int, world: AudioWorld) -> bool:
        policy = getattr(world.mixer, "stealing_policy", None) or world.settings.voice_stealing_policy
        if policy == VoiceStealingPolicy.REJECT:
            return False

        voices = list(world.mixer.active_voices.values())
        if not voices:
            return False

        target_voice = None
        if policy == VoiceStealingPolicy.STEAL_LOWEST_PRIORITY:
            # Deterministic: lowest priority, then oldest creation_order
            candidates = sorted(voices, key=lambda v: (v.priority, v.creation_order))
            if candidates[0].priority <= incoming_priority:
                target_voice = candidates[0]
        elif policy == VoiceStealingPolicy.STEAL_OLDEST:
            candidates = sorted(voices, key=lambda v: (v.creation_order, v.priority))
            target_voice = candidates[0]
        elif policy == VoiceStealingPolicy.STEAL_QUIETEST:
            candidates = sorted(voices, key=lambda v: (v.computed_gain, v.priority))
            target_voice = candidates[0]
        else:
            target_voice = voices[0]

        if target_voice:
            del world.mixer.active_voices[target_voice.voice_id]
            self.emit_event(AudioEventType.VOICE_STOLEN, source_id=target_voice.source_id, world=world)
            return True
        return False

    # --------------------------------------------------------------------------
    # 6. 3D Spatialization, Attenuation & Doppler
    # --------------------------------------------------------------------------

    def compute_spatial_distance(self, source_id: str, listener_id: Optional[str] = None, world: Optional[AudioWorld] = None) -> float:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            return 0.0
        lid = listener_id or target.active_listener_id
        if not lid or lid not in target.listeners:
            return 0.0
        s = target.sources[source_id]
        l = target.listeners[lid]
        return _vec3_dist(s.position, l.position)

    def compute_attenuation(self, source_id: str, listener_id: Optional[str] = None, world: Optional[AudioWorld] = None) -> float:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            return 1.0
        src = target.sources[source_id]
        if not src.spatialized:
            return 1.0

        r = self.compute_spatial_distance(source_id, listener_id, target)
        r_min = src.min_distance
        r_max = src.max_distance
        if r <= r_min:
            return 1.0
        if r >= r_max:
            return 0.0

        model = src.distance_model
        if model == AudioDistanceModel.LINEAR:
            att = 1.0 - (r - r_min) / (r_max - r_min)
        elif model == AudioDistanceModel.EXPONENTIAL:
            att = (r / r_min) ** (-src.rolloff_factor)
        elif model == AudioDistanceModel.LOGARITHMIC:
            att = 1.0 - src.rolloff_factor * math.log10(max(1.0, r / r_min))
        else:  # INVERSE default
            att = r_min / (r_min + src.rolloff_factor * (r - r_min))

        return max(0.0, min(1.0, att))

    def compute_doppler(self, source_id: str, listener_id: Optional[str] = None, world: Optional[AudioWorld] = None) -> float:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            return 1.0
        src = target.sources[source_id]
        lid = listener_id or target.active_listener_id
        if not lid or lid not in target.listeners:
            return 1.0
        lis = target.listeners[lid]

        disp = [lis.position[0] - src.position[0], lis.position[1] - src.position[1], lis.position[2] - src.position[2]]
        r = math.sqrt(disp[0] ** 2 + disp[1] ** 2 + disp[2] ** 2)
        if r < 1e-6:
            return 1.0

        d_unit = [disp[0] / r, disp[1] / r, disp[2] / r]
        v_s = _vec3_dot(src.velocity, d_unit)
        v_l = _vec3_dot(lis.velocity, d_unit)

        c = target.settings.speed_of_sound
        # Clamp velocity to avoid division by zero or negative Doppler shift
        v_s_clamped = min(v_s, c * 0.95)
        scale = target.settings.doppler_scale

        ratio = (c - scale * v_l) / (c - scale * v_s_clamped)
        ratio_clamped = max(target.settings.doppler_min_pitch, min(ratio, target.settings.doppler_max_pitch))
        return ratio_clamped

    def compute_voice_parameters(self, source_id: str, world: AudioWorld) -> Tuple[float, float, float]:
        src = world.sources[source_id]
        att = self.compute_attenuation(source_id, world=world) if src.spatialized else 1.0
        doppler = self.compute_doppler(source_id, world=world) if src.spatialized else 1.0
        gain = src.volume * att
        pitch = src.pitch * doppler

        pan = 0.0
        lid = world.active_listener_id
        if src.spatialized and lid and lid in world.listeners:
            lis = world.listeners[lid]
            disp = [src.position[0] - lis.position[0], src.position[1] - lis.position[1], src.position[2] - lis.position[2]]
            right = _vec3_cross(lis.up, lis.forward)
            r = math.sqrt(disp[0] ** 2 + disp[1] ** 2 + disp[2] ** 2)
            if r > 1e-6:
                d_unit = [disp[0] / r, disp[1] / r, disp[2] / r]
                pan = max(-1.0, min(1.0, _vec3_dot(d_unit, right)))

        return round(gain, 6), round(pitch, 6), round(pan, 6)

    # --------------------------------------------------------------------------
    # 7. Bus, Mixing & Effects
    # --------------------------------------------------------------------------

    def create_bus(self, bus_id: str, parent_bus_id: Optional[str] = "MASTER", volume: float = 1.0, world: Optional[AudioWorld] = None) -> AudioBus:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not bus_id or not bus_id.strip():
            raise ValueError("INVALID_BUS_ID")
        if bus_id in target.mixer.buses:
            raise ValueError(f"DUPLICATE_BUS_ID: '{bus_id}'")
        if len(target.mixer.buses) >= target.settings.max_buses:
            raise ValueError("SECURITY_VIOLATION: Max buses exceeded.")
        if volume < 0.0:
            raise ValueError("INVALID_VOLUME: Bus volume cannot be negative.")

        bus = AudioBus(bus_id=bus_id, parent_bus_id=parent_bus_id, volume=volume)
        target.mixer.buses[bus_id] = bus
        return bus

    def set_bus_volume(self, bus_id: str, volume: float, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        if volume < 0.0:
            raise ValueError("INVALID_VOLUME: Bus volume cannot be negative.")
        target.mixer.buses[bus_id].volume = volume

    def set_bus_mute(self, bus_id: str, is_muted: bool, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        target.mixer.buses[bus_id].is_muted = is_muted

    def set_bus_solo(self, bus_id: str, is_solo: bool, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        target.mixer.buses[bus_id].is_solo = is_solo

    def set_bus_ducking(self, bus_id: str, ducking_factor: float, target_bus_id: Optional[str] = None, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        target.mixer.buses[bus_id].ducking_factor = ducking_factor
        target.mixer.buses[bus_id].duck_target_bus_id = target_bus_id

    def route_source_to_bus(self, source_id: str, bus_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or source_id not in target.sources:
            raise ValueError(f"SOURCE_NOT_FOUND: '{source_id}'")
        if bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        target.sources[source_id].bus_id = bus_id

    def add_effect_to_bus(self, bus_id: str, effect: AudioEffect, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        target.mixer.buses[bus_id].effects.append(effect)

    def destroy_bus(self, bus_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        # Reroute sources that were on this bus
        for src in target.sources.values():
            if src.bus_id == bus_id:
                src.bus_id = "MASTER"
        del target.mixer.buses[bus_id]

    def compute_bus_effective_volume(self, bus_id: str, world: AudioWorld) -> float:
        bus = world.mixer.buses.get(bus_id)
        if not bus:
            return 0.0

        # Check solo mode
        any_solo = any(b.is_solo for b in world.mixer.buses.values())
        if any_solo:
            if not bus.is_solo:
                # Check if bus has any solo descendant
                def has_solo_desc(bid: str) -> bool:
                    for b in world.mixer.buses.values():
                        if b.parent_bus_id == bid:
                            if b.is_solo or has_solo_desc(b.bus_id):
                                return True
                    return False
                if not has_solo_desc(bus_id):
                    return 0.0

        if bus.is_muted:
            return 0.0

        vol = bus.volume * bus.ducking_factor
        if bus.parent_bus_id and bus.parent_bus_id in world.mixer.buses:
            vol *= self.compute_bus_effective_volume(bus.parent_bus_id, world)
        return vol

    def mix_frame(self, world: Optional[AudioWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        bus_levels: Dict[str, float] = {}
        for bid in target.mixer.buses:
            bus_levels[bid] = self.compute_bus_effective_volume(bid, target)

        voice_outputs: Dict[str, float] = {}
        for vid, voice in target.mixer.active_voices.items():
            if voice.state != VoiceState.PLAYING:
                continue
            src = target.sources.get(voice.source_id)
            bus_id = src.bus_id if src else "MASTER"
            bus_vol = bus_levels.get(bus_id, 1.0)
            voice_outputs[vid] = round(voice.computed_gain * bus_vol * target.settings.master_volume, 6)

        return {
            "bus_levels": bus_levels,
            "voice_outputs": voice_outputs,
            "total_active": len(voice_outputs),
        }

    # --------------------------------------------------------------------------
    # 8. Command Queue and Events
    # --------------------------------------------------------------------------

    def enqueue_command(self, command: AudioCommand, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.command_queue) >= target.settings.max_commands:
            raise ValueError("SECURITY_VIOLATION: Command queue overflow.")
        target.command_queue.append(command)

    def process_commands(self, world: Optional[AudioWorld] = None) -> int:
        target = world or self.active_world
        if not target:
            return 0
        count = len(target.command_queue)
        for cmd in target.command_queue:
            if cmd.command_type == AudioCommandType.PLAY:
                if cmd.target_id in target.sources:
                    self.play_source(cmd.target_id, target)
            elif cmd.command_type == AudioCommandType.PAUSE:
                if cmd.target_id in target.sources:
                    self.pause_source(cmd.target_id, target)
            elif cmd.command_type == AudioCommandType.RESUME:
                if cmd.target_id in target.sources:
                    self.resume_source(cmd.target_id, target)
            elif cmd.command_type == AudioCommandType.STOP:
                if cmd.target_id in target.sources:
                    self.stop_source(cmd.target_id, target)
            elif cmd.command_type == AudioCommandType.SEEK:
                pos = cmd.parameters.get("position", 0.0)
                if cmd.target_id in target.sources:
                    self.seek_source(cmd.target_id, pos, target)
            elif cmd.command_type == AudioCommandType.SET_VOLUME:
                vol = cmd.parameters.get("volume", 1.0)
                if cmd.target_id in target.sources:
                    self.set_source_volume(cmd.target_id, vol, target)
            elif cmd.command_type == AudioCommandType.SET_PITCH:
                pitch = cmd.parameters.get("pitch", 1.0)
                if cmd.target_id in target.sources:
                    self.set_source_pitch(cmd.target_id, pitch, target)
            elif cmd.command_type == AudioCommandType.SET_POSITION:
                pos = cmd.parameters.get("position", [0.0, 0.0, 0.0])
                if cmd.target_id in target.sources:
                    target.sources[cmd.target_id].position = list(pos)
            elif cmd.command_type == AudioCommandType.SET_VELOCITY:
                vel = cmd.parameters.get("velocity", [0.0, 0.0, 0.0])
                if cmd.target_id in target.sources:
                    target.sources[cmd.target_id].velocity = list(vel)
            elif cmd.command_type == AudioCommandType.SET_BUS:
                bus_id = cmd.parameters.get("bus_id", "MASTER")
                if cmd.target_id in target.sources:
                    self.route_source_to_bus(cmd.target_id, bus_id, target)
            elif cmd.command_type == AudioCommandType.SET_EFFECT_PARAMETER:
                pass
        target.command_queue.clear()
        return count

    def emit_event(
        self,
        event_type: AudioEventType,
        source_id: str = "",
        payload: Optional[Dict[str, Any]] = None,
        world: Optional[AudioWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target:
            return

        # Deduplication check for this tick/frame
        for ev in target.events:
            if ev.event_type == event_type and ev.source_id == source_id and ev.timestamp == target.time_seconds:
                return

        event = AudioEvent(
            event_id=f"ev_{len(target.events) + 1}",
            event_type=event_type,
            source_id=source_id,
            payload=payload or {},
            timestamp=target.time_seconds,
        )
        target.events.append(event)

    # --------------------------------------------------------------------------
    # 9. Frame Stepping and Transform Synchronization
    # --------------------------------------------------------------------------

    def update(self, delta_time: float, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state == AudioWorldState.PAUSED:
            return
        if target.state not in (AudioWorldState.PLAYING, AudioWorldState.READY):
            raise ValueError(f"NO_UPDATE_BEFORE_INITIALIZATION: AudioWorld state is '{target.state.value}'.")

        if delta_time < 0.0:
            raise ValueError("INVALID_TIMESTEP: delta_time cannot be negative.")

        self.process_commands(target)
        target.time_seconds += delta_time
        target.frames_rendered += 1

        # Advance voices
        to_stop = []
        for vid, voice in list(target.mixer.active_voices.items()):
            if voice.state != VoiceState.PLAYING:
                continue

            # Update voice parameters
            gain, pitch, pan = self.compute_voice_parameters(voice.source_id, target)
            voice.computed_gain = gain
            voice.computed_pitch = pitch
            voice.panning = pan

            voice.playback_time += delta_time * voice.computed_pitch
            clip = target.clips.get(voice.clip_id)
            if clip:
                if clip.loop_mode == LoopMode.LOOP or target.sources[voice.source_id].loop:
                    if voice.playback_time >= clip.duration_seconds:
                        voice.playback_time %= max(1e-6, clip.duration_seconds)
                elif clip.loop_mode == LoopMode.LOOP_REGION:
                    if voice.playback_time >= clip.loop_end:
                        span = max(1e-6, clip.loop_end - clip.loop_start)
                        voice.playback_time = clip.loop_start + (voice.playback_time - clip.loop_end) % span
                else:
                    if voice.playback_time >= clip.duration_seconds:
                        to_stop.append(voice)

        for v in to_stop:
            self.stop_source(v.source_id, target)
            self.emit_event(AudioEventType.PLAY_FINISHED, source_id=v.source_id, world=target)

        target.content_fingerprint = target.compute_fingerprint()

    def sync_from_runtime_world(self, runtime_world: Any, audio_world: Optional[AudioWorld] = None) -> None:
        target = audio_world or self.active_world
        if not target or not runtime_world:
            return

        for src in target.sources.values():
            if src.entity_id in runtime_world.entities:
                ent = runtime_world.entities[src.entity_id]
                tr = getattr(ent, "world_transform", getattr(ent, "transform", None))
                if tr:
                    src.position = list(tr.position)
                vel = getattr(ent, "linear_velocity", getattr(ent, "velocity", None))
                if vel:
                    src.velocity = list(vel)

        for lis in target.listeners.values():
            if lis.entity_id in runtime_world.entities:
                ent = runtime_world.entities[lis.entity_id]
                tr = getattr(ent, "world_transform", getattr(ent, "transform", None))
                if tr:
                    lis.position = list(tr.position)
                vel = getattr(ent, "linear_velocity", getattr(ent, "velocity", None))
                if vel:
                    lis.velocity = list(vel)

    # --------------------------------------------------------------------------
    # 10. Snapshots, Replay and Determinism
    # --------------------------------------------------------------------------

    def capture_snapshot(self, world: Optional[AudioWorld] = None) -> AudioSnapshot:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        sources_data = {k: v.to_dict() for k, v in sorted(target.sources.items())}
        voices_data = {k: v.to_dict() for k, v in sorted(target.mixer.active_voices.items())}
        buses_data = {k: v.to_dict() for k, v in sorted(target.mixer.buses.items())}

        serialized = json.dumps({"s": sources_data, "v": voices_data, "b": buses_data}, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        return AudioSnapshot(
            snapshot_id=f"snap_{int(target.time_seconds * 1000)}",
            world_id=target.audio_world_id,
            timestamp=target.time_seconds,
            sources=sources_data,
            voices=voices_data,
            buses=buses_data,
            snapshot_hash=h,
        )

    def restore_snapshot(self, snapshot: AudioSnapshot, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        # Validate hash
        serialized = json.dumps({"s": snapshot.sources, "v": snapshot.voices, "b": snapshot.buses}, sort_keys=True)
        if hashlib.sha256(serialized.encode("utf-8")).hexdigest() != snapshot.snapshot_hash:
            raise ValueError("SNAPSHOT_VALIDATION_FAILED: Snapshot hash mismatch.")

        target.time_seconds = snapshot.timestamp
        # Restore active voices
        target.mixer.active_voices.clear()
        for vid, vdata in snapshot.voices.items():
            target.mixer.active_voices[vid] = AudioVoice(
                voice_id=vid,
                source_id=vdata["source_id"],
                clip_id=vdata["clip_id"],
                priority=vdata["priority"],
                playback_time=vdata["playback_time"],
                state=VoiceState(vdata["state"]),
                computed_gain=vdata["computed_gain"],
                computed_pitch=vdata["computed_pitch"],
                panning=vdata["panning"],
                creation_order=vdata["creation_order"],
            )

        # Restore source states and positions
        for sid, sdata in snapshot.sources.items():
            if sid in target.sources:
                target.sources[sid].state = AudioSourceState(sdata["state"])
                target.sources[sid].playback_position = sdata["playback_position"]
                target.sources[sid].volume = sdata["volume"]
                target.sources[sid].pitch = sdata["pitch"]

    def execute_replay(self, replay: AudioReplay, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        for cmd in sorted(replay.commands, key=lambda c: c.timestamp):
            try:
                if cmd.command_type == "PLAY":
                    self.play_source(cmd.target_id, target)
                elif cmd.command_type == "PAUSE":
                    self.pause_source(cmd.target_id, target)
                elif cmd.command_type == "STOP":
                    self.stop_source(cmd.target_id, target)
                elif cmd.command_type == "SEEK":
                    self.seek_source(cmd.target_id, cmd.params.get("position", 0.0), target)
                elif cmd.command_type == "SET_VOLUME":
                    self.set_source_volume(cmd.target_id, cmd.params.get("volume", 1.0), target)
                elif cmd.command_type == "SET_PITCH":
                    self.set_source_pitch(cmd.target_id, cmd.params.get("pitch", 1.0), target)
            except ValueError:
                pass
        replay.is_finished = True

    def capture_golden_audio(self, world: Optional[AudioWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        data = {
            "world_id": target.audio_world_id,
            "frames": target.frames_rendered,
            "sources_count": len(target.sources),
            "voices_count": len(target.mixer.active_voices),
            "clips_count": len(target.clips),
            "streams_count": len(target.streams),
            "buses_count": len(target.mixer.buses),
            "mix": self.mix_frame(target),
        }
        serialized = json.dumps(data, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        data["golden_hash"] = h
        return data

    def get_debug_audio_data(self, world: Optional[AudioWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        return {
            "world_id": target.audio_world_id,
            "state": target.state.value,
            "active_voices": len(target.mixer.active_voices),
            "sources": list(target.sources.keys()),
            "active_listener": target.active_listener_id,
            "buses": list(target.mixer.buses.keys()),
            "time_seconds": target.time_seconds,
        }

    def create_stream(self, stream_id: str, buffer_size: int = 65536, buffer_size_bytes: int = 65536, world: Optional[AudioWorld] = None) -> AudioStream:
        size = buffer_size if buffer_size != 65536 else buffer_size_bytes
        return self.open_stream(stream_id, size, world)

    def push_stream_data(self, stream_id: str, data: bytes, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or stream_id not in target.streams:
            raise ValueError(f"STREAM_NOT_FOUND: '{stream_id}'")
        s = target.streams[stream_id]
        s.bytes_buffered = min(s.buffer_size_bytes, s.bytes_buffered + len(data))

    def get_bus(self, bus_id: str, world: Optional[AudioWorld] = None) -> AudioBus:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        return target.mixer.buses[bus_id]

    def destroy_bus(self, bus_id: str, world: Optional[AudioWorld] = None) -> None:
        target = world or self.active_world
        if not target or bus_id not in target.mixer.buses:
            raise ValueError(f"BUS_NOT_FOUND: '{bus_id}'")
        if bus_id == "MASTER":
            raise ValueError("CANNOT_DESTROY_MASTER_BUS")
        del target.mixer.buses[bus_id]
        for src in target.sources.values():
            if src.bus_id == bus_id:
                src.bus_id = "MASTER"
        for b in target.mixer.buses.values():
            if b.parent_bus_id == bus_id:
                b.parent_bus_id = "MASTER"

    def queue_command(
        self,
        command_type: AudioCommandType,
        target_id: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        timestamp: float = 0.0,
        world: Optional[AudioWorld] = None,
    ) -> AudioCommand:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        cmd_id = f"cmd_{len(target.command_queue) + 1}"
        cmd = AudioCommand(
            command_id=cmd_id,
            command_type=command_type,
            target_id=target_id,
            parameters=parameters or {},
            timestamp=timestamp,
        )
        self.enqueue_command(cmd, target)
        return cmd

    def compute_doppler_factor(self, src: Any, lis: Any, world: Optional[AudioWorld] = None) -> float:
        target = world or self.active_world
        c = target.settings.speed_of_sound if target else 343.0
        scale = target.settings.doppler_scale if target else 1.0

        src_pos = src.position if hasattr(src, "position") else [0.0, 0.0, 0.0]
        src_vel = src.velocity if hasattr(src, "velocity") else [0.0, 0.0, 0.0]
        lis_pos = lis.position if hasattr(lis, "position") else [0.0, 0.0, 0.0]
        lis_vel = lis.velocity if hasattr(lis, "velocity") else [0.0, 0.0, 0.0]

        disp = [lis_pos[0] - src_pos[0], lis_pos[1] - src_pos[1], lis_pos[2] - src_pos[2]]
        r = math.sqrt(disp[0] ** 2 + disp[1] ** 2 + disp[2] ** 2)
        if r < 1e-6:
            return 1.0

        d_unit = [disp[0] / r, disp[1] / r, disp[2] / r]
        v_s = _vec3_dot(src_vel, d_unit)
        v_l = _vec3_dot(lis_vel, d_unit)

        v_s_clamped = min(v_s, c * 0.95)
        ratio = (c - scale * v_l) / (c - scale * v_s_clamped)
        min_p = target.settings.doppler_min_pitch if target else 0.1
        max_p = target.settings.doppler_max_pitch if target else 4.0
        return max(min_p, min(ratio, max_p))

    destroy_audio_world = destroy_world
    handle_device_lost = handle_device_loss
    add_bus_effect = add_effect_to_bus
    post_event = emit_event

    def create_effect(
        self,
        effect_id: str,
        effect_type: AudioEffectType,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AudioEffect:
        return AudioEffect(effect_id=effect_id, effect_type=effect_type, parameters=parameters or {})
