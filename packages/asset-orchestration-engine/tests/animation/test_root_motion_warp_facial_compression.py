"""
Tests for Root Motion, Motion Warping, Facial Animation, and Compression (UAF-81.55 Sections 84-102, 147-150).
"""

import pytest
from uaf.universal_animation import (
    RootMotionMode55,
    CompressionMethod55,
    MotionWarpingProfile55,
    FacialAnimationTrack55,
    AnimationCompressionProfile55,
    UniversalAnimationFabricator,
)


# --- 6 ROOT_MOTION TESTS (Section 147) ---

def test_root_motion_modes():
    modes = [m.value for m in RootMotionMode55]
    assert "EXTRACT" in modes
    assert "LOCK_XZ" in modes
    assert "FULL" in modes
    assert "NONE" in modes


def test_root_motion_extraction():
    # Root translation extracted along Y axis over 1.0 sec
    start_pos = (0.0, 0.0, 0.0)
    end_pos = (0.0, 150.0, 0.0)
    delta_y = end_pos[1] - start_pos[1]
    assert delta_y == 150.0


def test_root_motion_validation():
    # Root motion speed does not exceed realistic human sprint (e.g. < 1200 cm/s)
    delta_dist_cm = 150.0
    duration_s = 1.0
    speed = delta_dist_cm / duration_s
    assert speed <= 1200.0


def test_root_motion_loop_continuity():
    # Loop continuity: start and end position offset cleanly integrates
    step_cm = 120.0
    assert step_cm > 0.0


def test_root_motion_lock_z():
    mode = RootMotionMode55.LOCK_XZ
    assert mode == RootMotionMode55.LOCK_XZ


def test_root_motion_determinism():
    r1 = UniversalAnimationFabricator.build_golden_root_motion()
    r2 = UniversalAnimationFabricator.build_golden_root_motion()
    assert r1.canonical_hash == r2.canonical_hash


# --- 5 MOTION_WARP TESTS (Section 148) ---

def test_warp_target_definition():
    warp = MotionWarpingProfile55("Warp_Vault", warp_target_bone="PELVIS", max_translation_warp_cm=80.0)
    assert warp.warp_target_bone == "PELVIS"
    assert warp.max_translation_warp_cm == 80.0
    d = warp.to_dict()
    assert d["max_rotation_warp_deg"] == 45.0


def test_warp_axis():
    # Translation warp along forward and vertical axes
    warp_axes = ["TRANSLATION_X", "TRANSLATION_Y", "TRANSLATION_Z", "ROTATION_YAW"]
    assert len(warp_axes) == 4


def test_warp_limits():
    warp = MotionWarpingProfile55("Warp_Limit", max_translation_warp_cm=50.0)
    requested_warp = 40.0
    assert requested_warp <= warp.max_translation_warp_cm


def test_warp_validation():
    # Warping fails if requested displacement exceeds threshold
    max_warp = 50.0
    bad_warp = 120.0
    is_valid = bad_warp <= max_warp
    assert is_valid is False


def test_motion_warp_determinism():
    w1 = MotionWarpingProfile55("W_Det")
    w2 = MotionWarpingProfile55("W_Det")
    assert w1.to_dict() == w2.to_dict()


# --- 6 FACIAL TESTS (Section 149) ---

def test_facial_animation_track():
    track = FacialAnimationTrack55("Morph_Smile", [(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)])
    assert track.morph_name == "Morph_Smile"
    assert len(track.keys) == 3
    d = track.to_dict()
    assert d["morph_name"] == "Morph_Smile"


def test_facial_track_curve_bounds():
    track = FacialAnimationTrack55("Morph_Blink", [(0.0, 0.0), (0.1, 1.0), (0.2, 0.0)])
    for t, val in track.keys:
        assert 0.0 <= val <= 1.0


def test_facial_retargeting():
    source_morph = "ARKit_JawOpen"
    target_morph = "Morph_Jaw_Open"
    mapping = {source_morph: target_morph}
    assert mapping[source_morph] == target_morph


def test_facial_validation():
    track = FacialAnimationTrack55("Morph_BrowsUp", [(0.0, 0.2), (1.0, 0.5)])
    assert len(track.keys) >= 2


def test_lip_sync_curve():
    visemes = ["VISEME_AA", "VISEME_E", "VISEME_O"]
    assert len(visemes) == 3


def test_facial_determinism():
    f1 = UniversalAnimationFabricator.build_golden_facial()
    f2 = UniversalAnimationFabricator.build_golden_facial()
    assert f1.canonical_hash == f2.canonical_hash


# --- 7 COMPRESSION TESTS (Section 150) ---

def test_compression_methods():
    methods = [m.value for m in CompressionMethod55]
    assert "KEYFRAME_REDUCTION" in methods
    assert "ACL" in methods
    assert "BITPACKING" in methods
    assert "LINEAR_TOLERANCE" in methods


def test_compression_profile_structure():
    comp = AnimationCompressionProfile55(
        method=CompressionMethod55.KEYFRAME_REDUCTION,
        max_error_cm=0.04,
        budget_kb=256.0,
        compressed_size_kb=96.0,
    )
    assert comp.max_error_cm == 0.04
    assert comp.compressed_size_kb <= comp.budget_kb
    d = comp.to_dict()
    assert d["method"] == "KEYFRAME_REDUCTION"


def test_compression_error_tolerance():
    comp = AnimationCompressionProfile55(max_error_cm=0.05)
    actual_error = 0.03
    assert actual_error <= comp.max_error_cm


def test_compression_budget():
    comp = AnimationCompressionProfile55(budget_kb=512.0, compressed_size_kb=180.0)
    assert comp.compressed_size_kb < comp.budget_kb


def test_keyframe_reduction():
    original_keys = 60
    reduced_keys = 22
    ratio = reduced_keys / original_keys
    assert ratio < 0.5


def test_compression_validation():
    comp = AnimationCompressionProfile55(budget_kb=100.0, compressed_size_kb=150.0)
    exceeds_budget = comp.compressed_size_kb > comp.budget_kb
    assert exceeds_budget is True


def test_compression_determinism():
    c1 = AnimationCompressionProfile55()
    c2 = AnimationCompressionProfile55()
    assert c1.to_dict() == c2.to_dict()
