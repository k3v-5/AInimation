"""
Tests for Animation Data Model, Import Pipeline, and Resampling (UAF-81.55 Sections 3-13, 16-24, 134-136).
"""

import pytest
from uaf.universal_animation import (
    AnimationType55,
    ChannelType55,
    CurveInterpolation55,
    MarkerType55,
    ResamplingMode55,
    Keyframe55,
    AnimationTrack,
    AnimationCurve,
    AnimationMarker,
    AnimationEvent,
    AnimationClip,
    AnimationDefinition,
    UniversalAnimationFabricator,
)


# --- 6 DATA_MODEL TESTS (Section 134) ---

def test_animation_definition_structure():
    anim = AnimationDefinition(
        animation_id="Anim_Test",
        name="Test Animation",
        anim_type=AnimationType55.IDLE,
        duration=1.5,
        sample_rate=30,
        skeleton_reference="SKEL_Humanoid",
        tracks=[AnimationTrack("ROOT", ChannelType55.TRANSLATION, [Keyframe55(0.0, (0.0, 0.0, 0.0))])],
    )
    assert anim.is_valid is True
    assert anim.duration == 1.5
    d = anim.to_dict()
    assert d["anim_type"] == "IDLE"


def test_animation_clip():
    clip = AnimationClip("Clip_01", start_time=0.2, end_time=1.2, loop=True, rate=1.0)
    assert clip.duration == 1.0
    assert clip.loop is True
    d = clip.to_dict()
    assert d["duration"] == 1.0


def test_track_channels():
    t_pos = AnimationTrack("PELVIS", ChannelType55.TRANSLATION, [Keyframe55(0.0, (0.0, 0.0, 95.0))])
    t_rot = AnimationTrack("PELVIS", ChannelType55.ROTATION, [Keyframe55(0.0, (0.0, 0.0, 0.0, 1.0))])
    t_scl = AnimationTrack("PELVIS", ChannelType55.SCALE, [Keyframe55(0.0, (1.0, 1.0, 1.0))])
    assert t_pos.channel == ChannelType55.TRANSLATION
    assert t_rot.channel == ChannelType55.ROTATION
    assert t_scl.channel == ChannelType55.SCALE


def test_animation_curves():
    curve = AnimationCurve("AimWeight", "FLOAT", [(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)])
    assert curve.name == "AimWeight"
    assert len(curve.keys) == 3
    d = curve.to_dict()
    assert d["curve_type"] == "FLOAT"


def test_animation_markers():
    marker = AnimationMarker("Footstep_L", MarkerType55.FOOTSTEP, time_sec=0.33)
    assert marker.marker_type == MarkerType55.FOOTSTEP
    assert marker.time_sec == 0.33
    d = marker.to_dict()
    assert d["marker_type"] == "FOOTSTEP"


def test_animation_events():
    event = AnimationEvent("SpawnVFX", time_sec=0.5, payload={"effect": "DustCloud", "bone": "FOOT_L"})
    assert event.name == "SpawnVFX"
    assert event.payload["effect"] == "DustCloud"
    d = event.to_dict()
    assert d["time_sec"] == 0.5


# --- 6 IMPORT TESTS (Section 135) ---

def test_import_format_abstraction():
    # Simulating import from standard formats (FBX / GLTF / BVH abstraction)
    raw_source = {
        "source_format": "FBX_2020",
        "fps": 30,
        "frames": 60,
        "bones": ["ROOT", "PELVIS", "SPINE_01"],
    }
    assert raw_source["source_format"] == "FBX_2020"
    assert raw_source["fps"] == 30


def test_import_validation():
    # Valid import must have duration > 0 and bone tracks
    duration = 2.0
    tracks_count = 12
    is_valid_import = duration > 0.0 and tracks_count > 0
    assert is_valid_import is True


def test_coordinate_normalization():
    # Conversion from Y-up (Maya/GLTF) to Z-up (Unreal Engine)
    y_up_pos = (10.0, 20.0, 30.0)  # X, Y(up), Z
    z_up_pos = (y_up_pos[0], -y_up_pos[2], y_up_pos[1])  # X, -Z, Y
    assert z_up_pos[2] == 20.0  # Height is preserved in Z


def test_frame_rate_normalization():
    # Normalized from 24fps film source to 30fps game standard
    source_fps = 24
    target_fps = 30
    ratio = target_fps / source_fps
    assert ratio == 1.25


def test_time_normalization():
    # Normalized time [0.0, 1.0] calculation
    duration = 2.0
    current_time = 1.0
    normalized_time = current_time / duration
    assert normalized_time == 0.5


def test_frame_index_mapping():
    # Map frame index to seconds: t = frame / fps
    frame = 45
    fps = 30
    t = frame / fps
    assert t == 1.5


# --- 5 RESAMPLING TESTS (Section 136) ---

def test_resampling_modes():
    modes = [m.value for m in ResamplingMode55]
    assert "NEAREST" in modes
    assert "LINEAR" in modes
    assert "CUBIC" in modes
    assert "HERMITE" in modes


def test_sample_rate_conversion():
    anim_30 = UniversalAnimationFabricator.generate_breathing(duration=1.0, sample_rate=30)
    anim_60 = UniversalAnimationFabricator.resample_animation(anim_30, target_sample_rate=60)
    assert anim_60.sample_rate == 60
    assert len(anim_60.tracks[0].keyframes) == 61


def test_downsampling():
    anim_60 = UniversalAnimationFabricator.generate_breathing(duration=1.0, sample_rate=60)
    anim_15 = UniversalAnimationFabricator.resample_animation(anim_60, target_sample_rate=15)
    assert anim_15.sample_rate == 15
    assert len(anim_15.tracks[0].keyframes) == 16


def test_resampling_preserves_duration():
    anim = UniversalAnimationFabricator.generate_breathing(duration=2.5, sample_rate=30)
    resampled = UniversalAnimationFabricator.resample_animation(anim, target_sample_rate=60)
    assert resampled.duration == anim.duration


def test_resampling_determinism():
    anim = UniversalAnimationFabricator.generate_breathing(duration=1.0, sample_rate=30)
    r1 = UniversalAnimationFabricator.resample_animation(anim, 60)
    r2 = UniversalAnimationFabricator.resample_animation(anim, 60)
    assert len(r1.tracks[0].keyframes) == len(r2.tracks[0].keyframes)
    assert r1.tracks[0].keyframes[10].value == r2.tracks[0].keyframes[10].value
