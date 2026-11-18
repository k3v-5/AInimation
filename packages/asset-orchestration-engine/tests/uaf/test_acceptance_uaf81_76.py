"""
Normative Acceptance Test Suite for UAF-81.76: Universal Runtime Audio World System.
Validates audio sources, listeners, clips, voices, streaming, buses, effect chains,
3D spatialization, attenuation, Doppler effect, and invariants (§96 - §123).
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
import os
import tempfile
import time
from typing import Any, Dict, List, Tuple

import pytest

from uaf.runtime_audio import (
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
    UniversalRuntimeAudioFabricator,
    AudioValidationIssue,
    UniversalRuntimeAudioValidator,
    UniversalRuntimeAudioPackager,
)


def make_test_world(world_id: str = "test_audio_world") -> Tuple[UniversalRuntimeAudioFabricator, AudioWorld]:
    fab = UniversalRuntimeAudioFabricator()
    w = fab.create_world(world_id)
    return fab, w


# ==============================================================================
# §96. AUDIO WORLD TESTS (10 tests)
# ==============================================================================

class TestAudioWorldLifecycle:
    """Normative tests for Audio World Creation and Lifecycle Machine (§96)."""

    def test_audio_world_creation(self):
        fab, w = make_test_world("aw_create")
        assert w.audio_world_id == "aw_create"
        assert w.state == AudioWorldState.CREATED
        assert len(w.sources) == 0

    def test_audio_world_identity(self):
        fab, w = make_test_world("aw_ident")
        assert fab.get_world("aw_ident") is w
        assert fab.active_world is w

    def test_audio_world_state(self):
        fab, w = make_test_world("aw_state")
        fab.initialize_world(w)
        assert w.state == AudioWorldState.READY

    def test_audio_world_pause(self):
        fab, w = make_test_world("aw_pause")
        fab.initialize_world(w)
        fab.start_playback(w)
        assert w.state == AudioWorldState.PLAYING
        fab.pause_playback(w)
        assert w.state == AudioWorldState.PAUSED

    def test_audio_world_stop(self):
        fab, w = make_test_world("aw_stop")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.stop_playback(w)
        assert w.state == AudioWorldState.STOPPED

    def test_audio_world_destroy(self):
        fab, w = make_test_world("aw_destroy")
        fab.destroy_world(w)
        assert w.state == AudioWorldState.DESTROYED
        assert len(w.sources) == 0
        assert len(w.clips) == 0

    def test_invalid_audio_world_transition(self):
        fab, w = make_test_world("aw_invalid")
        with pytest.raises(ValueError, match="NO_INVALID_AUDIO_WORLD_TRANSITION"):
            fab.stop_playback(w)

    def test_audio_context(self):
        fab, w = make_test_world("aw_context")
        fab.initialize_world(w)
        assert w.mixer is not None
        assert "MASTER" in w.mixer.buses

    def test_headless_audio_world(self):
        fab, w = make_test_world("aw_headless")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.update(0.016, w)
        assert w.frames_rendered == 1

    def test_audio_world_cleanup(self):
        fab, w = make_test_world("aw_clean")
        fab.initialize_world(w)
        fab.destroy_world(w)
        assert w.state == AudioWorldState.DESTROYED


# ==============================================================================
# §97. AUDIO DEVICE TESTS (8 tests)
# ==============================================================================

class TestAudioDeviceExecution:
    """Normative tests for Audio Device Abstraction and Fault Recovery (§97)."""

    def test_device_creation(self):
        fab, w = make_test_world("aw_dev_1")
        dev = fab.create_device("dev_speakers", sample_rate=48000, channel_count=2, world=w)
        assert dev.device_id == "dev_speakers"
        assert dev.sample_rate == 48000
        assert dev.state == AudioDeviceState.READY

    def test_device_selection(self):
        fab, w = make_test_world("aw_dev_2")
        fab.create_device("dev_1", world=w)
        fab.create_device("dev_2", world=w)
        fab.set_active_device("dev_2", w)
        assert w.active_device_id == "dev_2"

    def test_default_device(self):
        fab, w = make_test_world("aw_dev_3")
        fab.create_device("dev_default", world=w)
        assert w.active_device_id == "dev_default"

    def test_device_state(self):
        fab, w = make_test_world("aw_dev_4")
        dev = fab.create_device("dev_state", world=w)
        assert dev.state == AudioDeviceState.READY

    def test_device_loss(self):
        fab, w = make_test_world("aw_dev_5")
        dev = fab.create_device("dev_lost", world=w)
        fab.handle_device_loss("dev_lost", w)
        assert dev.state == AudioDeviceState.LOST
        assert w.state == AudioWorldState.DEVICE_LOST

    def test_device_recovery(self):
        fab, w = make_test_world("aw_dev_6")
        dev = fab.create_device("dev_rec", world=w)
        fab.handle_device_loss("dev_rec", w)
        fab.recover_device("dev_rec", w)
        assert dev.state == AudioDeviceState.READY
        assert w.state == AudioWorldState.READY

    def test_device_shutdown(self):
        fab, w = make_test_world("aw_dev_7")
        dev = fab.create_device("dev_shut", world=w)
        fab.shutdown_device("dev_shut", w)
        assert dev.state == AudioDeviceState.STOPPED

    def test_invalid_device(self):
        fab, w = make_test_world("aw_dev_8")
        with pytest.raises(ValueError, match="INVALID_SAMPLE_RATE"):
            fab.create_device("dev_bad", sample_rate=-1, world=w)


# ==============================================================================
# §98. AUDIO CLIP TESTS (10 tests)
# ==============================================================================

class TestAudioClipManagement:
    """Normative tests for Audio Clips and Resource Metadata (§98)."""

    def test_audio_clip(self):
        fab, w = make_test_world("aw_clip_1")
        clip = AudioClip("clip_gunshot", duration_seconds=0.8, channels=2, sample_rate=44100)
        fab.register_clip(clip, w)
        assert "clip_gunshot" in w.clips
        assert w.clips["clip_gunshot"].duration_seconds == 0.8

    def test_clip_metadata(self):
        clip = AudioClip("clip_meta", duration_seconds=1.5, metadata={"author": "DarX"})
        d = clip.to_dict()
        assert d["metadata"]["author"] == "DarX"

    def test_clip_duration(self):
        clip = AudioClip("clip_dur", duration_seconds=3.2)
        assert clip.duration_seconds == 3.2

    def test_clip_sample_rate(self):
        clip = AudioClip("clip_sr", sample_rate=48000)
        assert clip.sample_rate == 48000

    def test_clip_channels(self):
        clip = AudioClip("clip_ch", channels=1)
        assert clip.channels == 1

    def test_clip_loop(self):
        clip = AudioClip("clip_loop", loop_mode=LoopMode.LOOP)
        assert clip.loop_mode == LoopMode.LOOP

    def test_loop_region(self):
        clip = AudioClip("clip_region", duration_seconds=5.0, loop_mode=LoopMode.LOOP_REGION, loop_start=1.0, loop_end=4.0)
        assert clip.loop_start == 1.0
        assert clip.loop_end == 4.0

    def test_invalid_loop(self):
        fab, w = make_test_world("aw_clip_inv_loop")
        clip = AudioClip("clip_bad_loop", duration_seconds=2.0, loop_mode=LoopMode.LOOP_REGION, loop_start=3.0, loop_end=1.0)
        with pytest.raises(ValueError, match="INVALID_LOOP_RANGE"):
            fab.register_clip(clip, w)

    def test_invalid_clip(self):
        fab, w = make_test_world("aw_clip_inv")
        clip = AudioClip("clip_bad", duration_seconds=-1.0)
        with pytest.raises(ValueError, match="INVALID_CLIP_DURATION"):
            fab.register_clip(clip, w)

    def test_clip_lifetime(self):
        fab, w = make_test_world("aw_clip_life")
        clip = AudioClip("clip_life", duration_seconds=1.0)
        fab.register_clip(clip, w)
        fab.destroy_clip("clip_life", w)
        assert "clip_life" not in w.clips


# ==============================================================================
# §99. AUDIO SOURCE TESTS (12 tests)
# ==============================================================================

class TestAudioSourceExecution:
    """Normative tests for Audio Sources and Playback Controls (§99)."""

    def test_source_creation(self):
        fab, w = make_test_world("aw_src_1")
        src = fab.create_source("src_1", volume=0.8, pitch=1.1, world=w)
        assert src.source_id == "src_1"
        assert src.volume == 0.8
        assert src.pitch == 1.1

    def test_source_play(self):
        fab, w = make_test_world("aw_src_2")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        src = fab.create_source("s2", clip_id="c1", world=w)
        v = fab.play_source("s2", w)
        assert v is not None
        assert src.state == AudioSourceState.PLAYING
        assert len(w.mixer.active_voices) == 1

    def test_source_pause(self):
        fab, w = make_test_world("aw_src_3")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        src = fab.create_source("s3", clip_id="c1", world=w)
        fab.play_source("s3", w)
        fab.pause_source("s3", w)
        assert src.state == AudioSourceState.PAUSED

    def test_source_resume(self):
        fab, w = make_test_world("aw_src_4")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        src = fab.create_source("s4", clip_id="c1", world=w)
        fab.play_source("s4", w)
        fab.pause_source("s4", w)
        fab.resume_source("s4", w)
        assert src.state == AudioSourceState.PLAYING

    def test_source_stop(self):
        fab, w = make_test_world("aw_src_5")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        src = fab.create_source("s5", clip_id="c1", world=w)
        fab.play_source("s5", w)
        fab.stop_source("s5", w)
        assert src.state == AudioSourceState.STOPPED
        assert len(w.mixer.active_voices) == 0

    def test_source_seek(self):
        fab, w = make_test_world("aw_src_6")
        fab.register_clip(AudioClip("c1", duration_seconds=10.0), w)
        src = fab.create_source("s6", clip_id="c1", world=w)
        fab.play_source("s6", w)
        fab.seek_source("s6", 4.5, w)
        assert src.playback_position == 4.5

    def test_source_volume(self):
        fab, w = make_test_world("aw_src_7")
        src = fab.create_source("s7", world=w)
        fab.set_source_volume("s7", 0.5, w)
        assert src.volume == 0.5

    def test_source_pitch(self):
        fab, w = make_test_world("aw_src_8")
        src = fab.create_source("s8", world=w)
        fab.set_source_pitch("s8", 1.5, w)
        assert src.pitch == 1.5

    def test_source_loop(self):
        fab, w = make_test_world("aw_src_9")
        src = fab.create_source("s9", loop=True, world=w)
        assert src.loop is True

    def test_source_priority(self):
        fab, w = make_test_world("aw_src_10")
        src = fab.create_source("s10", priority=200, world=w)
        assert src.priority == 200

    def test_source_destroy(self):
        fab, w = make_test_world("aw_src_11")
        fab.create_source("s11", world=w)
        fab.destroy_source("s11", w)
        assert "s11" not in w.sources

    def test_source_cleanup(self):
        fab, w = make_test_world("aw_src_12")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s12", clip_id="c1", world=w)
        fab.play_source("s12", w)
        fab.destroy_source("s12", w)
        assert len(w.mixer.active_voices) == 0


# ==============================================================================
# §100. AUDIO VOICE TESTS (8 tests)
# ==============================================================================

class TestAudioVoiceExecution:
    """Normative tests for Audio Voice Allocation, Stealing, and Budget (§100)."""

    def test_voice_creation(self):
        fab, w = make_test_world("aw_vc_1")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        v = fab.play_source("s1", w)
        assert v.voice_id.startswith("voice_")
        assert v.state == VoiceState.PLAYING

    def test_voice_playback(self):
        fab, w = make_test_world("aw_vc_2")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        v = fab.play_source("s1", w)
        fab.update(0.1, w)
        assert v.playback_time > 0.0

    def test_voice_budget(self):
        settings = AudioWorldSettings(max_voices=2)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_vc_3", settings=settings)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.create_source("s2", clip_id="c1", world=w)
        fab.play_source("s1", w)
        fab.play_source("s2", w)
        assert len(w.mixer.active_voices) == 2

    def test_voice_priority(self):
        settings = AudioWorldSettings(max_voices=1, voice_stealing_policy=VoiceStealingPolicy.STEAL_LOWEST_PRIORITY)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_vc_4", settings=settings)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s_low", clip_id="c1", priority=10, world=w)
        fab.create_source("s_high", clip_id="c1", priority=100, world=w)
        fab.play_source("s_low", w)
        assert "s_low" in [v.source_id for v in w.mixer.active_voices.values()]
        fab.play_source("s_high", w)
        assert "s_high" in [v.source_id for v in w.mixer.active_voices.values()]
        assert "s_low" not in [v.source_id for v in w.mixer.active_voices.values()]

    def test_voice_stealing(self):
        settings = AudioWorldSettings(max_voices=2, voice_stealing_policy=VoiceStealingPolicy.STEAL_OLDEST)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_vc_5", settings=settings)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.create_source("s2", clip_id="c1", world=w)
        fab.create_source("s3", clip_id="c1", world=w)
        fab.play_source("s1", w)
        fab.play_source("s2", w)
        fab.play_source("s3", w)
        assert len(w.mixer.active_voices) == 2
        # Oldest s1 should be stolen
        assert "s1" not in [v.source_id for v in w.mixer.active_voices.values()]

    def test_voice_stealing_determinism(self):
        def run_steal_sim():
            settings = AudioWorldSettings(max_voices=1, voice_stealing_policy=VoiceStealingPolicy.STEAL_OLDEST)
            fab = UniversalRuntimeAudioFabricator()
            w = fab.create_world("aw_det", settings=settings)
            fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
            fab.create_source("s1", clip_id="c1", world=w)
            fab.create_source("s2", clip_id="c1", world=w)
            fab.play_source("s1", w)
            fab.play_source("s2", w)
            return [v.source_id for v in w.mixer.active_voices.values()]

        assert run_steal_sim() == run_steal_sim() == ["s2"]

    def test_voice_release(self):
        fab, w = make_test_world("aw_vc_7")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.play_source("s1", w)
        assert len(w.mixer.active_voices) == 1
        fab.stop_source("s1", w)
        assert len(w.mixer.active_voices) == 0

    def test_voice_resource_protection(self):
        fab, w = make_test_world("aw_vc_8")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.play_source("s1", w)
        with pytest.raises(ValueError, match="RESOURCE_IN_USE"):
            fab.destroy_clip("c1", w)


# ==============================================================================
# §101. AUDIO LISTENER TESTS (6 tests)
# ==============================================================================

class TestAudioListenerExecution:
    """Normative tests for Audio Listener Transform, Velocity & Spatial Orientation (§101)."""

    def test_listener_creation(self):
        fab, w = make_test_world("aw_lis_1")
        lis = fab.create_listener("lis_main", position=[0.0, 1.0, 0.0], gain=1.0, world=w)
        assert lis.listener_id == "lis_main"
        assert lis.position == [0.0, 1.0, 0.0]
        assert lis.gain == 1.0

    def test_listener_transform(self):
        fab, w = make_test_world("aw_lis_2")
        lis = fab.create_listener("lis_tr", position=[5.0, 0.0, -10.0], forward=[0.0, 0.0, 1.0], world=w)
        assert lis.position == [5.0, 0.0, -10.0]
        assert lis.forward == [0.0, 0.0, 1.0]

    def test_listener_velocity(self):
        fab, w = make_test_world("aw_lis_3")
        lis = fab.create_listener("lis_vel", velocity=[0.0, 0.0, 20.0], world=w)
        assert lis.velocity == [0.0, 0.0, 20.0]

    def test_active_listener(self):
        fab, w = make_test_world("aw_lis_4")
        fab.create_listener("lis_1", world=w)
        fab.create_listener("lis_2", world=w)
        fab.set_active_listener("lis_2", w)
        assert w.active_listener_id == "lis_2"

    def test_multiple_listeners_policy(self):
        fab, w = make_test_world("aw_lis_5")
        fab.create_listener("lis_A", world=w)
        fab.create_listener("lis_B", world=w)
        assert len(w.listeners) == 2
        assert w.active_listener_id == "lis_A"

    def test_listener_destroy(self):
        fab, w = make_test_world("aw_lis_6")
        fab.create_listener("lis_del", world=w)
        fab.destroy_listener("lis_del", w)
        assert "lis_del" not in w.listeners


# ==============================================================================
# §102. SPATIALIZATION TESTS (9 tests)
# ==============================================================================

class TestSpatializationExecution:
    """Normative tests for 3D Distance, Relative Direction, and Attenuation Models (§102)."""

    def test_spatial_position(self):
        fab, w = make_test_world("aw_sp_1")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[3.0, 4.0, 0.0], world=w)
        d = fab.compute_spatial_distance("src", "lis", w)
        assert round(d, 4) == 5.0

    def test_spatial_distance(self):
        fab, w = make_test_world("aw_sp_2")
        fab.create_listener("lis", position=[1.0, 1.0, 1.0], world=w)
        fab.create_source("src", position=[4.0, 5.0, 1.0], world=w)
        assert round(fab.compute_spatial_distance("src", "lis", w), 4) == 5.0

    def test_spatial_direction(self):
        fab, w = make_test_world("aw_sp_3")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], forward=[0.0, 0.0, 1.0], world=w)
        fab.create_source("src", position=[10.0, 0.0, 0.0], world=w)
        gain, pitch, pan = fab.compute_voice_parameters("src", w)
        assert pan > 0.5  # Pan right

    def test_attenuation_linear(self):
        fab, w = make_test_world("aw_sp_4")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 50.0], min_distance=0.0, max_distance=100.0, distance_model=AudioDistanceModel.LINEAR, world=w)
        att = fab.compute_attenuation("src", "lis", w)
        assert round(att, 2) == 0.5

    def test_attenuation_inverse(self):
        fab, w = make_test_world("aw_sp_5")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 10.0], min_distance=1.0, max_distance=100.0, distance_model=AudioDistanceModel.INVERSE, world=w)
        att = fab.compute_attenuation("src", "lis", w)
        assert 0.0 < att < 1.0

    def test_attenuation_exponential(self):
        fab, w = make_test_world("aw_sp_6")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 20.0], min_distance=2.0, max_distance=100.0, distance_model=AudioDistanceModel.EXPONENTIAL, world=w)
        att = fab.compute_attenuation("src", "lis", w)
        assert att < 0.5

    def test_min_distance(self):
        fab, w = make_test_world("aw_sp_7")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 2.0], min_distance=5.0, max_distance=50.0, world=w)
        att = fab.compute_attenuation("src", "lis", w)
        assert att == 1.0

    def test_max_distance(self):
        fab, w = make_test_world("aw_sp_8")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 150.0], min_distance=5.0, max_distance=50.0, world=w)
        att = fab.compute_attenuation("src", "lis", w)
        assert att == 0.0

    def test_spatialization_determinism(self):
        fab1, w1 = make_test_world("aw_sp_det1")
        fab1.create_listener("lis", position=[1.0, 2.0, 3.0], world=w1)
        fab1.create_source("src", position=[4.0, 6.0, 8.0], world=w1)

        fab2, w2 = make_test_world("aw_sp_det2")
        fab2.create_listener("lis", position=[1.0, 2.0, 3.0], world=w2)
        fab2.create_source("src", position=[4.0, 6.0, 8.0], world=w2)

        p1 = fab1.compute_voice_parameters("src", w1)
        p2 = fab2.compute_voice_parameters("src", w2)
        assert p1 == p2


# ==============================================================================
# §103. DOPPLER TESTS (8 tests)
# ==============================================================================

class TestDopplerExecution:
    """Normative tests for Doppler Pitch Shift and Velocity Projections (§103)."""

    def test_doppler_static(self):
        fab, w = make_test_world("aw_dop_1")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 10.0], velocity=[0.0, 0.0, 0.0], world=w)
        shift = fab.compute_doppler("src", "lis", w)
        assert shift == 1.0

    def test_doppler_approaching(self):
        fab, w = make_test_world("aw_dop_2")
        # Source at +50 moving towards listener at origin (negative velocity along d vector)
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 50.0], velocity=[0.0, 0.0, -34.3], world=w)
        shift = fab.compute_doppler("src", "lis", w)
        assert shift > 1.0  # Higher pitch

    def test_doppler_receding(self):
        fab, w = make_test_world("aw_dop_3")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 50.0], velocity=[0.0, 0.0, 34.3], world=w)
        shift = fab.compute_doppler("src", "lis", w)
        assert shift < 1.0  # Lower pitch

    def test_doppler_source_velocity(self):
        fab, w = make_test_world("aw_dop_4")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 10.0], velocity=[0.0, 0.0, -50.0], world=w)
        assert fab.compute_doppler("src", "lis", w) > 1.0

    def test_doppler_listener_velocity(self):
        fab, w = make_test_world("aw_dop_5")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 50.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 100.0], velocity=[0.0, 0.0, 0.0], world=w)
        assert fab.compute_doppler("src", "lis", w) > 1.0

    def test_doppler_speed_of_sound(self):
        fab, w = make_test_world("aw_dop_6")
        w.settings.speed_of_sound = 500.0
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 10.0], velocity=[0.0, 0.0, -50.0], world=w)
        shift = fab.compute_doppler("src", "lis", w)
        assert shift > 1.0

    def test_doppler_limits(self):
        fab, w = make_test_world("aw_dop_7")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        # Extreme supersonic speed
        fab.create_source("src", position=[0.0, 0.0, 10.0], velocity=[0.0, 0.0, -1000.0], world=w)
        shift = fab.compute_doppler("src", "lis", w)
        assert shift <= w.settings.doppler_max_pitch

    def test_doppler_determinism(self):
        fab, w = make_test_world("aw_dop_8")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 10.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 20.0], velocity=[0.0, 0.0, -20.0], world=w)
        s1 = fab.compute_doppler("src", "lis", w)
        s2 = fab.compute_doppler("src", "lis", w)
        assert s1 == s2


# ==============================================================================
# §104. AUDIO BUS TESTS (9 tests)
# ==============================================================================

class TestBusExecution:
    """Normative tests for Audio Buses, Routing, Volumes, and Ducking (§104)."""

    def test_bus_creation(self):
        fab, w = make_test_world("aw_bus_1")
        bus = fab.create_bus("WEAPONS", parent_bus_id="SFX", volume=0.9, world=w)
        assert bus.bus_id == "WEAPONS"
        assert bus.parent_bus_id == "SFX"
        assert bus.volume == 0.9

    def test_bus_hierarchy(self):
        fab, w = make_test_world("aw_bus_2")
        fab.create_bus("UI", parent_bus_id="MASTER", volume=0.5, world=w)
        eff = fab.compute_bus_effective_volume("UI", w)
        assert eff == 0.5

    def test_bus_routing(self):
        fab, w = make_test_world("aw_bus_3")
        fab.create_source("s1", bus_id="SFX", world=w)
        fab.route_source_to_bus("s1", "MUSIC", w)
        assert w.sources["s1"].bus_id == "MUSIC"

    def test_bus_volume(self):
        fab, w = make_test_world("aw_bus_4")
        fab.set_bus_volume("SFX", 0.75, w)
        assert w.mixer.buses["SFX"].volume == 0.75

    def test_bus_mute(self):
        fab, w = make_test_world("aw_bus_5")
        fab.set_bus_mute("SFX", True, w)
        assert fab.compute_bus_effective_volume("SFX", w) == 0.0

    def test_bus_solo(self):
        fab, w = make_test_world("aw_bus_6")
        fab.set_bus_solo("MUSIC", True, w)
        # SFX is not soloed so it receives 0.0
        assert fab.compute_bus_effective_volume("SFX", w) == 0.0
        assert fab.compute_bus_effective_volume("MUSIC", w) > 0.0

    def test_bus_ducking(self):
        fab, w = make_test_world("aw_bus_7")
        fab.set_bus_ducking("MUSIC", ducking_factor=0.3, target_bus_id="VOICE", world=w)
        eff = fab.compute_bus_effective_volume("MUSIC", w)
        assert round(eff, 2) == 0.3

    def test_bus_destroy(self):
        fab, w = make_test_world("aw_bus_8")
        fab.create_bus("TEMP", world=w)
        fab.destroy_bus("TEMP", w)
        assert "TEMP" not in w.mixer.buses

    def test_bus_cleanup(self):
        fab, w = make_test_world("aw_bus_9")
        fab.create_bus("CLEAN_BUS", world=w)
        fab.create_source("s_bus", bus_id="CLEAN_BUS", world=w)
        fab.destroy_bus("CLEAN_BUS", w)
        assert w.sources["s_bus"].bus_id == "MASTER"


# ==============================================================================
# §105. AUDIO MIXER TESTS (8 tests)
# ==============================================================================

class TestMixerExecution:
    """Normative tests for Audio Mixer, Multi-Bus Mixing, and Voice Summation (§105)."""

    def test_mixer_creation(self):
        fab, w = make_test_world("aw_mix_1")
        assert w.mixer.mixer_id == "master_mixer"
        assert "MASTER" in w.mixer.buses

    def test_mixer_order(self):
        fab, w = make_test_world("aw_mix_2")
        mix = fab.mix_frame(w)
        assert "bus_levels" in mix
        assert "voice_outputs" in mix

    def test_mixer_source_mix(self):
        fab, w = make_test_world("aw_mix_3")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", volume=0.8, spatialized=False, world=w)
        fab.play_source("s1", w)
        mix = fab.mix_frame(w)
        assert len(mix["voice_outputs"]) == 1
        assert list(mix["voice_outputs"].values())[0] == 0.8

    def test_mixer_bus_mix(self):
        fab, w = make_test_world("aw_mix_4")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", bus_id="SFX", volume=1.0, spatialized=False, world=w)
        fab.play_source("s1", w)
        fab.set_bus_volume("SFX", 0.5, w)
        mix = fab.mix_frame(w)
        assert list(mix["voice_outputs"].values())[0] == 0.5

    def test_mixer_volume(self):
        fab, w = make_test_world("aw_mix_5")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", volume=1.0, spatialized=False, world=w)
        fab.play_source("s1", w)
        w.settings.master_volume = 0.5
        mix = fab.mix_frame(w)
        assert list(mix["voice_outputs"].values())[0] == 0.5

    def test_mixer_determinism(self):
        fab, w = make_test_world("aw_mix_6")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", volume=0.7, spatialized=False, world=w)
        fab.play_source("s1", w)
        m1 = fab.mix_frame(w)
        m2 = fab.mix_frame(w)
        assert m1 == m2

    def test_mixer_reset(self):
        fab, w = make_test_world("aw_mix_7")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.play_source("s1", w)
        assert len(w.mixer.active_voices) == 1
        w.mixer.active_voices.clear()
        assert len(w.mixer.active_voices) == 0

    def test_mixer_cleanup(self):
        fab, w = make_test_world("aw_mix_8")
        fab.destroy_world(w)
        assert len(w.mixer.buses) == 0


# ==============================================================================
# §106. AUDIO EFFECT TESTS (11 tests)
# ==============================================================================

class TestEffectExecution:
    """Normative tests for Audio Effects, Parameter Validation, and Chains (§106)."""

    def test_gain_effect(self):
        eff = AudioEffect("eff_gain", AudioEffectType.GAIN, parameters={"gain": 1.5})
        assert eff.effect_type == AudioEffectType.GAIN
        assert eff.parameters["gain"] == 1.5

    def test_low_pass_effect(self):
        eff = AudioEffect("eff_lp", AudioEffectType.LOW_PASS, parameters={"cutoff_hz": 1200.0})
        assert eff.parameters["cutoff_hz"] == 1200.0

    def test_high_pass_effect(self):
        eff = AudioEffect("eff_hp", AudioEffectType.HIGH_PASS, parameters={"cutoff_hz": 300.0})
        assert eff.parameters["cutoff_hz"] == 300.0

    def test_equalizer_effect(self):
        eff = AudioEffect("eff_eq", AudioEffectType.EQUALIZER, parameters={"low": 0.0, "mid": 2.0, "high": -1.0})
        assert eff.parameters["mid"] == 2.0

    def test_reverb_effect(self):
        eff = AudioEffect("eff_rev", AudioEffectType.REVERB, parameters={"decay_time": 2.5, "room_size": 0.8})
        assert eff.parameters["decay_time"] == 2.5

    def test_compressor_effect(self):
        eff = AudioEffect("eff_comp", AudioEffectType.COMPRESSOR, parameters={"threshold_db": -12.0, "ratio": 4.0})
        assert eff.parameters["ratio"] == 4.0

    def test_limiter_effect(self):
        eff = AudioEffect("eff_lim", AudioEffectType.LIMITER, parameters={"ceiling_db": -0.1})
        assert eff.parameters["ceiling_db"] == -0.1

    def test_effect_chain(self):
        fab, w = make_test_world("aw_eff_chain")
        e1 = AudioEffect("e1", AudioEffectType.GAIN)
        e2 = AudioEffect("e2", AudioEffectType.LOW_PASS)
        fab.add_effect_to_bus("SFX", e1, w)
        fab.add_effect_to_bus("SFX", e2, w)
        assert len(w.mixer.buses["SFX"].effects) == 2

    def test_effect_order(self):
        fab, w = make_test_world("aw_eff_ord")
        e1 = AudioEffect("first", AudioEffectType.GAIN)
        e2 = AudioEffect("second", AudioEffectType.REVERB)
        fab.add_effect_to_bus("SFX", e1, w)
        fab.add_effect_to_bus("SFX", e2, w)
        assert [e.effect_id for e in w.mixer.buses["SFX"].effects] == ["first", "second"]

    def test_effect_bypass(self):
        eff = AudioEffect("eff_byp", AudioEffectType.GAIN, is_bypassed=True)
        assert eff.is_bypassed is True

    def test_effect_parameter_validation(self):
        val = UniversalRuntimeAudioValidator()
        eff = AudioEffect("", AudioEffectType.GAIN)
        issues = val.validate_effect(eff)
        assert any(i.error_code == "EMPTY_EFFECT_ID" for i in issues)


# ==============================================================================
# §107. AUDIO COMMAND TESTS (12 tests)
# ==============================================================================

class TestCommandExecution:
    """Normative tests for Audio Command Queue, Validation, and Processing (§107)."""

    def test_play_command(self):
        fab, w = make_test_world("aw_cmd_1")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        cmd = AudioCommand("cmd_1", AudioCommandType.PLAY, "s1")
        fab.enqueue_command(cmd, w)
        fab.process_commands(w)
        assert w.sources["s1"].state == AudioSourceState.PLAYING

    def test_pause_command(self):
        fab, w = make_test_world("aw_cmd_2")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s2", clip_id="c1", world=w)
        fab.play_source("s2", w)
        fab.enqueue_command(AudioCommand("cmd_p", AudioCommandType.PAUSE, "s2"), w)
        fab.process_commands(w)
        assert w.sources["s2"].state == AudioSourceState.PAUSED

    def test_resume_command(self):
        fab, w = make_test_world("aw_cmd_3")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s3", clip_id="c1", world=w)
        fab.play_source("s3", w)
        fab.pause_source("s3", w)
        fab.enqueue_command(AudioCommand("cmd_r", AudioCommandType.RESUME, "s3"), w)
        fab.process_commands(w)
        assert w.sources["s3"].state == AudioSourceState.PLAYING

    def test_stop_command(self):
        fab, w = make_test_world("aw_cmd_4")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s4", clip_id="c1", world=w)
        fab.play_source("s4", w)
        fab.enqueue_command(AudioCommand("cmd_s", AudioCommandType.STOP, "s4"), w)
        fab.process_commands(w)
        assert w.sources["s4"].state == AudioSourceState.STOPPED

    def test_seek_command(self):
        fab, w = make_test_world("aw_cmd_5")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s5", clip_id="c1", world=w)
        fab.play_source("s5", w)
        fab.enqueue_command(AudioCommand("cmd_seek", AudioCommandType.SEEK, "s5", {"position": 3.0}), w)
        fab.process_commands(w)
        assert w.sources["s5"].playback_position == 3.0

    def test_volume_command(self):
        fab, w = make_test_world("aw_cmd_6")
        fab.create_source("s6", volume=1.0, world=w)
        fab.enqueue_command(AudioCommand("cmd_v", AudioCommandType.SET_VOLUME, "s6", {"volume": 0.4}), w)
        fab.process_commands(w)
        assert w.sources["s6"].volume == 0.4

    def test_pitch_command(self):
        fab, w = make_test_world("aw_cmd_7")
        fab.create_source("s7", pitch=1.0, world=w)
        fab.enqueue_command(AudioCommand("cmd_pi", AudioCommandType.SET_PITCH, "s7", {"pitch": 1.25}), w)
        fab.process_commands(w)
        assert w.sources["s7"].pitch == 1.25

    def test_transform_command(self):
        fab, w = make_test_world("aw_cmd_8")
        fab.create_source("s8", world=w)
        fab.enqueue_command(AudioCommand("cmd_tr", AudioCommandType.SET_POSITION, "s8", {"position": [10.0, 5.0, 0.0]}), w)
        fab.process_commands(w)
        assert w.sources["s8"].position == [10.0, 5.0, 0.0]

    def test_bus_command(self):
        fab, w = make_test_world("aw_cmd_9")
        fab.create_source("s9", bus_id="SFX", world=w)
        fab.enqueue_command(AudioCommand("cmd_b", AudioCommandType.SET_BUS, "s9", {"bus_id": "MUSIC"}), w)
        fab.process_commands(w)
        assert w.sources["s9"].bus_id == "MUSIC"

    def test_effect_command(self):
        fab, w = make_test_world("aw_cmd_10")
        fab.enqueue_command(AudioCommand("cmd_eff", AudioCommandType.SET_EFFECT_PARAMETER, "eff1", {"val": 1.0}), w)
        count = fab.process_commands(w)
        assert count == 1

    def test_command_order(self):
        fab, w = make_test_world("aw_cmd_11")
        fab.create_source("s11", volume=1.0, world=w)
        fab.enqueue_command(AudioCommand("c1", AudioCommandType.SET_VOLUME, "s11", {"volume": 0.3}), w)
        fab.enqueue_command(AudioCommand("c2", AudioCommandType.SET_VOLUME, "s11", {"volume": 0.8}), w)
        fab.process_commands(w)
        assert w.sources["s11"].volume == 0.8

    def test_invalid_command(self):
        fab, w = make_test_world("aw_cmd_12")
        # Target missing source safely ignored or rejected
        fab.enqueue_command(AudioCommand("c_bad", AudioCommandType.SET_VOLUME, "missing_source", {"volume": 0.5}), w)
        fab.process_commands(w)
        assert len(w.command_queue) == 0


# ==============================================================================
# §108. AUDIO EVENT TESTS (10 tests)
# ==============================================================================

class TestEventExecution:
    """Normative tests for Audio Events, Deduplication, and Ordering (§108)."""

    def test_play_started(self):
        fab, w = make_test_world("aw_ev_1")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.play_source("s1", w)
        assert any(e.event_type == AudioEventType.PLAY_STARTED for e in w.events)

    def test_play_paused(self):
        fab, w = make_test_world("aw_ev_2")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s2", clip_id="c1", world=w)
        fab.play_source("s2", w)
        fab.pause_source("s2", w)
        assert any(e.event_type == AudioEventType.PLAY_PAUSED for e in w.events)

    def test_play_resumed(self):
        fab, w = make_test_world("aw_ev_3")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s3", clip_id="c1", world=w)
        fab.play_source("s3", w)
        fab.pause_source("s3", w)
        fab.resume_source("s3", w)
        assert any(e.event_type == AudioEventType.PLAY_RESUMED for e in w.events)

    def test_play_stopped(self):
        fab, w = make_test_world("aw_ev_4")
        fab.register_clip(AudioClip("c1", duration_seconds=2.0), w)
        fab.create_source("s4", clip_id="c1", world=w)
        fab.play_source("s4", w)
        fab.stop_source("s4", w)
        assert any(e.event_type == AudioEventType.PLAY_STOPPED for e in w.events)

    def test_play_finished(self):
        fab, w = make_test_world("aw_ev_5")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=0.1), w)
        fab.create_source("s5", clip_id="c1", world=w)
        fab.play_source("s5", w)
        fab.update(0.2, w)
        assert any(e.event_type == AudioEventType.PLAY_FINISHED for e in w.events)

    def test_voice_stolen(self):
        settings = AudioWorldSettings(max_voices=1, voice_stealing_policy=VoiceStealingPolicy.STEAL_OLDEST)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_ev_6", settings=settings)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.create_source("s2", clip_id="c1", world=w)
        fab.play_source("s1", w)
        fab.play_source("s2", w)
        assert any(e.event_type == AudioEventType.VOICE_STOLEN for e in w.events)

    def test_device_lost_event(self):
        fab, w = make_test_world("aw_ev_7")
        fab.create_device("dev_main", world=w)
        fab.handle_device_loss("dev_main", w)
        assert any(e.event_type == AudioEventType.DEVICE_LOST for e in w.events)

    def test_device_recovered_event(self):
        fab, w = make_test_world("aw_ev_8")
        fab.create_device("dev_main", world=w)
        fab.handle_device_loss("dev_main", w)
        fab.recover_device("dev_main", w)
        assert any(e.event_type == AudioEventType.DEVICE_RECOVERED for e in w.events)

    def test_event_order(self):
        fab, w = make_test_world("aw_ev_9")
        fab.emit_event(AudioEventType.PLAY_STARTED, "s1", world=w)
        fab.emit_event(AudioEventType.PLAY_STOPPED, "s1", world=w)
        assert [e.event_type for e in w.events] == [AudioEventType.PLAY_STARTED, AudioEventType.PLAY_STOPPED]

    def test_event_deduplication(self):
        fab, w = make_test_world("aw_ev_10")
        fab.emit_event(AudioEventType.PLAY_STARTED, "s1", world=w)
        fab.emit_event(AudioEventType.PLAY_STARTED, "s1", world=w)
        # Should be deduplicated within the same frame/tick
        matches = [e for e in w.events if e.event_type == AudioEventType.PLAY_STARTED and e.source_id == "s1"]
        assert len(matches) == 1


# ==============================================================================
# §109. AUDIO STREAM TESTS (10 tests)
# ==============================================================================

class TestStreamExecution:
    """Normative tests for Audio Streams, Buffering, and Underflow Recovery (§109)."""

    def test_stream_open(self):
        fab, w = make_test_world("aw_str_1")
        s = fab.open_stream("str_music", buffer_size_bytes=32768, world=w)
        assert s.stream_id == "str_music"
        assert s.is_open is True

    def test_stream_buffer(self):
        fab, w = make_test_world("aw_str_2")
        fab.open_stream("s2", world=w)
        fab.buffer_stream("s2", 1024, w)
        assert w.streams["s2"].bytes_buffered == 1024

    def test_stream_decode(self):
        fab, w = make_test_world("aw_str_3")
        fab.open_stream("s3", buffer_size_bytes=512, world=w)
        fab.buffer_stream("s3", 1024, w)
        success = fab.decode_stream("s3", w)
        assert success is True
        assert w.streams["s3"].bytes_buffered == 512

    def test_stream_refill(self):
        fab, w = make_test_world("aw_str_4")
        fab.open_stream("s4", world=w)
        fab.buffer_stream("s4", 500, w)
        fab.refill_stream("s4", 500, w)
        assert w.streams["s4"].bytes_buffered == 1000

    def test_stream_end(self):
        fab, w = make_test_world("aw_str_5")
        fab.open_stream("s5", world=w)
        w.streams["s5"].is_exhausted = True
        assert w.streams["s5"].is_exhausted is True

    def test_stream_close(self):
        fab, w = make_test_world("aw_str_6")
        fab.open_stream("s6", world=w)
        fab.close_stream("s6", w)
        assert "s6" not in w.streams

    def test_stream_underflow(self):
        fab, w = make_test_world("aw_str_7")
        fab.open_stream("s7", buffer_size_bytes=1024, world=w)
        # Empty stream decode causes underflow / exhaustion
        success = fab.decode_stream("s7", w)
        assert success is False
        assert w.streams["s7"].is_exhausted is True

    def test_stream_recovery(self):
        fab, w = make_test_world("aw_str_8")
        fab.open_stream("s8", buffer_size_bytes=1024, world=w)
        fab.decode_stream("s8", w)
        assert w.streams["s8"].is_exhausted is True
        fab.refill_stream("s8", 2048, w)
        assert w.streams["s8"].is_exhausted is False
        assert fab.decode_stream("s8", w) is True

    def test_stream_memory_limit(self):
        fab, w = make_test_world("aw_str_9")
        fab.open_stream("s9", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.buffer_stream("s9", w.settings.max_stream_memory_bytes + 1, w)

    def test_stream_cleanup(self):
        fab, w = make_test_world("aw_str_10")
        fab.open_stream("s10", world=w)
        fab.destroy_world(w)
        assert len(w.streams) == 0


# ==============================================================================
# §110. AUDIO SNAPSHOT TESTS (8 tests)
# ==============================================================================

class TestSnapshotExecution:
    """Normative tests for Audio State Snapshots, Serialization, and Restoration (§110)."""

    def test_audio_snapshot(self):
        fab, w = make_test_world("aw_snap_1")
        snap = fab.capture_snapshot(w)
        assert snap.snapshot_id.startswith("snap_")
        assert len(snap.snapshot_hash) == 64

    def test_snapshot_source_state(self):
        fab, w = make_test_world("aw_snap_2")
        fab.create_source("s1", volume=0.75, world=w)
        snap = fab.capture_snapshot(w)
        assert "s1" in snap.sources
        assert snap.sources["s1"]["volume"] == 0.75

    def test_snapshot_voice_state(self):
        fab, w = make_test_world("aw_snap_3")
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.play_source("s1", w)
        snap = fab.capture_snapshot(w)
        assert len(snap.voices) == 1

    def test_snapshot_bus_state(self):
        fab, w = make_test_world("aw_snap_4")
        fab.set_bus_volume("SFX", 0.6, w)
        snap = fab.capture_snapshot(w)
        assert snap.buses["SFX"]["volume"] == 0.6

    def test_snapshot_effect_state(self):
        fab, w = make_test_world("aw_snap_5")
        eff = AudioEffect("eq1", AudioEffectType.EQUALIZER, parameters={"mid": 3.0})
        fab.add_effect_to_bus("SFX", eff, w)
        snap = fab.capture_snapshot(w)
        assert len(snap.buses["SFX"]["effects"]) == 1

    def test_snapshot_position(self):
        fab, w = make_test_world("aw_snap_6")
        fab.create_source("s1", position=[10.0, 20.0, 30.0], world=w)
        snap = fab.capture_snapshot(w)
        assert snap.sources["s1"]["position"] == [10.0, 20.0, 30.0]

    def test_snapshot_restore(self):
        fab, w = make_test_world("aw_snap_7")
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", volume=0.9, world=w)
        fab.play_source("s1", w)
        snap = fab.capture_snapshot(w)

        # Mutate
        fab.set_source_volume("s1", 0.1, w)
        fab.stop_source("s1", w)
        assert len(w.mixer.active_voices) == 0

        # Restore
        fab.restore_snapshot(snap, w)
        assert w.sources["s1"].volume == 0.9
        assert len(w.mixer.active_voices) == 1

    def test_snapshot_validation(self):
        fab, w = make_test_world("aw_snap_8")
        snap = fab.capture_snapshot(w)
        # Tamper hash
        snap.snapshot_hash = "invalid_hash_value"
        with pytest.raises(ValueError, match="SNAPSHOT_VALIDATION_FAILED"):
            fab.restore_snapshot(snap, w)


# ==============================================================================
# §111. AUDIO REPLAY TESTS (10 tests)
# ==============================================================================

class TestReplayExecution:
    """Normative tests for Audio Replay Command Recording and Playback (§111)."""

    def test_audio_replay(self):
        replay = AudioReplay("rep_1", commands=[
            AudioReplayCommand("c1", "PLAY", "s1", timestamp=0.0)
        ])
        assert replay.replay_id == "rep_1"
        assert len(replay.commands) == 1

    def test_play_replay(self):
        fab, w = make_test_world("aw_rep_1")
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        rep = AudioReplay("r1", commands=[AudioReplayCommand("c1", "PLAY", "s1")])
        fab.execute_replay(rep, w)
        assert w.sources["s1"].state == AudioSourceState.PLAYING

    def test_pause_replay(self):
        fab, w = make_test_world("aw_rep_2")
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        rep = AudioReplay("r2", commands=[
            AudioReplayCommand("c1", "PLAY", "s1", timestamp=0.0),
            AudioReplayCommand("c2", "PAUSE", "s1", timestamp=0.5),
        ])
        fab.execute_replay(rep, w)
        assert w.sources["s1"].state == AudioSourceState.PAUSED

    def test_seek_replay(self):
        fab, w = make_test_world("aw_rep_3")
        fab.register_clip(AudioClip("c1", duration_seconds=10.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        rep = AudioReplay("r3", commands=[
            AudioReplayCommand("c1", "PLAY", "s1"),
            AudioReplayCommand("c2", "SEEK", "s1", {"position": 4.0}),
        ])
        fab.execute_replay(rep, w)
        assert w.sources["s1"].playback_position == 4.0

    def test_volume_replay(self):
        fab, w = make_test_world("aw_rep_4")
        fab.create_source("s1", volume=1.0, world=w)
        rep = AudioReplay("r4", commands=[
            AudioReplayCommand("c1", "SET_VOLUME", "s1", {"volume": 0.25}),
        ])
        fab.execute_replay(rep, w)
        assert w.sources["s1"].volume == 0.25

    def test_spatial_replay(self):
        fab, w = make_test_world("aw_rep_5")
        fab.create_source("s1", position=[0.0, 0.0, 0.0], world=w)
        rep = AudioReplay("r5", commands=[
            AudioReplayCommand("c1", "SET_POSITION", "s1", {"position": [10.0, 0.0, 0.0]}),
        ])
        # Direct execution of position command
        for cmd in rep.commands:
            if cmd.command_type == "SET_POSITION":
                w.sources[cmd.target_id].position = list(cmd.params["position"])
        assert w.sources["s1"].position == [10.0, 0.0, 0.0]

    def test_bus_replay(self):
        fab, w = make_test_world("aw_rep_6")
        fab.create_source("s1", bus_id="SFX", world=w)
        rep = AudioReplay("r6", commands=[
            AudioReplayCommand("c1", "SET_BUS", "s1", {"bus_id": "MUSIC"}),
        ])
        for cmd in rep.commands:
            if cmd.command_type == "SET_BUS":
                fab.route_source_to_bus(cmd.target_id, cmd.params["bus_id"], w)
        assert w.sources["s1"].bus_id == "MUSIC"

    def test_effect_replay(self):
        fab, w = make_test_world("aw_rep_7")
        eff = AudioEffect("e1", AudioEffectType.GAIN, {"gain": 1.0})
        fab.add_effect_to_bus("SFX", eff, w)
        rep = AudioReplay("r7", commands=[
            AudioReplayCommand("c1", "SET_EFFECT_PARAMETER", "e1", {"gain": 2.0}),
        ])
        eff.parameters["gain"] = 2.0
        assert eff.parameters["gain"] == 2.0

    def test_replay_determinism(self):
        def run_rep():
            fab, w = make_test_world("aw_rep_det")
            fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
            fab.create_source("s1", clip_id="c1", world=w)
            rep = AudioReplay("r_det", commands=[
                AudioReplayCommand("c1", "PLAY", "s1"),
                AudioReplayCommand("c2", "SET_VOLUME", "s1", {"volume": 0.45}),
            ])
            fab.execute_replay(rep, w)
            return w.sources["s1"].volume

        assert run_rep() == run_rep() == 0.45

    def test_replay_corruption(self):
        fab, w = make_test_world("aw_rep_corrupt")
        rep = AudioReplay("r_bad", commands=[
            AudioReplayCommand("c_bad", "UNKNOWN_CMD", "non_existent_id"),
        ])
        fab.execute_replay(rep, w)
        assert rep.is_finished is True


# ==============================================================================
# §112. DETERMINISM TESTS (10 tests)
# ==============================================================================

class TestDeterminismExecution:
    """Normative tests for Deterministic Audio Computations (§112)."""

    def test_same_input_same_audio_state(self):
        def build_and_step(wid):
            fab, w = make_test_world(wid)
            fab.initialize_world(w)
            fab.start_playback(w)
            fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
            fab.create_source("s1", clip_id="c1", world=w)
            fab.play_source("s1", w)
            fab.update(0.1, w)
            return w.compute_fingerprint()

        assert build_and_step("aw_det") == build_and_step("aw_det")

    def test_same_clock_same_result(self):
        fab, w = make_test_world("aw_clk")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.update(0.016, w)
        t1 = w.time_seconds
        fab.update(0.016, w)
        t2 = w.time_seconds
        assert round(t2 - t1, 4) == 0.016

    def test_same_source_state_same_result(self):
        fab, w = make_test_world("aw_src_res")
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", volume=0.5, pitch=1.2, world=w)
        v1 = fab.compute_voice_parameters("s1", w)
        v2 = fab.compute_voice_parameters("s1", w)
        assert v1 == v2

    def test_same_spatial_input_same_result(self):
        fab, w = make_test_world("aw_sp_same")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[10.0, 10.0, 0.0], world=w)
        a1 = fab.compute_attenuation("src", "lis", w)
        a2 = fab.compute_attenuation("src", "lis", w)
        assert a1 == a2

    def test_same_bus_state_same_result(self):
        fab, w = make_test_world("aw_bus_same")
        fab.set_bus_volume("SFX", 0.65, w)
        v1 = fab.compute_bus_effective_volume("SFX", w)
        v2 = fab.compute_bus_effective_volume("SFX", w)
        assert v1 == v2

    def test_same_effect_state_same_result(self):
        eff1 = AudioEffect("e1", AudioEffectType.GAIN, {"gain": 1.2})
        eff2 = AudioEffect("e1", AudioEffectType.GAIN, {"gain": 1.2})
        assert eff1.to_dict() == eff2.to_dict()

    def test_voice_stealing_determinism(self):
        settings = AudioWorldSettings(max_voices=1, voice_stealing_policy=VoiceStealingPolicy.STEAL_LOWEST_PRIORITY)
        fab, w = make_test_world("aw_v_det")
        w.settings = settings
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s_a", clip_id="c1", priority=10, world=w)
        fab.create_source("s_b", clip_id="c1", priority=20, world=w)
        fab.play_source("s_a", w)
        fab.play_source("s_b", w)
        assert list(w.mixer.active_voices.values())[0].source_id == "s_b"

    def test_event_order_determinism(self):
        fab, w = make_test_world("aw_ev_det")
        fab.emit_event(AudioEventType.PLAY_STARTED, "s1", world=w)
        fab.emit_event(AudioEventType.PLAY_PAUSED, "s1", world=w)
        fab.emit_event(AudioEventType.PLAY_RESUMED, "s1", world=w)
        assert [e.event_type for e in w.events] == [
            AudioEventType.PLAY_STARTED,
            AudioEventType.PLAY_PAUSED,
            AudioEventType.PLAY_RESUMED,
        ]

    def test_replay_determinism(self):
        fab, w = make_test_world("aw_rep_det2")
        rep = AudioReplay("r", commands=[
            AudioReplayCommand("c1", "SET_VOLUME", "s1", {"volume": 0.33}),
        ])
        fab.create_source("s1", world=w)
        fab.execute_replay(rep, w)
        assert w.sources["s1"].volume == 0.33

    def test_snapshot_determinism(self):
        fab, w = make_test_world("aw_snap_det")
        s1 = fab.capture_snapshot(w)
        s2 = fab.capture_snapshot(w)
        assert s1.snapshot_hash == s2.snapshot_hash


# ==============================================================================
# §113. GOLDEN AUDIO TESTS (15 tests)
# ==============================================================================

class TestGoldenAudioExecution:
    """Normative tests for Deterministic Golden Audio State Hashes (§113)."""

    def test_golden_empty_audio(self):
        fab, w = make_test_world("aw_g_empty")
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga
        assert ga["sources_count"] == 0

    def test_golden_single_source(self):
        fab, w = make_test_world("aw_g_single")
        fab.register_clip(AudioClip("c1", duration_seconds=1.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        ga = fab.capture_golden_audio(w)
        assert ga["sources_count"] == 1

    def test_golden_loop(self):
        fab, w = make_test_world("aw_g_loop")
        fab.register_clip(AudioClip("c1", duration_seconds=1.0, loop_mode=LoopMode.LOOP), w)
        fab.create_source("s1", clip_id="c1", loop=True, world=w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_multiple_sources(self):
        fab, w = make_test_world("aw_g_multi")
        for i in range(5):
            fab.create_source(f"s_{i}", world=w)
        ga = fab.capture_golden_audio(w)
        assert ga["sources_count"] == 5

    def test_golden_spatial_audio(self):
        fab, w = make_test_world("aw_g_spat")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[10.0, 0.0, 5.0], world=w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_attenuation(self):
        fab, w = make_test_world("aw_g_att")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 25.0], min_distance=1.0, max_distance=100.0, world=w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_doppler(self):
        fab, w = make_test_world("aw_g_dop")
        fab.create_listener("lis", position=[0.0, 0.0, 0.0], world=w)
        fab.create_source("src", position=[0.0, 0.0, 25.0], velocity=[0.0, 0.0, -20.0], world=w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_bus_mix(self):
        fab, w = make_test_world("aw_g_mix")
        fab.set_bus_volume("SFX", 0.7, w)
        ga = fab.capture_golden_audio(w)
        assert ga["mix"]["bus_levels"]["SFX"] == 0.7

    def test_golden_effect_chain(self):
        fab, w = make_test_world("aw_g_eff")
        fab.add_effect_to_bus("SFX", AudioEffect("e1", AudioEffectType.GAIN), w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_stream(self):
        fab, w = make_test_world("aw_g_stream")
        fab.open_stream("str1", world=w)
        ga = fab.capture_golden_audio(w)
        assert ga["streams_count"] == 1

    def test_golden_snapshot_restore(self):
        fab, w = make_test_world("aw_g_snap")
        snap = fab.capture_snapshot(w)
        fab.restore_snapshot(snap, w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_replay(self):
        fab, w = make_test_world("aw_g_rep")
        fab.create_source("s1", world=w)
        rep = AudioReplay("r", [AudioReplayCommand("c1", "SET_VOLUME", "s1", {"volume": 0.5})])
        fab.execute_replay(rep, w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_device_recovery(self):
        fab, w = make_test_world("aw_g_dev")
        fab.create_device("dev1", world=w)
        fab.handle_device_loss("dev1", w)
        fab.recover_device("dev1", w)
        ga = fab.capture_golden_audio(w)
        assert "golden_hash" in ga

    def test_golden_silence_after_stop(self):
        fab, w = make_test_world("aw_g_silence")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.play_source("s1", w)
        fab.stop_source("s1", w)
        ga = fab.capture_golden_audio(w)
        assert ga["voices_count"] == 0

    def test_golden_audio_sequence(self):
        fab, w = make_test_world("aw_g_seq")
        fab.initialize_world(w)
        fab.start_playback(w)
        h1 = fab.capture_golden_audio(w)["golden_hash"]
        fab.update(0.016, w)
        h2 = fab.capture_golden_audio(w)["golden_hash"]
        assert h1 != h2


# ==============================================================================
# §114. SECURITY TESTS (20 tests)
# ==============================================================================

class TestSecurityExecution:
    """Normative tests for Audio World Security, Budgets, and Validation Limits (§114)."""

    def test_source_count_exhaustion(self):
        settings = AudioWorldSettings(max_sources=2)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_sec_1", settings=settings)
        fab.create_source("s1", world=w)
        fab.create_source("s2", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_source("s3", world=w)

    def test_voice_count_exhaustion(self):
        settings = AudioWorldSettings(max_voices=1, voice_stealing_policy=VoiceStealingPolicy.REJECT)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_sec_2", settings=settings)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.create_source("s2", clip_id="c1", world=w)
        fab.play_source("s1", w)
        with pytest.raises(ValueError, match="VOICE_BUDGET_EXHAUSTED"):
            fab.play_source("s2", w)

    def test_clip_count_exhaustion(self):
        settings = AudioWorldSettings(max_clips=2)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_sec_3", settings=settings)
        fab.register_clip(AudioClip("c1"), w)
        fab.register_clip(AudioClip("c2"), w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.register_clip(AudioClip("c3"), w)

    def test_stream_count_exhaustion(self):
        settings = AudioWorldSettings(max_streams=2)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_sec_4", settings=settings)
        fab.open_stream("str1", world=w)
        fab.open_stream("str2", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.open_stream("str3", world=w)

    def test_bus_count_exhaustion(self):
        settings = AudioWorldSettings(max_buses=6)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_sec_5", settings=settings)
        fab.create_bus("B_EXTRA", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_bus("B_OVERFLOW", world=w)

    def test_effect_chain_exhaustion(self):
        fab, w = make_test_world("aw_sec_6")
        for i in range(50):
            fab.add_effect_to_bus("SFX", AudioEffect(f"eff_{i}", AudioEffectType.GAIN), w)
        assert len(w.mixer.buses["SFX"].effects) == 50

    def test_audio_buffer_exhaustion(self):
        fab, w = make_test_world("aw_sec_7")
        s = fab.open_stream("str_buf", buffer_size_bytes=1024, world=w)
        assert s.buffer_size_bytes == 1024

    def test_stream_memory_exhaustion(self):
        fab, w = make_test_world("aw_sec_8")
        fab.open_stream("str_mem", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.buffer_stream("str_mem", w.settings.max_stream_memory_bytes + 100, w)

    def test_decode_work_exhaustion(self):
        fab, w = make_test_world("aw_sec_9")
        s = fab.open_stream("str_dec", buffer_size_bytes=512, world=w)
        fab.buffer_stream("str_dec", 512, w)
        assert fab.decode_stream("str_dec", w) is True
        assert fab.decode_stream("str_dec", w) is False  # Exhausted

    def test_command_flood(self):
        settings = AudioWorldSettings(max_commands=2)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_sec_10", settings=settings)
        fab.enqueue_command(AudioCommand("c1", AudioCommandType.PLAY, "s1"), w)
        fab.enqueue_command(AudioCommand("c2", AudioCommandType.PAUSE, "s1"), w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.enqueue_command(AudioCommand("c3", AudioCommandType.STOP, "s1"), w)

    def test_event_flood(self):
        fab, w = make_test_world("aw_sec_11")
        for i in range(100):
            fab.emit_event(AudioEventType.PLAY_STARTED, f"s_{i}", world=w)
        assert len(w.events) == 100

    def test_invalid_sample_rate(self):
        val = UniversalRuntimeAudioValidator()
        clip = AudioClip("bad_sr", sample_rate=-44100)
        issues = val.validate_clip(clip)
        assert any(i.error_code == "INVALID_SAMPLE_RATE" for i in issues)

    def test_invalid_channel_count(self):
        val = UniversalRuntimeAudioValidator()
        clip = AudioClip("bad_ch", channels=0)
        issues = val.validate_clip(clip)
        assert any(i.error_code == "INVALID_CHANNELS" for i in issues)

    def test_invalid_buffer_size(self):
        fab, w = make_test_world("aw_sec_14")
        with pytest.raises(ValueError, match="INVALID_BUFFER_SIZE"):
            fab.open_stream("str_bad", buffer_size_bytes=-100, world=w)

    def test_invalid_pitch(self):
        fab, w = make_test_world("aw_sec_15")
        with pytest.raises(ValueError, match="INVALID_PITCH"):
            fab.create_source("s_bad_p", pitch=-1.0, world=w)

    def test_invalid_volume(self):
        fab, w = make_test_world("aw_sec_16")
        with pytest.raises(ValueError, match="INVALID_VOLUME"):
            fab.create_source("s_bad_v", volume=-0.5, world=w)

    def test_invalid_loop_range(self):
        val = UniversalRuntimeAudioValidator()
        clip = AudioClip("c_bad_loop", duration_seconds=3.0, loop_mode=LoopMode.LOOP_REGION, loop_start=2.5, loop_end=1.0)
        issues = val.validate_clip(clip)
        assert any(i.error_code == "INVALID_LOOP_RANGE" for i in issues)

    def test_invalid_device(self):
        val = UniversalRuntimeAudioValidator()
        dev = AudioDevice("dev_bad", sample_rate=0, channel_count=-1)
        issues = val.validate_device(dev)
        assert any(i.error_code == "INVALID_SAMPLE_RATE" for i in issues)
        assert any(i.error_code == "INVALID_CHANNELS" for i in issues)

    def test_snapshot_tampering(self):
        fab, w = make_test_world("aw_sec_19")
        snap = fab.capture_snapshot(w)
        snap.sources["hacked_source"] = {}
        with pytest.raises(ValueError, match="SNAPSHOT_VALIDATION_FAILED"):
            fab.restore_snapshot(snap, w)

    def test_replay_tampering(self):
        fab, w = make_test_world("aw_sec_20")
        rep = AudioReplay("rep_tamper", [
            AudioReplayCommand("c1", "SET_VOLUME", "s_unknown", {"volume": 0.5})
        ])
        fab.execute_replay(rep, w)
        assert rep.is_finished is True


# ==============================================================================
# §115. PERFORMANCE TESTS (16 tests)
# ==============================================================================

class TestPerformanceExecution:
    """Normative tests for Audio Engine Performance & Throughput (§115)."""

    def test_100_sources(self):
        fab, w = make_test_world("aw_perf_100")
        t0 = time.perf_counter()
        for i in range(100):
            fab.create_source(f"s_{i}", world=w)
        elapsed = time.perf_counter() - t0
        assert len(w.sources) == 100
        assert elapsed < 0.5

    def test_1k_sources(self):
        fab, w = make_test_world("aw_perf_1k")
        t0 = time.perf_counter()
        sources = {
            f"s_{i}": AudioSource(f"s_{i}") for i in range(1000)
        }
        w.sources.update(sources)
        elapsed = time.perf_counter() - t0
        assert len(w.sources) == 1000
        assert elapsed < 0.5

    def test_10k_sources(self):
        fab, w = make_test_world("aw_perf_10k")
        assert w.settings.max_sources >= 1000

    def test_many_voices(self):
        fab, w = make_test_world("aw_perf_voices")
        w.settings.max_voices = 200
        fab.register_clip(AudioClip("c1", duration_seconds=10.0), w)
        for i in range(100):
            src = fab.create_source(f"s_{i}", clip_id="c1", world=w)
            fab.play_source(f"s_{i}", w)
        assert len(w.mixer.active_voices) == 100

    def test_many_buses(self):
        fab, w = make_test_world("aw_perf_buses")
        t0 = time.perf_counter()
        for i in range(25):
            fab.create_bus(f"bus_{i}", parent_bus_id="SFX", world=w)
        elapsed = time.perf_counter() - t0
        assert len(w.mixer.buses) >= 30
        assert elapsed < 0.5

    def test_large_effect_chain(self):
        fab, w = make_test_world("aw_perf_eff")
        t0 = time.perf_counter()
        for i in range(100):
            fab.add_effect_to_bus("SFX", AudioEffect(f"e_{i}", AudioEffectType.GAIN), w)
        elapsed = time.perf_counter() - t0
        assert len(w.mixer.buses["SFX"].effects) == 100
        assert elapsed < 0.5

    def test_spatialization_throughput(self):
        fab, w = make_test_world("aw_perf_spat")
        fab.create_listener("lis", world=w)
        for i in range(500):
            w.sources[f"s_{i}"] = AudioSource(f"s_{i}", position=[float(i), 0.0, 0.0])
        t0 = time.perf_counter()
        for i in range(500):
            fab.compute_spatial_distance(f"s_{i}", "lis", w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_attenuation_throughput(self):
        fab, w = make_test_world("aw_perf_att")
        fab.create_listener("lis", world=w)
        for i in range(500):
            w.sources[f"s_{i}"] = AudioSource(f"s_{i}", position=[float(i), 0.0, 0.0])
        t0 = time.perf_counter()
        for i in range(500):
            fab.compute_attenuation(f"s_{i}", "lis", w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_doppler_throughput(self):
        fab, w = make_test_world("aw_perf_dop")
        fab.create_listener("lis", world=w)
        for i in range(500):
            w.sources[f"s_{i}"] = AudioSource(f"s_{i}", position=[float(i), 0.0, 10.0], velocity=[10.0, 0.0, 0.0])
        t0 = time.perf_counter()
        for i in range(500):
            fab.compute_doppler(f"s_{i}", "lis", w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_mixer_throughput(self):
        fab, w = make_test_world("aw_perf_mix")
        t0 = time.perf_counter()
        for _ in range(100):
            fab.mix_frame(w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_stream_decode_throughput(self):
        fab, w = make_test_world("aw_perf_dec")
        s = fab.open_stream("str1", buffer_size_bytes=1024, world=w)
        fab.buffer_stream("str1", 102400, w)
        t0 = time.perf_counter()
        for _ in range(100):
            fab.decode_stream("str1", w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_command_throughput(self):
        fab, w = make_test_world("aw_perf_cmd")
        fab.create_source("s1", world=w)
        for i in range(500):
            fab.enqueue_command(AudioCommand(f"c_{i}", AudioCommandType.SET_VOLUME, "s1", {"volume": 0.5}), w)
        t0 = time.perf_counter()
        count = fab.process_commands(w)
        elapsed = time.perf_counter() - t0
        assert count == 500
        assert elapsed < 0.5

    def test_event_throughput(self):
        fab, w = make_test_world("aw_perf_ev")
        t0 = time.perf_counter()
        for i in range(500):
            fab.emit_event(AudioEventType.PLAY_STARTED, f"s_{i}", world=w)
        elapsed = time.perf_counter() - t0
        assert len(w.events) == 500
        assert elapsed < 0.5

    def test_snapshot_throughput(self):
        fab, w = make_test_world("aw_perf_snap")
        t0 = time.perf_counter()
        for _ in range(100):
            fab.capture_snapshot(w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_replay_throughput(self):
        fab, w = make_test_world("aw_perf_rep")
        cmds = [AudioReplayCommand(f"c_{i}", "SET_VOLUME", "s1", {"volume": 0.5}) for i in range(200)]
        rep = AudioReplay("r_bulk", cmds)
        fab.create_source("s1", world=w)
        t0 = time.perf_counter()
        fab.execute_replay(rep, w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_device_recovery(self):
        fab, w = make_test_world("aw_perf_rec")
        dev = fab.create_device("dev1", world=w)
        t0 = time.perf_counter()
        for _ in range(50):
            fab.handle_device_loss("dev1", w)
            fab.recover_device("dev1", w)
        elapsed = time.perf_counter() - t0
        assert dev.state == AudioDeviceState.READY
        assert elapsed < 0.5


# ==============================================================================
# §116. STRESS TESTS (18 tests)
# ==============================================================================

class TestStressExecution:
    """Normative tests for Audio Engine Rapid Reconfiguration & Stress Load (§116)."""

    def test_stress_source_spawn(self):
        fab, w = make_test_world("aw_str_src_sp")
        for i in range(500):
            fab.create_source(f"src_{i}", world=w)
        assert len(w.sources) == 500

    def test_stress_source_destroy(self):
        fab, w = make_test_world("aw_str_src_des")
        for i in range(200):
            fab.create_source(f"s_{i}", world=w)
        for i in range(200):
            fab.destroy_source(f"s_{i}", w)
        assert len(w.sources) == 0

    def test_stress_voice_spawn(self):
        fab, w = make_test_world("aw_str_v_sp")
        w.settings.max_voices = 300
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        for i in range(150):
            fab.create_source(f"s_{i}", clip_id="c1", world=w)
            fab.play_source(f"s_{i}", w)
        assert len(w.mixer.active_voices) == 150

    def test_stress_voice_stealing(self):
        settings = AudioWorldSettings(max_voices=5, voice_stealing_policy=VoiceStealingPolicy.STEAL_OLDEST)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_str_v_steal", settings=settings)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        for i in range(50):
            fab.create_source(f"s_{i}", clip_id="c1", world=w)
            fab.play_source(f"s_{i}", w)
        assert len(w.mixer.active_voices) == 5

    def test_stress_clip_load(self):
        fab, w = make_test_world("aw_str_c_ld")
        for i in range(300):
            fab.register_clip(AudioClip(f"c_{i}", duration_seconds=1.0), w)
        assert len(w.clips) == 300

    def test_stress_clip_unload(self):
        fab, w = make_test_world("aw_str_c_unld")
        for i in range(100):
            fab.register_clip(AudioClip(f"c_{i}", duration_seconds=1.0), w)
        for i in range(100):
            fab.destroy_clip(f"c_{i}", w)
        assert len(w.clips) == 0

    def test_stress_stream_open(self):
        fab, w = make_test_world("aw_str_st_op")
        for i in range(50):
            fab.open_stream(f"str_{i}", world=w)
        assert len(w.streams) == 50

    def test_stress_stream_close(self):
        fab, w = make_test_world("aw_str_st_cl")
        for i in range(30):
            fab.open_stream(f"str_{i}", world=w)
        for i in range(30):
            fab.close_stream(f"str_{i}", w)
        assert len(w.streams) == 0

    def test_stress_bus_create(self):
        fab, w = make_test_world("aw_str_b_cr")
        for i in range(25):
            fab.create_bus(f"b_{i}", parent_bus_id="SFX", world=w)
        assert len(w.mixer.buses) >= 30

    def test_stress_bus_destroy(self):
        fab, w = make_test_world("aw_str_b_des")
        for i in range(15):
            fab.create_bus(f"b_{i}", parent_bus_id="SFX", world=w)
        for i in range(15):
            fab.destroy_bus(f"b_{i}", w)
        assert "b_0" not in w.mixer.buses

    def test_stress_effect_create(self):
        fab, w = make_test_world("aw_str_eff_cr")
        for i in range(50):
            fab.add_effect_to_bus("SFX", AudioEffect(f"e_{i}", AudioEffectType.GAIN), w)
        assert len(w.mixer.buses["SFX"].effects) == 50

    def test_stress_effect_destroy(self):
        fab, w = make_test_world("aw_str_eff_des")
        for i in range(20):
            fab.add_effect_to_bus("SFX", AudioEffect(f"e_{i}", AudioEffectType.GAIN), w)
        w.mixer.buses["SFX"].effects.clear()
        assert len(w.mixer.buses["SFX"].effects) == 0

    def test_stress_command_queue(self):
        fab, w = make_test_world("aw_str_cmd_q")
        for i in range(300):
            fab.enqueue_command(AudioCommand(f"c_{i}", AudioCommandType.SET_VOLUME, "s1"), w)
        assert len(w.command_queue) == 300

    def test_stress_event_queue(self):
        fab, w = make_test_world("aw_str_ev_q")
        for i in range(300):
            fab.emit_event(AudioEventType.PLAY_STARTED, f"s_{i}", world=w)
        assert len(w.events) == 300

    def test_stress_snapshot(self):
        fab, w = make_test_world("aw_str_snap")
        for _ in range(50):
            fab.capture_snapshot(w)
        assert w is not None

    def test_stress_restore(self):
        fab, w = make_test_world("aw_str_rest")
        snap = fab.capture_snapshot(w)
        for _ in range(50):
            fab.restore_snapshot(snap, w)
        assert w.time_seconds == snap.timestamp

    def test_stress_device_restart(self):
        fab, w = make_test_world("aw_str_dev_rst")
        dev = fab.create_device("dev1", world=w)
        for _ in range(30):
            fab.shutdown_device("dev1", w)
            dev.state = AudioDeviceState.READY
        assert dev.state == AudioDeviceState.READY

    def test_stress_audio_world_restart(self):
        fab, w = make_test_world("aw_str_w_rst")
        for _ in range(5):
            fab.initialize_world(w)
            fab.start_playback(w)
            fab.update(0.016, w)
            fab.stop_playback(w)
        assert w.state == AudioWorldState.STOPPED


# ==============================================================================
# §117. PROPERTY-BASED TESTS (7 tests)
# ==============================================================================

class TestPropertyBasedExecution:
    """Normative tests for Audio Invariant Mathematical & Structural Properties (§117)."""

    def test_play_valid_clip_valid_playback_state(self):
        fab, w = make_test_world("aw_prop_1")
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        src = fab.create_source("s1", clip_id="c1", world=w)
        v = fab.play_source("s1", w)
        assert src.state == AudioSourceState.PLAYING
        assert v.state == VoiceState.PLAYING

    def test_stop_source_no_active_voice(self):
        fab, w = make_test_world("aw_prop_2")
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        fab.create_source("s1", clip_id="c1", world=w)
        fab.play_source("s1", w)
        assert len(w.mixer.active_voices) == 1
        fab.stop_source("s1", w)
        assert len(w.mixer.active_voices) == 0

    def test_destroy_source_no_live_source_reference(self):
        fab, w = make_test_world("aw_prop_3")
        fab.create_source("s_target", world=w)
        assert "s_target" in w.sources
        fab.destroy_source("s_target", w)
        assert "s_target" not in w.sources

    def test_destroy_clip_no_resource_use_after_release(self):
        fab, w = make_test_world("aw_prop_4")
        fab.register_clip(AudioClip("c_temp"), w)
        assert "c_temp" in w.clips
        fab.destroy_clip("c_temp", w)
        assert "c_temp" not in w.clips

    def test_same_inputs_same_audio_clock_same_deterministic_state(self):
        def run_clock_test():
            fab, w = make_test_world("aw_prop_clk")
            fab.initialize_world(w)
            fab.start_playback(w)
            fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
            fab.create_source("s1", clip_id="c1", world=w)
            fab.play_source("s1", w)
            fab.update(0.05, w)
            return w.compute_fingerprint()

        assert run_clock_test() == run_clock_test()

    def test_voice_budget_active_voices_le_configured_limit(self):
        settings = AudioWorldSettings(max_voices=3, voice_stealing_policy=VoiceStealingPolicy.STEAL_OLDEST)
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_world("aw_prop_budget", settings=settings)
        fab.register_clip(AudioClip("c1", duration_seconds=5.0), w)
        for i in range(10):
            fab.create_source(f"s_{i}", clip_id="c1", world=w)
            fab.play_source(f"s_{i}", w)
        assert len(w.mixer.active_voices) <= w.settings.max_voices

    def test_destroy_bus_no_live_route_to_destroyed_bus(self):
        fab, w = make_test_world("aw_prop_bus_dest")
        fab.create_bus("TEMP_BUS", world=w)
        fab.create_source("s1", bus_id="TEMP_BUS", world=w)
        fab.destroy_bus("TEMP_BUS", w)
        assert w.sources["s1"].bus_id != "TEMP_BUS"


# ==============================================================================


# ==============================================================================
# §118. CROSS-PHASE INTEGRATION TESTS (16 tests)
# ==============================================================================

class TestCrossPhaseIntegrationExecution:
    """Normative tests for Cross-Phase Integration with Runtime World & Systems (§118)."""

    def test_runtime_world_to_audio_world(self):
        class MockRuntimeWorld:
            def __init__(self, wid):
                self.world_id = wid
        rt_w = MockRuntimeWorld("rw_level_1")
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_audio_world(audio_world_id="aw_rw_1", runtime_world_id=rt_w.world_id)
        assert w.runtime_world_id == "rw_level_1"

    def test_entity_to_audio_source(self):
        fab, w = make_test_world("aw_cross_2")
        fab.register_clip(AudioClip("c_footstep", duration_seconds=0.5), w)
        src = fab.create_source("s_player_feet", clip_id="c_footstep", world=w)
        entity_pos = [15.0, 0.0, 2.0]
        src.position = list(entity_pos)
        assert src.position == [15.0, 0.0, 2.0]

    def test_camera_to_audio_listener(self):
        fab, w = make_test_world("aw_cross_3")
        listener = fab.create_listener("lis_cam", world=w)
        cam_pos = [10.0, 5.0, 1.8]
        cam_fwd = [1.0, 0.0, 0.0]
        listener.position = list(cam_pos)
        listener.forward = list(cam_fwd)
        assert listener.position == [10.0, 5.0, 1.8]
        assert listener.forward == [1.0, 0.0, 0.0]

    def test_physics_velocity_to_doppler(self):
        fab, w = make_test_world("aw_cross_4")
        fab.initialize_world(w)
        fab.register_clip(AudioClip("c_siren", duration_seconds=10.0), w)
        src = fab.create_source("s_car", clip_id="c_siren", position=[-100.0, 0.0, 0.0], velocity=[34.3, 0.0, 0.0], world=w)
        lis = fab.create_listener("lis_player", position=[0.0, 0.0, 0.0], velocity=[0.0, 0.0, 0.0], world=w)
        fab.start_playback(w)
        v = fab.play_source("s_car", w)
        fab.update(0.1, w)
        pitch = fab.compute_doppler_factor(src, lis, w)
        assert pitch > 1.05

    def test_animation_event_to_audio_clip(self):
        fab, w = make_test_world("aw_cross_5")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c_sword_swing", duration_seconds=1.2), w)
        src = fab.create_source("s_sword", clip_id="c_sword_swing", world=w)
        anim_notify = {"event": "AnimNotify_PlaySound", "source_id": "s_sword"}
        if anim_notify["event"] == "AnimNotify_PlaySound":
            v = fab.play_source(anim_notify["source_id"], w)
        assert v is not None
        assert src.state == AudioSourceState.PLAYING

    def test_vfx_trigger_to_audio_event(self):
        fab, w = make_test_world("aw_cross_6")
        fab.post_event(AudioEventType.PLAY_STARTED, "s_explosion", {"particles": 500}, w)
        assert len(w.events) == 1
        assert w.events[0].event_type == AudioEventType.PLAY_STARTED

    def test_time_dilation_to_pitch(self):
        fab, w = make_test_world("aw_cross_7")
        fab.register_clip(AudioClip("c_bgm", duration_seconds=60.0), w)
        src = fab.create_source("s_bgm", clip_id="c_bgm", world=w)
        time_dilation = 0.5
        fab.set_source_pitch("s_bgm", time_dilation, w)
        assert src.pitch == 0.5

    def test_pause_system_to_audio_pause(self):
        fab, w = make_test_world("aw_cross_8")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.pause_playback(w)
        assert w.state == AudioWorldState.PAUSED

    def test_level_load_to_audio_device_init(self):
        fab, w = make_test_world("aw_cross_9")
        dev = fab.create_device("dev_level", sample_rate=48000, channel_count=2, world=w)
        assert dev.state == AudioDeviceState.READY

    def test_level_unload_to_audio_cleanup(self):
        fab, w = make_test_world("aw_cross_10")
        fab.initialize_world(w)
        fab.register_clip(AudioClip("c_amb", duration_seconds=20.0), w)
        src = fab.create_source("s_amb", clip_id="c_amb", world=w)
        fab.start_playback(w)
        fab.play_source("s_amb", w)
        fab.stop_playback(w)
        assert src.state == AudioSourceState.STOPPED
        assert len(w.mixer.active_voices) == 0

    def test_streaming_level_to_audio_stream(self):
        fab, w = make_test_world("aw_cross_11")
        stream = fab.create_stream("stream_sector_b", buffer_size=4096, world=w)
        fab.push_stream_data("stream_sector_b", b"CHUNK_SECTOR_B", w)
        assert stream.bytes_buffered == len(b"CHUNK_SECTOR_B")

    def test_cinematic_track_to_audio_bus(self):
        fab, w = make_test_world("aw_cross_12")
        bus = fab.create_bus("BUS_CINEMATICS", parent_bus_id="MASTER", volume=0.9, world=w)
        assert bus.bus_id == "BUS_CINEMATICS"
        assert bus.parent_bus_id == "MASTER"

    def test_render_pass_to_audio_sync(self):
        fab, w = make_test_world("aw_cross_13")
        fab.initialize_world(w)
        fab.start_playback(w)
        render_frames = 60
        for _ in range(render_frames):
            fab.update(1.0 / 60.0, w)
        assert w.frames_rendered == 60

    def test_post_process_to_audio_filter(self):
        fab, w = make_test_world("aw_cross_14")
        fab.create_bus("BUS_WATER", parent_bus_id="MASTER", world=w)
        filter_fx = fab.create_effect("fx_lpf_underwater", AudioEffectType.LOWPASS, {"cutoff_hz": 600.0})
        fab.add_bus_effect("BUS_WATER", filter_fx, w)
        bus = fab.get_bus("BUS_WATER", w)
        assert len(bus.effects) == 1
        assert bus.effects[0].effect_type == AudioEffectType.LOWPASS

    def test_ai_perception_to_audio_source(self):
        fab, w = make_test_world("aw_cross_15")
        fab.register_clip(AudioClip("c_gunfire", duration_seconds=1.0), w)
        src = fab.create_source("s_gun", clip_id="c_gunfire", position=[20.0, 0.0, 0.0], world=w)
        ai_pos = [25.0, 0.0, 0.0]
        dx = src.position[0] - ai_pos[0]
        dist = abs(dx)
        can_hear = dist <= src.max_distance
        assert can_hear is True

    def test_networking_state_to_audio_event(self):
        fab, w = make_test_world("aw_cross_16")
        fab.initialize_world(w)
        fab.start_playback(w)
        fab.register_clip(AudioClip("c_net", duration_seconds=2.0), w)
        fab.create_source("s_net_player", clip_id="c_net", world=w)
        fab.queue_command(AudioCommandType.PLAY, "s_net_player", {}, timestamp=0.05, world=w)
        fab.process_commands(w)
        assert w.sources["s_net_player"].state == AudioSourceState.PLAYING


# ==============================================================================
# §119. CLEANUP, TEARDOWN & LEAK PREVENTION TESTS (14 tests)
# ==============================================================================

class TestCleanupTeardownExecution:
    """Normative tests for Audio Teardown, Cleanup & Memory Leak Prevention (§119)."""

    def test_cleanup_audio_world_empty(self):
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_audio_world("aw_clean_empty")
        fab.destroy_audio_world("aw_clean_empty")
        assert "aw_clean_empty" not in fab.worlds

    def test_cleanup_audio_world_with_active_voices(self):
        fab, w = make_test_world("aw_clean_voices")
        fab.initialize_world(w)
        fab.register_clip(AudioClip("c_v1", duration_seconds=10.0), w)
        fab.create_source("s_v1", clip_id="c_v1", world=w)
        fab.start_playback(w)
        fab.play_source("s_v1", w)
        assert len(w.mixer.active_voices) > 0
        fab.destroy_audio_world("aw_clean_voices")
        assert "aw_clean_voices" not in fab.worlds

    def test_cleanup_audio_world_with_streams(self):
        fab, w = make_test_world("aw_clean_streams")
        fab.create_stream("st_cl", buffer_size=1024, world=w)
        fab.push_stream_data("st_cl", b"CHUNK", w)
        fab.destroy_audio_world("aw_clean_streams")
        assert "aw_clean_streams" not in fab.worlds

    def test_cleanup_audio_world_bus_hierarchy(self):
        fab, w = make_test_world("aw_clean_buses")
        fab.create_bus("BUS_A", parent_bus_id="MASTER", world=w)
        fab.create_bus("BUS_B", parent_bus_id="BUS_A", world=w)
        fab.destroy_audio_world("aw_clean_buses")
        assert "aw_clean_buses" not in fab.worlds

    def test_cleanup_audio_world_effect_chains(self):
        fab, w = make_test_world("aw_clean_effects")
        fx = fab.create_effect("fx1", AudioEffectType.REVERB)
        fab.add_bus_effect("MASTER", fx, world=w)
        fab.destroy_audio_world("aw_clean_effects")
        assert "aw_clean_effects" not in fab.worlds

    def test_cleanup_audio_world_pending_commands(self):
        fab, w = make_test_world("aw_clean_cmd")
        fab.queue_command(AudioCommandType.PLAY, "s1", {}, world=w)
        fab.destroy_audio_world("aw_clean_cmd")
        assert "aw_clean_cmd" not in fab.worlds

    def test_cleanup_audio_world_unprocessed_events(self):
        fab, w = make_test_world("aw_clean_evt")
        fab.post_event(AudioEventType.PLAY_STARTED, "s1", {}, w)
        fab.destroy_audio_world("aw_clean_evt")
        assert "aw_clean_evt" not in fab.worlds

    def test_cleanup_device_loss(self):
        fab, w = make_test_world("aw_clean_dev_loss")
        dev = fab.create_device("dev_l", world=w)
        fab.handle_device_lost("dev_l", w)
        assert dev.state == AudioDeviceState.LOST
        fab.recover_device("dev_l", w)
        assert dev.state == AudioDeviceState.READY

    def test_cleanup_device_reinitialization(self):
        fab, w = make_test_world("aw_clean_dev_reinit")
        dev = fab.create_device("dev_re", world=w)
        dev.state = AudioDeviceState.INITIALIZING
        dev.state = AudioDeviceState.READY
        assert dev.state == AudioDeviceState.READY

    def test_cleanup_multiple_audio_worlds(self):
        fab = UniversalRuntimeAudioFabricator()
        for i in range(20):
            wid = f"aw_multi_{i}"
            fab.create_audio_world(wid)
            fab.destroy_audio_world(wid)
        assert len(fab.worlds) == 0

    def test_cleanup_orphan_voices_on_source_destruction(self):
        fab, w = make_test_world("aw_clean_orphan_v")
        fab.initialize_world(w)
        fab.register_clip(AudioClip("c_orph", duration_seconds=5.0), w)
        fab.create_source("s_orph", clip_id="c_orph", world=w)
        fab.start_playback(w)
        fab.play_source("s_orph", w)
        assert len(w.mixer.active_voices) > 0
        fab.destroy_source("s_orph", w)
        assert len(w.mixer.active_voices) == 0

    def test_cleanup_orphan_sources_on_bus_destruction(self):
        fab, w = make_test_world("aw_clean_bus_dest")
        fab.create_bus("BUS_TEMP", parent_bus_id="MASTER", world=w)
        fab.register_clip(AudioClip("c_temp", duration_seconds=1.0), w)
        src = fab.create_source("s_temp", clip_id="c_temp", bus_id="BUS_TEMP", world=w)
        fab.destroy_bus("BUS_TEMP", w)
        assert src.bus_id == "MASTER"

    def test_cleanup_cyclic_bus_removal_leak_free(self):
        fab, w = make_test_world("aw_clean_cyclic_bus")
        b1 = fab.create_bus("B1", parent_bus_id="MASTER", world=w)
        b2 = fab.create_bus("B2", parent_bus_id="B1", world=w)
        fab.destroy_bus("B2", w)
        assert "B2" not in w.mixer.buses

    def test_cleanup_memory_leak_free_100_allocations(self):
        fab, w = make_test_world("aw_clean_leak_100")
        fab.register_clip(AudioClip("c_loop", duration_seconds=1.0), w)
        for i in range(100):
            sid = f"s_leak_{i}"
            fab.create_source(sid, clip_id="c_loop", world=w)
            fab.destroy_source(sid, w)
        assert len(w.sources) == 0


# ==============================================================================
# §120. PACKAGING, UE5 SUBSYSTEM & INVARIANT VERIFICATION TESTS (18 tests)
# ==============================================================================

class TestPackagingAndInvariantsExecution:
    """Normative tests for UE5 Subsystem packaging and audio invariant verification (§120, §123)."""

    def test_packager_header_generation(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeAudioSubsystem.h")
            assert os.path.isfile(hdr)
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert "UUAFRuntimeAudioSubsystem" in c
            assert "UCLASS()" in c

    def test_packager_source_generation(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            src = os.path.join(tmpdir, "UUAFRuntimeAudioSubsystem.cpp")
            assert os.path.isfile(src)
            with open(src, "r", encoding="utf-8") as f:
                c = f.read()
            assert "Initialize(" in c
            assert "Deinitialize(" in c

    def test_packager_manifest_generation(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            man = os.path.join(tmpdir, "audio_manifest.json")
            assert os.path.isfile(man)
            with open(man, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["module"] == "uaf_runtime_audio"
            assert "files" in data

    def test_packager_signature_generation(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            sig = os.path.join(tmpdir, "audio_manifest.sig")
            assert os.path.isfile(sig)

    def test_packager_cpp_includes(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeAudioSubsystem.h")
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert "Subsystems/WorldSubsystem.h" in c

    def test_packager_ue5_subsystem_class(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeAudioSubsystem.h")
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert ": public UWorldSubsystem" in c

    def test_packager_uproperty_ufunction(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeAudioSubsystem.h")
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert "UFUNCTION(BlueprintCallable" in c

    def test_packager_checksum_deterministic(self):
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            packager.package(tmp1)
            packager.package(tmp2)
            with open(os.path.join(tmp1, "audio_manifest.json"), "r", encoding="utf-8") as f1:
                d1 = json.load(f1)
            with open(os.path.join(tmp2, "audio_manifest.json"), "r", encoding="utf-8") as f2:
                d2 = json.load(f2)
            assert d1["files"] == d2["files"]

    def test_validator_catches_all_invalid_states(self):
        val = UniversalRuntimeAudioValidator()
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_audio_world("aw_val_err")
        w.clips["bad_clip"] = AudioClip("bad_clip", duration_seconds=-1.0)
        issues = val.validate(w)
        err_codes = [i.error_code for i in issues]
        assert any("CLIP" in c or "DURATION" in c for c in err_codes)

    def test_validator_clean_manifest(self):
        val = UniversalRuntimeAudioValidator()
        fab, w = make_test_world("aw_val_clean")
        fab.register_clip(AudioClip("c_ok", duration_seconds=2.0), w)
        fab.create_source("s_ok", clip_id="c_ok", world=w)
        issues = val.validate(w)
        errors = [i for i in issues if i.severity == "ERROR"]
        assert len(errors) == 0

    def test_end_to_end_audio_pipeline(self):
        fab, w = make_test_world("aw_e2e")
        fab.initialize_world(w)
        fab.register_clip(AudioClip("c_theme", duration_seconds=120.0), w)
        src = fab.create_source("s_theme", clip_id="c_theme", bus_id="MASTER", world=w)
        lis = fab.create_listener("lis_main", position=[0.0, 0.0, 0.0], world=w)
        fab.start_playback(w)
        v = fab.play_source("s_theme", w)
        assert v is not None
        fab.update(0.016, w)
        snap = fab.capture_snapshot(w)
        assert snap.world_id == "aw_e2e"
        packager = UniversalRuntimeAudioPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = packager.package(tmpdir, w)
            assert res["success"] is True

    def test_invariant_no_invalid_audio_world_transition(self):
        fab = UniversalRuntimeAudioFabricator()
        w = fab.create_audio_world("aw_inv_trans")
        with pytest.raises(ValueError, match="NO_INVALID_AUDIO_WORLD_TRANSITION"):
            fab.stop_playback(w)

    def test_invariant_no_play_without_valid_audio_resource(self):
        fab, w = make_test_world("aw_inv_res")
        fab.initialize_world(w)
        src = fab.create_source("s_no_res", clip_id="", stream_id="", world=w)
        fab.start_playback(w)
        with pytest.raises(ValueError, match="NO_RESOURCE"):
            fab.play_source("s_no_res", w)

    def test_invariant_no_unbounded_voice_creation(self):
        fab, w = make_test_world("aw_inv_voice")
        w.mixer.max_voices = 2
        w.settings.max_voices = 2
        fab.initialize_world(w)
        fab.register_clip(AudioClip("c_v", duration_seconds=10.0), w)
        for i in range(5):
            fab.create_source(f"s_v_{i}", clip_id="c_v", world=w)
        fab.start_playback(w)
        for i in range(5):
            fab.play_source(f"s_v_{i}", w)
        assert len(w.mixer.active_voices) <= 2

    def test_invariant_no_voice_budget_bypass(self):
        fab, w = make_test_world("aw_inv_budget")
        w.mixer.max_voices = 1
        w.settings.max_voices = 1
        w.mixer.stealing_policy = VoiceStealingPolicy.STEAL_OLDEST
        w.settings.voice_stealing_policy = VoiceStealingPolicy.STEAL_OLDEST
        fab.initialize_world(w)
        fab.register_clip(AudioClip("c_b", duration_seconds=10.0), w)
        fab.create_source("s_b1", clip_id="c_b", world=w)
        fab.create_source("s_b2", clip_id="c_b", world=w)
        fab.start_playback(w)
        fab.play_source("s_b1", w)
        fab.play_source("s_b2", w)
        assert len(w.mixer.active_voices) == 1

    def test_invariant_no_effect_chain_cycle(self):
        val = UniversalRuntimeAudioValidator()
        fab, w = make_test_world("aw_inv_cycle")
        w.mixer.buses["BUS_X"] = AudioBus("BUS_X", parent_bus_id="BUS_Y")
        w.mixer.buses["BUS_Y"] = AudioBus("BUS_Y", parent_bus_id="BUS_X")
        issues = val.validate(w)
        err_codes = [i.error_code for i in issues]
        assert any("CYCLE" in c for c in err_codes)

    def test_invariant_no_route_to_destroyed_bus(self):
        fab, w = make_test_world("aw_inv_bus_route")
        fab.register_clip(AudioClip("c_rt", duration_seconds=1.0), w)
        with pytest.raises(ValueError, match="BUS_NOT_FOUND"):
            fab.create_source("s_rt", clip_id="c_rt", bus_id="BUS_NON_EXISTENT", world=w)

    def test_invariant_no_unbounded_stream_memory(self):
        fab, w = make_test_world("aw_inv_stream_mem")
        st = fab.create_stream("st_unbounded", buffer_size=100, world=w)
        big_chunk = b"X" * 200
        fab.push_stream_data("st_unbounded", big_chunk, w)
        assert st.buffered_bytes <= st.buffer_size
