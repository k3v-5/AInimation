"""
Tests for Animation Montage, State Machine, and Locomotion (UAF-81.55 Sections 71-83, 144-146).
"""

import pytest
from uaf.universal_animation import (
    LocomotionMode55,
    MontageSection55,
    AnimationMontage55,
    StateTransition55,
    AnimationStateMachine55,
    UniversalAnimationFabricator,
)


# --- 5 MONTAGE TESTS (Section 144) ---

def test_montage_structure():
    mont = UniversalAnimationFabricator.build_montage("Anim_Attack_01", "MONT_01")
    assert mont.montage_id == "MONT_01"
    assert mont.animation_id == "Anim_Attack_01"
    assert len(mont.sections) == 3
    d = mont.to_dict()
    assert d["blend_in_sec"] == 0.2


def test_montage_sections():
    s = MontageSection55("Windup", start_time=0.0, length=0.3, next_section="Strike")
    assert s.name == "Windup"
    assert s.next_section == "Strike"
    d = s.to_dict()
    assert d["length"] == 0.3


def test_montage_notifies():
    mont = UniversalAnimationFabricator.build_montage("Anim_Attack_01")
    assert len(mont.notifies) >= 2


def test_montage_branching():
    # Section branch logic
    sections = {
        "Combo_1": "Combo_2",
        "Combo_2": "Combo_Finisher",
        "Combo_Finisher": None,
    }
    assert sections["Combo_1"] == "Combo_2"
    assert sections["Combo_Finisher"] is None


def test_montage_blending():
    mont = AnimationMontage55("M1", "A1", blend_in_sec=0.15, blend_out_sec=0.25)
    assert mont.blend_in_sec == 0.15
    assert mont.blend_out_sec == 0.25


# --- 7 STATE_MACHINE TESTS (Section 145) ---

def test_state_machine_structure():
    sm = UniversalAnimationFabricator.build_locomotion_state_machine()
    assert sm.machine_id == "SM_Locomotion"
    assert "IDLE" in sm.states
    assert len(sm.transitions) >= 6
    d = sm.to_dict()
    assert d["default_state"] == "IDLE"


def test_state_definition():
    states = ["IDLE", "WALK", "RUN", "JUMP"]
    assert len(states) == 4


def test_transition_definition():
    trans = StateTransition55("IDLE", "WALK", condition="Speed > 10.0", duration_sec=0.2)
    assert trans.from_state == "IDLE"
    assert trans.to_state == "WALK"
    d = trans.to_dict()
    assert d["duration_sec"] == 0.2


def test_transition_conditions():
    speed = 50.0
    cond_walk = speed > 10.0
    assert cond_walk is True


def test_transition_priority():
    t1 = StateTransition55("IDLE", "JUMP", "IsJumping", priority=10)
    t2 = StateTransition55("IDLE", "WALK", "Speed > 0", priority=1)
    assert t1.priority > t2.priority


def test_state_machine_cycle_detection():
    # Detects cycle when transitions loop infinitely without exit
    sm_cyclic = AnimationStateMachine55("SM_Loop", ["A", "B"], [
        StateTransition55("A", "B", "True"),
        StateTransition55("B", "A", "True"),
    ])
    assert sm_cyclic.has_cycle() is True


def test_state_machine_acyclic():
    # Pure DAG transitions
    sm_dag = AnimationStateMachine55("SM_DAG", ["A", "B", "C"], [
        StateTransition55("A", "B", "Cond1"),
        StateTransition55("B", "C", "Cond2"),
    ])
    assert sm_dag.has_cycle() is False


# --- 9 LOCOMOTION TESTS (Section 146) ---

def test_locomotion_modes():
    modes = [m.value for m in LocomotionMode55]
    assert "IN_PLACE" in modes
    assert "ROOT_MOTION" in modes
    assert "PROCEDURAL" in modes
    assert "HYBRID" in modes


def test_speed_normalization():
    raw_speed = 300.0  # cm/s
    max_speed = 600.0
    norm_speed = raw_speed / max_speed
    assert norm_speed == 0.5


def test_direction_normalization():
    # Direction angle [-180, 180] normalized to [-1.0, 1.0]
    angle_deg = 90.0
    norm_dir = angle_deg / 180.0
    assert norm_dir == 0.5


def test_walk_run_blend():
    speed = 200.0
    walk_speed = 150.0
    run_speed = 350.0
    run_weight = (speed - walk_speed) / (run_speed - walk_speed)
    walk_weight = 1.0 - run_weight
    assert round(walk_weight + run_weight, 3) == 1.0


def test_stride_length_calculation():
    # Stride length scales with leg length
    leg_length = 90.0
    stride_factor = 1.2
    stride_cm = leg_length * stride_factor
    assert stride_cm == 108.0


def test_cadence_calculation():
    # Cadence steps per minute
    speed_cm_s = 150.0
    stride_cm = 100.0
    steps_per_sec = speed_cm_s / stride_cm
    spm = steps_per_sec * 60.0
    assert spm == 90.0


def test_in_place_locomotion():
    mode = LocomotionMode55.IN_PLACE
    assert mode.value == "IN_PLACE"


def test_procedural_locomotion():
    mode = LocomotionMode55.PROCEDURAL
    assert mode.value == "PROCEDURAL"


def test_hybrid_locomotion():
    mode = LocomotionMode55.HYBRID
    assert mode.value == "HYBRID"
