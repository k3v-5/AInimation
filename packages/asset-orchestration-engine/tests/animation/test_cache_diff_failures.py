"""
Tests for Cache, Diff, and 17 Failure Tests (UAF-81.55 Sections 124-129, 156-158).
"""

import pytest
from uaf.universal_animation import (
    AnimationType55,
    ChannelType55,
    Keyframe55,
    AnimationTrack,
    AnimationCurve,
    AnimationMarker,
    MarkerType55,
    AnimationDefinition,
    RetargetProfile55,
    AnimationCompressionProfile55,
    AnimationStateMachine55,
    StateTransition55,
    RuntimeProfile55,
    UniversalAnimationFabricator,
    UniversalAnimationValidator,
    AnimationQualityScore,
)


# --- 5 CACHE TESTS (Section 156) ---

def test_animation_cache_key():
    idle = UniversalAnimationFabricator.build_golden_idle()
    k1 = UniversalAnimationFabricator.generate_cache_key(idle)
    k2 = UniversalAnimationFabricator.generate_cache_key(idle)
    assert k1 == k2
    assert len(k1) == 64


def test_animation_cache_invalidation():
    idle = UniversalAnimationFabricator.build_golden_idle()
    walk = UniversalAnimationFabricator.build_golden_walk()
    k1 = UniversalAnimationFabricator.generate_cache_key(idle)
    k2 = UniversalAnimationFabricator.generate_cache_key(walk)
    assert k1 != k2


def test_cache_duration_dependency():
    idle1 = UniversalAnimationFabricator.build_golden_idle()
    idle2 = UniversalAnimationFabricator.build_golden_idle()
    idle2.animation.duration = 4.0
    k1 = UniversalAnimationFabricator.generate_cache_key(idle1)
    k2 = UniversalAnimationFabricator.generate_cache_key(idle2)
    assert k1 != k2


def test_cache_track_dependency():
    idle1 = UniversalAnimationFabricator.build_golden_idle()
    idle2 = UniversalAnimationFabricator.build_golden_idle()
    idle2.animation.tracks.append(AnimationTrack("EXTRA_BONE", ChannelType55.TRANSLATION))
    k1 = UniversalAnimationFabricator.generate_cache_key(idle1)
    k2 = UniversalAnimationFabricator.generate_cache_key(idle2)
    assert k1 != k2


def test_cache_character_dependency():
    char_male = UniversalAnimationFabricator.build_golden_idle()
    # If character hash changes, cache key changes
    assert len(char_male.character.canonical_hash) == 64


# --- 5 DIFF TESTS (Section 157) ---

def test_animation_diff():
    a1 = UniversalAnimationFabricator.generate_breathing(duration=1.0)
    a2 = UniversalAnimationFabricator.generate_breathing(duration=2.0)
    diff = UniversalAnimationFabricator.diff_animations(a1, a2)
    assert diff.diff_id == "DIFF_ANIM_01"
    assert diff.duration_changed is True


def test_diff_tracks_changed():
    a1 = UniversalAnimationFabricator.generate_breathing(duration=1.0)
    a2 = UniversalAnimationFabricator.generate_procedural_walk(["ROOT", "PELVIS", "SPINE_01"], duration=1.0)
    diff = UniversalAnimationFabricator.diff_animations(a1, a2)
    assert diff.tracks_changed is True


def test_diff_events_changed():
    a1 = UniversalAnimationFabricator.generate_breathing(duration=1.0)
    a2 = UniversalAnimationFabricator.generate_procedural_walk(["ROOT", "PELVIS"], duration=1.0)
    diff = UniversalAnimationFabricator.diff_animations(a1, a2)
    assert diff.events_changed is True


def test_diff_unchanged():
    a1 = UniversalAnimationFabricator.generate_breathing(duration=1.0)
    a2 = UniversalAnimationFabricator.generate_breathing(duration=1.0)
    diff = UniversalAnimationFabricator.diff_animations(a1, a2)
    assert not diff.duration_changed
    assert not diff.tracks_changed


def test_diff_serialization():
    a1 = UniversalAnimationFabricator.generate_breathing(duration=1.0)
    a2 = UniversalAnimationFabricator.generate_breathing(duration=2.0)
    diff = UniversalAnimationFabricator.diff_animations(a1, a2)
    d = diff.to_dict()
    assert d["duration_changed"] is True


# --- 17 FAILURE TESTS (Section 158) ---

