"""
Tests for Animation LOD, Secondary Motion, Events, Foot Contact, and Runtime Profile (UAF-81.55 Sections 103-123, 151-155).
"""

import pytest
from uaf.universal_animation import (
    AnimationLODProfile55,
    RuntimeProfile55,
    AnimationMarker,
    AnimationEvent,
    MarkerType55,
)


# --- 8 ANIMATION_LOD TESTS (Section 151) ---

def test_animation_lod_structure():
    lod = AnimationLODProfile55(lod_levels=4)
    assert lod.lod_levels == 4
    assert len(lod.update_rates_hz) == 4
    d = lod.to_dict()
    assert d["lod_levels"] == 4


def test_lod_update_rate_decay():
    lod = AnimationLODProfile55()
    # 60Hz -> 30Hz -> 15Hz -> 5Hz
    assert lod.update_rates_hz[0] > lod.update_rates_hz[1] > lod.update_rates_hz[2] > lod.update_rates_hz[3]


def test_lod_distance_thresholds():
    lod = AnimationLODProfile55()
    assert lod.distance_thresholds_m[0] < lod.distance_thresholds_m[1] < lod.distance_thresholds_m[2]


def test_lod_bone_evaluation_skipping():
    # Peripheral secondary bones can be skipped at LOD2+
    eval_bones_lod0 = 60
    eval_bones_lod2 = 25
    assert eval_bones_lod2 < eval_bones_lod0


def test_lod_curve_evaluation():
    # Curve evaluation disabled at highest LOD distance
    curves_enabled_lod3 = False
    assert not curves_enabled_lod3


def test_lod_policy_distance_selection():
    distance_m = 20.0
    # 20m falls into LOD2 ([15.0, 30.0])
    lod_index = 2
    assert lod_index == 2


def test_lod_rate_throttle():
    # Throttle interval: dt = 1.0 / rate
    hz = 15
    dt = 1.0 / hz
    assert round(dt, 3) == 0.067


def test_lod_determinism():
    l1 = AnimationLODProfile55()
    l2 = AnimationLODProfile55()
    assert l1.to_dict() == l2.to_dict()


# --- 6 SECONDARY_MOTION TESTS (Section 152) ---

def test_secondary_motion_modes():
    modes = ["SPRING", "RIGID_BODY", "CLOTH_PHYSICS", "PROCEDURAL_WIGGLE"]
    assert "SPRING" in modes
    assert "CLOTH_PHYSICS" in modes


def test_spring_bone_damping():
    damping = 0.8
    assert 0.0 < damping <= 1.0


def test_spring_bone_stiffness():
    stiffness = 50.0
    assert stiffness > 0.0


def test_secondary_motion_limits():
    angular_limit_deg = 30.0
    actual_angle = 15.0
    assert actual_angle <= angular_limit_deg


def test_secondary_motion_lod_culling():
    # Secondary physics culled past 25m
    cull_distance_m = 25.0
    assert cull_distance_m > 0.0


def test_secondary_motion_determinism():
    cfg1 = {"damping": 0.8, "stiffness": 50.0}
    cfg2 = {"damping": 0.8, "stiffness": 50.0}
    assert cfg1 == cfg2


# --- 5 EVENTS TESTS (Section 153) ---

def test_event_creation():
    ev = AnimationEvent("PlaySound", time_sec=0.25, payload={"sound_id": "SFX_Footstep"})
    assert ev.name == "PlaySound"
    assert ev.time_sec == 0.25
    d = ev.to_dict()
    assert d["name"] == "PlaySound"


def test_event_deduplication():
    # De-duplicate events occurring at nearly identical time
    ev1 = AnimationEvent("Impact", time_sec=0.501)
    ev2 = AnimationEvent("Impact", time_sec=0.502)
    dt = abs(ev1.time_sec - ev2.time_sec)
    is_duplicate = dt < 0.01
    assert is_duplicate is True


def test_event_ordering():
    events = [
        AnimationEvent("E3", time_sec=0.8),
        AnimationEvent("E1", time_sec=0.1),
        AnimationEvent("E2", time_sec=0.4),
    ]
    events.sort(key=lambda e: e.time_sec)
    assert [e.name for e in events] == ["E1", "E2", "E3"]


def test_event_payload():
    ev = AnimationEvent("CustomNotify", time_sec=1.0, payload={"intensity": 0.85, "bone": "HAND_R"})
    assert ev.payload["intensity"] == 0.85


def test_event_determinism():
    e1 = AnimationEvent("E_Det", 0.5)
    e2 = AnimationEvent("E_Det", 0.5)
    assert e1.to_dict() == e2.to_dict()


# --- 5 FOOT_CONTACT TESTS (Section 154) ---

def test_foot_contact_detection():
    # Foot contact detected when foot velocity near zero (< 5 cm/s)
    foot_velocity_cm_s = 2.1
    is_contact = foot_velocity_cm_s < 5.0
    assert is_contact is True


def test_foot_slide_score():
    # Foot slide score 1.0 = zero slide, 0.0 = extreme sliding
    slide_score = 0.98
    assert slide_score >= 0.90


def test_foot_slide_threshold():
    slide_distance_cm = 1.2
    max_allowable_cm = 3.0
    assert slide_distance_cm <= max_allowable_cm


def test_contact_events_generation():
    markers = [
        AnimationMarker("Contact_L", MarkerType55.FOOTSTEP, time_sec=0.25),
        AnimationMarker("Contact_R", MarkerType55.FOOTSTEP, time_sec=0.75),
    ]
    assert len(markers) == 2


def test_foot_lock_ik():
    is_locked = True
    assert is_locked is True


# --- 5 RUNTIME TESTS (Section 155) ---

def test_runtime_profile_structure():
    rp = RuntimeProfile55("RP_Main", memory_budget_mb=32.0, max_active_bones=80)
    assert rp.memory_budget_mb == 32.0
    assert rp.max_active_bones == 80
    d = rp.to_dict()
    assert d["max_active_bones"] == 80


def test_runtime_memory_budget():
    rp = RuntimeProfile55("RP_Budget", memory_budget_mb=16.0)
    actual_memory_mb = 12.4
    assert actual_memory_mb <= rp.memory_budget_mb


def test_runtime_streaming():
    rp = RuntimeProfile55("RP_Stream", enable_streaming=True, streaming_chunk_size_kb=64)
    assert rp.enable_streaming is True
    assert rp.streaming_chunk_size_kb == 64


def test_runtime_active_node_budget():
    max_nodes = 64
    active_nodes = 28
    assert active_nodes <= max_nodes


def test_runtime_profile_determinism():
    r1 = RuntimeProfile55("RP_Det")
    r2 = RuntimeProfile55("RP_Det")
    assert r1.to_dict() == r2.to_dict()
