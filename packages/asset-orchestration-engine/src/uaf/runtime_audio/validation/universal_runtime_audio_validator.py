"""
Universal Runtime Audio Validator (UAF-81.76).
Normative validation for audio sources, listeners, clips, streams, buses,
effect chains, spatialization invariants, and resource lifetimes.
"""

from __future__ import annotations
from typing import List, Dict, Set, Optional

from ..models.definition import (
    AudioClip,
    AudioStream,
    AudioDevice,
    AudioEffect,
    AudioBus,
    AudioVoice,
    AudioSource,
    AudioListener,
    AudioWorld,
    LoopMode,
)


class AudioValidationIssue(str):
    """A string-compatible validation issue with structured error attributes."""

    error_code: str
    message: str
    severity: str

    def __new__(cls, error_code: str, message: str = "", severity: str = "ERROR"):
        full = f"{severity}: [{error_code}] {message}" if message else error_code
        instance = super().__new__(cls, full)
        instance.error_code = error_code
        instance.message = message or error_code
        instance.severity = severity
        return instance


class UniversalRuntimeAudioValidator:
    """Normative validation of runtime audio world entities, buses and constraints."""

    def validate_clip(self, clip: AudioClip) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        if clip.duration_seconds <= 0.0:
            errors.append(AudioValidationIssue("INVALID_CLIP_DURATION", f"duration_seconds must be > 0 ({clip.duration_seconds})."))
        if clip.sample_rate <= 0:
            errors.append(AudioValidationIssue("INVALID_SAMPLE_RATE", f"sample_rate must be > 0 ({clip.sample_rate})."))
        if clip.channels <= 0:
            errors.append(AudioValidationIssue("INVALID_CHANNELS", f"channels must be > 0 ({clip.channels})."))
        if clip.loop_mode == LoopMode.LOOP_REGION:
            if clip.loop_start < 0.0 or clip.loop_end > clip.duration_seconds or clip.loop_start >= clip.loop_end:
                errors.append(AudioValidationIssue("INVALID_LOOP_RANGE", f"Loop range ({clip.loop_start}, {clip.loop_end}) invalid for duration {clip.duration_seconds}."))
        return errors

    def validate_stream(self, stream: AudioStream) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        if stream.buffer_size_bytes <= 0:
            errors.append(AudioValidationIssue("INVALID_BUFFER_SIZE", f"buffer_size_bytes must be > 0 ({stream.buffer_size_bytes})."))
        return errors

    def validate_device(self, device: AudioDevice) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        if device.sample_rate <= 0:
            errors.append(AudioValidationIssue("INVALID_SAMPLE_RATE", f"sample_rate must be > 0 ({device.sample_rate})."))
        if device.channel_count <= 0:
            errors.append(AudioValidationIssue("INVALID_CHANNELS", f"channel_count must be > 0 ({device.channel_count})."))
        return errors

    def validate_source(self, source: AudioSource, world: Optional[AudioWorld] = None) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        if source.volume < 0.0:
            errors.append(AudioValidationIssue("INVALID_VOLUME", f"volume cannot be negative ({source.volume})."))
        if source.pitch <= 0.0:
            errors.append(AudioValidationIssue("INVALID_PITCH", f"pitch must be positive ({source.pitch})."))
        if source.min_distance <= 0.0:
            errors.append(AudioValidationIssue("INVALID_MIN_DISTANCE", f"min_distance must be > 0 ({source.min_distance})."))
        if source.max_distance <= source.min_distance:
            errors.append(AudioValidationIssue("INVALID_DISTANCE_RANGE", f"max_distance ({source.max_distance}) must be > min_distance ({source.min_distance})."))
        if not (0.0 <= source.cone_inner_angle <= 360.0):
            errors.append(AudioValidationIssue("INVALID_CONE_ANGLE", f"cone_inner_angle ({source.cone_inner_angle}) must be in [0, 360]."))
        if not (source.cone_inner_angle <= source.cone_outer_angle <= 360.0):
            errors.append(AudioValidationIssue("INVALID_CONE_ANGLE", f"cone_outer_angle ({source.cone_outer_angle}) must be in [inner_angle, 360]."))

        if world:
            if source.clip_id and source.clip_id not in world.clips:
                errors.append(AudioValidationIssue("MISSING_CLIP", f"Clip '{source.clip_id}' not found in AudioWorld."))
            if source.bus_id and source.bus_id not in world.mixer.buses:
                errors.append(AudioValidationIssue("MISSING_BUS", f"Bus '{source.bus_id}' not found in AudioWorld."))
        return errors

    def validate_listener(self, listener: AudioListener) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        if listener.gain < 0.0:
            errors.append(AudioValidationIssue("INVALID_GAIN", f"gain cannot be negative ({listener.gain})."))
        f_len = sum(x ** 2 for x in listener.forward)
        if f_len <= 1e-9:
            errors.append(AudioValidationIssue("INVALID_LISTENER_FORWARD", "Listener forward vector cannot be zero."))
        u_len = sum(x ** 2 for x in listener.up)
        if u_len <= 1e-9:
            errors.append(AudioValidationIssue("INVALID_LISTENER_UP", "Listener up vector cannot be zero."))
        return errors

    def validate_bus(self, bus: AudioBus, world: Optional[AudioWorld] = None) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        if bus.volume < 0.0:
            errors.append(AudioValidationIssue("INVALID_VOLUME", f"volume cannot be negative ({bus.volume})."))

        if world and bus.parent_bus_id:
            if bus.parent_bus_id not in world.mixer.buses:
                errors.append(AudioValidationIssue("MISSING_PARENT_BUS", f"Parent bus '{bus.parent_bus_id}' not found."))
            else:
                # Cycle check in bus tree
                visited = {bus.bus_id}
                curr = bus.parent_bus_id
                while curr:
                    if curr in visited:
                        errors.append(AudioValidationIssue("NO_BUS_CYCLE", f"Cycle detected in bus hierarchy at '{curr}'."))
                        break
                    visited.add(curr)
                    p_bus = world.mixer.buses.get(curr)
                    curr = p_bus.parent_bus_id if p_bus else None
        return errors

    def validate_effect(self, effect: AudioEffect) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        if not effect.effect_id or not effect.effect_id.strip():
            errors.append(AudioValidationIssue("EMPTY_EFFECT_ID", "effect_id cannot be empty."))
        return errors

    def validate_world(self, world: AudioWorld) -> List[AudioValidationIssue]:
        errors: List[AudioValidationIssue] = []
        for d in world.devices.values():
            errors.extend(self.validate_device(d))
        for c in world.clips.values():
            errors.extend(self.validate_clip(c))
        for s in world.streams.values():
            errors.extend(self.validate_stream(s))
        for src in world.sources.values():
            errors.extend(self.validate_source(src, world))
        for lis in world.listeners.values():
            errors.extend(self.validate_listener(lis))
        for bus in world.mixer.buses.values():
            errors.extend(self.validate_bus(bus, world))
        return errors

    validate = validate_world