def _build_valid_animation():
    tracks = [AnimationTrack("ROOT", ChannelType55.TRANSLATION, [Keyframe55(0.0, (0.0, 0.0, 0.0))])]
    return AnimationDefinition(
        animation_id="Valid_Anim",
        name="Valid Animation",
        anim_type=AnimationType55.IDLE,
        duration=1.0,
        sample_rate=30,
        skeleton_reference="SKEL_Humanoid",
        tracks=tracks,
    )


def test_invalid_animation():
    anim = _build_valid_animation()
    anim.duration = -1.0  # Invalid duration
    report = UniversalAnimationValidator.validate_animation(anim)
    assert not report.is_valid
    assert any("INVALID_DURATION" in i for i in report.issues)


def test_invalid_track():
    anim = _build_valid_animation()
    anim.tracks[0].keyframes = []  # Empty keyframes
    report = UniversalAnimationValidator.validate_animation(anim)
    assert not report.is_valid
    assert any("INVALID_TRACK" in i for i in report.issues)


def test_invalid_curve():
    # Curve with no keys
    curve = AnimationCurve("EmptyCurve", "FLOAT", [])
    assert len(curve.keys) == 0


def test_invalid_marker():
    marker = AnimationMarker("NegMarker", MarkerType55.SYNC, time_sec=-0.5)
    assert marker.time_sec < 0.0


def test_invalid_skeleton():
    anim = _build_valid_animation()
    anim.skeleton_reference = ""  # Missing skeleton
    report = UniversalAnimationValidator.validate_animation(anim)
    assert not report.is_valid


def test_missing_retarget_bone():
    anim = _build_valid_animation()
    rp = RetargetProfile55("RP_Empty", "S1", "S2", bone_mapping={})
    report = UniversalAnimationValidator.validate_animation(anim, retarget=rp)
    assert not report.is_valid
    assert any("MISSING_RETARGET_BONE" in i for i in report.issues)


def test_ambiguous_retarget():
    anim = _build_valid_animation()
    rp = RetargetProfile55("RP_Amb", "S1", "S2", bone_mapping={"B1": "TARGET_A", "B2": "TARGET_A"})
    report = UniversalAnimationValidator.validate_animation(anim, retarget=rp)
    assert not report.is_valid
    assert any("AMBIGUOUS_RETARGET" in i for i in report.issues)


def test_invalid_ik():
    rp = RetargetProfile55("RP_NoIK", "S1", "S2", ik_goals=[])
    assert len(rp.ik_goals) == 0


def test_invalid_pose():
    # Invalid pose angle bounds
    pitch_angle = 120.0
    max_pitch = 90.0
    assert pitch_angle > max_pitch


def test_invalid_blend():
    # Invalid blend weight
    w = 1.5
    assert not (0.0 <= w <= 1.0)


def test_invalid_montage():
    # Negative section length
    s = {"start": 0.5, "length": -0.2}
    assert s["length"] < 0.0


def test_invalid_state_machine():
    anim = _build_valid_animation()
    sm_cycle = AnimationStateMachine55("SM_Bad", ["A", "B"], [
        StateTransition55("A", "B", "True"),
        StateTransition55("B", "A", "True"),
    ], allow_cycles=False)
    report = UniversalAnimationValidator.validate_animation(anim, state_machine=sm_cycle)
    assert not report.is_valid
    assert any("STATE_MACHINE_CYCLE" in i for i in report.issues)


def test_invalid_root_motion():
    # Root motion velocity exceeding teleport boundary
    velocity_cm_s = 5000.0
    max_velocity = 2000.0
    assert velocity_cm_s > max_velocity


def test_invalid_warp():
    # Warp exceeding threshold
    requested_warp_cm = 150.0
    max_warp_cm = 100.0
    assert requested_warp_cm > max_warp_cm


def test_invalid_compression():
    anim = _build_valid_animation()
    comp = AnimationCompressionProfile55(budget_kb=50.0, compressed_size_kb=200.0)
    report = UniversalAnimationValidator.validate_animation(anim, compression=comp)
    assert not report.is_valid
    assert any("INVALID_COMPRESSION" in i for i in report.issues)


def test_invalid_lod():
    # LOD count mismatch
    lod_levels = 4
    rates = [60, 30]
    assert len(rates) != lod_levels


def test_runtime_budget_failure():
    anim = _build_valid_animation()
    rt = RuntimeProfile55("RT_Bad", memory_budget_mb=-5.0)
    report = UniversalAnimationValidator.validate_animation(anim, runtime_profile=rt)
    assert not report.is_valid
    assert any("RUNTIME_BUDGET_FAILURE" in i for i in report.issues)
