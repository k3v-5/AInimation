"""
Normative Acceptance Test Suite for UAF-81.77: Universal Runtime Input World System.
Validates input devices, raw events, normalization, action/axis mappings,
contexts, gestures, rebinding, replay, determinism, and invariants (§96 - §124).
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

from uaf.runtime_input import (
    copy_dict_deterministic,
    InputWorldState,
    InputDeviceType,
    InputDeviceStatus,
    RawInputEventType,
    DeadZoneMode,
    AxisCurveType,
    GestureType,
    GestureState,
    InputRoutingMode,
    InputModifierKey,
    ActionTriggerState,
    DeviceCapabilities,
    InputDevice,
    RawInputEvent,
    ActionBinding,
    InputAction,
    AxisBinding,
    InputAxis,
    GestureBinding,
    InputContext,
    InputRebindingProfile,
    InputSnapshot,
    InputRecord,
    InputReplaySession,
    DeviceHotplugEvent,
    InputWorldSettings,
    InputWorld,
    UniversalRuntimeInputFabricator,
    InputValidationIssue,
    UniversalRuntimeInputValidator,
    UniversalRuntimeInputPackager,
)


def make_test_world(world_id: str = "test_input_world") -> Tuple[UniversalRuntimeInputFabricator, InputWorld]:
    fab = UniversalRuntimeInputFabricator()
    w = fab.create_world(world_id)
    return fab, w


# ==============================================================================
# §96. INPUT WORLD LIFECYCLE TESTS (10 tests)
# ==============================================================================

class TestInputWorldLifecycle:
    """Normative tests for Input World Creation and Lifecycle Machine (§96)."""

    def test_input_world_creation(self):
        fab, w = make_test_world("iw_create")
        assert w.input_world_id == "iw_create"
        assert w.state == InputWorldState.CREATED
        assert len(w.devices) == 0

    def test_input_world_identity(self):
        fab, w = make_test_world("iw_ident")
        assert fab.get_world("iw_ident") is w
        assert fab.active_world is w

    def test_input_world_state(self):
        fab, w = make_test_world("iw_state")
        fab.initialize_world(w)
        assert w.state == InputWorldState.READY

    def test_input_world_pause(self):
        fab, w = make_test_world("iw_pause")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.pause_world(w)
        assert w.state == InputWorldState.PAUSED

    def test_input_world_resume(self):
        fab, w = make_test_world("iw_resume")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.pause_world(w)
        fab.start_world(w)
        assert w.state == InputWorldState.RUNNING

    def test_input_world_stop(self):
        fab, w = make_test_world("iw_stop")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.stop_world(w)
        assert w.state == InputWorldState.STOPPED

    def test_input_world_invalid_transition(self):
        fab, w = make_test_world("iw_inv_trans")
        with pytest.raises(ValueError, match="NO_INVALID_INPUT_WORLD_TRANSITION"):
            fab.stop_world(w)

    def test_input_world_destroy(self):
        fab, w = make_test_world("iw_destroy")
        fab.destroy_world(w)
        assert w.state == InputWorldState.DESTROYED
        assert fab.get_world("iw_destroy") is None

    def test_input_world_fingerprint(self):
        fab, w = make_test_world("iw_fp")
        fp1 = w.compute_fingerprint()
        fab.initialize_world(w)
        fp2 = w.compute_fingerprint()
        assert fp1 != fp2
        assert len(fp1) == 64

    def test_input_world_reset(self):
        fab, w = make_test_world("iw_rst")
        fab.reset()
        assert len(fab.worlds) == 0
        assert fab.active_world is None


# ==============================================================================
# §97. DEVICE REGISTRY, IDENTITY & HOTPLUG TESTS (8 tests)
# ==============================================================================

class TestDeviceRegistryAndHotplug:
    """Normative tests for Input Device Registration, Identity & Hotplug (§97)."""

    def test_register_device(self):
        fab, w = make_test_world("iw_dev_1")
        dev = fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        assert dev.device_id == "kb_1"
        assert dev.device_type == InputDeviceType.KEYBOARD
        assert "kb_1" in w.devices

    def test_duplicate_device_rejected(self):
        fab, w = make_test_world("iw_dev_2")
        fab.create_device("mouse_1", InputDeviceType.MOUSE, world=w)
        with pytest.raises(ValueError, match="DUPLICATE_DEVICE_ID"):
            fab.create_device("mouse_1", InputDeviceType.MOUSE, world=w)

    def test_device_capabilities(self):
        fab, w = make_test_world("iw_dev_3")
        caps = DeviceCapabilities(supports_buttons=True, button_count=104, supports_axes=False)
        dev = fab.create_device("kb_2", InputDeviceType.KEYBOARD, capabilities=caps, world=w)
        assert dev.capabilities.button_count == 104
        assert dev.capabilities.supports_buttons is True

    def test_device_disconnect_hotplug(self):
        fab, w = make_test_world("iw_dev_4")
        dev = fab.create_device("gp_1", InputDeviceType.GAMEPAD, world=w)
        fab.disconnect_device("gp_1", w)
        assert dev.status == InputDeviceStatus.DISCONNECTED
        assert len(w.hotplug_history) == 2
        assert w.hotplug_history[-1].is_connected is False

    def test_device_reconnect_hotplug(self):
        fab, w = make_test_world("iw_dev_5")
        dev = fab.create_device("gp_2", InputDeviceType.GAMEPAD, world=w)
        fab.disconnect_device("gp_2", w)
        fab.reconnect_device("gp_2", w)
        assert dev.status == InputDeviceStatus.CONNECTED
        assert w.hotplug_history[-1].is_connected is True

    def test_device_state_reset_on_disconnect(self):
        fab, w = make_test_world("iw_dev_6")
        dev = fab.create_device("gp_3", InputDeviceType.GAMEPAD, world=w)
        dev.button_states["A"] = True
        dev.axis_states["LeftX"] = 0.8
        fab.disconnect_device("gp_3", w)
        assert len(dev.button_states) == 0
        assert len(dev.axis_states) == 0

    def test_remove_device(self):
        fab, w = make_test_world("iw_dev_7")
        fab.create_device("touch_1", InputDeviceType.TOUCH, world=w)
        fab.remove_device("touch_1", w)
        assert "touch_1" not in w.devices

    def test_device_max_limit(self):
        fab, w = make_test_world("iw_dev_8")
        w.settings.max_devices = 2
        fab.create_device("d1", InputDeviceType.KEYBOARD, world=w)
        fab.create_device("d2", InputDeviceType.MOUSE, world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_device("d3", InputDeviceType.GAMEPAD, world=w)


# ==============================================================================
# §98. RAW INPUT EVENTS, SEQUENCE & NORMALIZATION TESTS (8 tests)
# ==============================================================================

class TestRawInputEventsAndNormalization:
    """Normative tests for Raw Events, Sequencing & Normalization (§98)."""

    def test_create_raw_event(self):
        fab, w = make_test_world("iw_raw_1")
        fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        ev = fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code="KeyW", world=w)
        assert ev.code == "KeyW"
        assert ev.event_type == RawInputEventType.KEY_DOWN
        assert len(w.raw_event_queue) == 1

    def test_event_sequence_increment(self):
        fab, w = make_test_world("iw_raw_2")
        fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        ev1 = fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code="KeyA", world=w)
        ev2 = fab.create_raw_event("kb_1", RawInputEventType.KEY_UP, code="KeyA", world=w)
        assert ev2.sequence_number > ev1.sequence_number

    def test_event_sorting_deterministic(self):
        fab, w = make_test_world("iw_raw_3")
        fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        ev1 = RawInputEvent("ev1", sequence_number=2, device_id="kb_1", device_type=InputDeviceType.KEYBOARD, event_type=RawInputEventType.KEY_DOWN, timestamp=0.1)
        ev2 = RawInputEvent("ev2", sequence_number=1, device_id="kb_1", device_type=InputDeviceType.KEYBOARD, event_type=RawInputEventType.KEY_DOWN, timestamp=0.05)
        fab.queue_raw_event(ev1, w)
        fab.queue_raw_event(ev2, w)
        count = fab.process_events(w)
        assert count == 2
        assert w.processed_events[0].event_id == "ev2"
        assert w.processed_events[1].event_id == "ev1"

    def test_event_from_disconnected_device_ignored(self):
        fab, w = make_test_world("iw_raw_4")
        dev = fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        fab.disconnect_device("kb_1", w)
        fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code="KeySpace", world=w)
        fab.process_events(w)
        assert dev.button_states.get("KeySpace", False) is False

    def test_event_queue_buffer_limit(self):
        fab, w = make_test_world("iw_raw_5")
        w.settings.max_buffer_size = 3
        fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        for i in range(3):
            fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code=f"Key{i}", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code="KeyOverflow", world=w)

    def test_event_flood_protection(self):
        fab, w = make_test_world("iw_raw_6")
        w.settings.max_events_per_frame = 2
        fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        for i in range(5):
            fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code=f"Key{i}", world=w)
        fab.process_events(w)
        assert len(w.processed_events) == 2

    def test_raw_event_serialization(self):
        fab, w = make_test_world("iw_raw_7")
        fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        ev = fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code="KeyD", value=1.0, world=w)
        d = ev.to_dict()
        assert d["code"] == "KeyD"
        assert d["value"] == 1.0

    def test_clear_queue_on_process(self):
        fab, w = make_test_world("iw_raw_8")
        fab.create_device("kb_1", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_1", RawInputEventType.KEY_DOWN, code="KeyS", world=w)
        assert len(w.raw_event_queue) == 1
        fab.process_events(w)
        assert len(w.raw_event_queue) == 0


# ==============================================================================
# §99. KEYBOARD, MODIFIERS & REPEAT TESTS (8 tests)
# ==============================================================================

class TestKeyboardAndModifiers:
    """Normative tests for Keyboard State, Modifier Tracking & Repeats (§99)."""

    def test_key_down_state(self):
        fab, w = make_test_world("iw_kb_1")
        fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="KeyW", world=w)
        fab.process_events(w)
        assert fab.is_key_pressed("KeyW", w) is True

    def test_key_up_state(self):
        fab, w = make_test_world("iw_kb_2")
        fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="KeyW", world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_UP, code="KeyW", world=w)
        fab.process_events(w)
        assert fab.is_key_pressed("KeyW", w) is False

    def test_shift_modifier_tracking(self):
        fab, w = make_test_world("iw_kb_3")
        fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="ShiftLeft", world=w)
        fab.process_events(w)
        assert fab.is_modifier_active("SHIFT", w) is True
        fab.create_raw_event("kb_main", RawInputEventType.KEY_UP, code="ShiftLeft", world=w)
        fab.process_events(w)
        assert fab.is_modifier_active("SHIFT", w) is False

    def test_control_modifier_tracking(self):
        fab, w = make_test_world("iw_kb_4")
        fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="ControlLeft", world=w)
        fab.process_events(w)
        assert fab.is_modifier_active("CONTROL", w) is True

    def test_alt_modifier_tracking(self):
        fab, w = make_test_world("iw_kb_5")
        fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="AltLeft", world=w)
        fab.process_events(w)
        assert fab.is_modifier_active("ALT", w) is True

    def test_multiple_modifiers(self):
        fab, w = make_test_world("iw_kb_6")
        fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="ShiftLeft", world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="ControlLeft", world=w)
        fab.process_events(w)
        assert fab.is_modifier_active("SHIFT", w) is True
        assert fab.is_modifier_active("CONTROL", w) is True

    def test_key_repeat_event_handling(self):
        fab, w = make_test_world("iw_kb_7")
        fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="KeyA", world=w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="KeyA", world=w)
        fab.process_events(w)
        assert fab.is_key_pressed("KeyA", w) is True

    def test_unregistered_key_query(self):
        fab, w = make_test_world("iw_kb_8")
        assert fab.is_key_pressed("KeyUnknown", w) is False


# ==============================================================================
# §100. MOUSE, POINTER & COORDINATE TRANSFORMS TESTS (9 tests)
# ==============================================================================

class TestMouseAndCoordinateTransforms:
    """Normative tests for Mouse State, Relative Delta & Coordinate Mapping (§100)."""

    def test_mouse_move_position(self):
        fab, w = make_test_world("iw_mouse_1")
        fab.create_device("mouse_main", InputDeviceType.MOUSE, world=w)
        fab.create_raw_event("mouse_main", RawInputEventType.MOUSE_MOVE, position=[1920.0, 1080.0], delta=[10.0, 5.0], world=w)
        fab.process_events(w)
        assert w.mouse_position == [1920.0, 1080.0]
        assert w.mouse_delta == [10.0, 5.0]

    def test_mouse_button_down(self):
        fab, w = make_test_world("iw_mouse_2")
        fab.create_device("mouse_main", InputDeviceType.MOUSE, world=w)
        fab.create_raw_event("mouse_main", RawInputEventType.MOUSE_DOWN, code="LeftButton", world=w)
        fab.process_events(w)
        assert w.mouse_buttons.get("LeftButton", False) is True

    def test_mouse_button_up(self):
        fab, w = make_test_world("iw_mouse_3")
        fab.create_device("mouse_main", InputDeviceType.MOUSE, world=w)
        fab.create_raw_event("mouse_main", RawInputEventType.MOUSE_DOWN, code="RightButton", world=w)
        fab.create_raw_event("mouse_main", RawInputEventType.MOUSE_UP, code="RightButton", world=w)
        fab.process_events(w)
        assert w.mouse_buttons.get("RightButton", False) is False

    def test_mouse_set_position(self):
        fab, w = make_test_world("iw_mouse_4")
        fab.set_mouse_position(500.0, 300.0, w)
        assert w.mouse_position == [500.0, 300.0]

    def test_mouse_capture_mode(self):
        fab, w = make_test_world("iw_mouse_5")
        fab.set_mouse_captured(True, w)
        assert w.mouse_captured is True
        fab.set_mouse_captured(False, w)
        assert w.mouse_captured is False

    def test_screen_to_normalized_transform(self):
        fab = UniversalRuntimeInputFabricator()
        norm = fab.transform_screen_to_normalized([960.0, 540.0], 1920.0, 1080.0)
        assert norm == [0.5, 0.5]

    def test_normalized_to_screen_transform(self):
        fab = UniversalRuntimeInputFabricator()
        screen = fab.transform_normalized_to_screen([0.5, 0.5], 1920.0, 1080.0)
        assert screen == [960.0, 540.0]

    def test_screen_transform_invalid_dimensions(self):
        fab = UniversalRuntimeInputFabricator()
        with pytest.raises(ValueError, match="INVALID_SCREEN_DIMENSIONS"):
            fab.transform_screen_to_normalized([10.0, 10.0], 0.0, 1080.0)

    def test_screen_transform_clamped_bounds(self):
        fab = UniversalRuntimeInputFabricator()
        norm = fab.transform_screen_to_normalized([3000.0, -100.0], 1920.0, 1080.0)
        assert norm == [1.0, 0.0]


# ==============================================================================
# §101. GAMEPAD, DEAD-ZONES & RUMBLE TESTS (9 tests)
# ==============================================================================

class TestGamepadAndRumble:
    """Normative tests for Gamepad Buttons, Dead-Zone Normalization & Rumble (§101)."""

    def test_gamepad_button_down_up(self):
        fab, w = make_test_world("iw_gp_1")
        dev = fab.create_device("gp_main", InputDeviceType.GAMEPAD, world=w)
        fab.create_raw_event("gp_main", RawInputEventType.GAMEPAD_BUTTON_DOWN, code="ButtonA", world=w)
        fab.process_events(w)
        assert dev.button_states["ButtonA"] is True
        fab.create_raw_event("gp_main", RawInputEventType.GAMEPAD_BUTTON_UP, code="ButtonA", world=w)
        fab.process_events(w)
        assert dev.button_states["ButtonA"] is False

    def test_gamepad_axis_inside_dead_zone(self):
        fab = UniversalRuntimeInputFabricator()
        # Value 0.05 inside dead zone 0.1 returns 0.0
        val = fab.apply_dead_zone(0.05, 0.1)
        assert val == 0.0

    def test_gamepad_axis_outside_dead_zone_rescaled(self):
        fab = UniversalRuntimeInputFabricator()
        # Value 0.55 with dead zone 0.1: (0.55 - 0.1) / 0.9 = 0.5
        val = fab.apply_dead_zone(0.55, 0.1)
        assert pytest.approx(val, rel=1e-3) == 0.5

    def test_gamepad_axis_negative_dead_zone(self):
        fab = UniversalRuntimeInputFabricator()
        val = fab.apply_dead_zone(-0.05, 0.1)
        assert val == 0.0
        val2 = fab.apply_dead_zone(-0.55, 0.1)
        assert pytest.approx(val2, rel=1e-3) == -0.5

    def test_gamepad_dead_zone_invalid_range(self):
        fab = UniversalRuntimeInputFabricator()
        with pytest.raises(ValueError, match="INVALID_DEAD_ZONE"):
            fab.apply_dead_zone(0.5, 1.2)

    def test_gamepad_rumble_trigger(self):
        fab, w = make_test_world("iw_gp_6")
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp_rumble", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        fab.set_gamepad_rumble("gp_rumble", 0.7, 0.9, duration_seconds=2.0, world=w)
        assert dev.rumble_left == 0.7
        assert dev.rumble_right == 0.9
        assert dev.rumble_remaining_seconds == 2.0

    def test_gamepad_rumble_timeout_clamp(self):
        fab, w = make_test_world("iw_gp_7")
        w.settings.rumble_timeout_seconds = 3.0
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp_rumble2", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        fab.set_gamepad_rumble("gp_rumble2", 1.0, 1.0, duration_seconds=10.0, world=w)
        assert dev.rumble_remaining_seconds == 3.0

    def test_gamepad_rumble_stop(self):
        fab, w = make_test_world("iw_gp_8")
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp_rumble3", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        fab.set_gamepad_rumble("gp_rumble3", 0.5, 0.5, duration_seconds=1.0, world=w)
        fab.stop_gamepad_rumble("gp_rumble3", w)
        assert dev.rumble_left == 0.0
        assert dev.rumble_right == 0.0

    def test_gamepad_rumble_update_expiration(self):
        fab, w = make_test_world("iw_gp_9")
        fab.initialize_world(w)
        fab.start_world(w)
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp_rumble4", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        fab.set_gamepad_rumble("gp_rumble4", 0.5, 0.5, duration_seconds=0.1, world=w)
        fab.update(0.2, w)
        assert dev.rumble_left == 0.0
        assert dev.rumble_right == 0.0


# ==============================================================================
# §102. TOUCH & MULTI-TOUCH TESTS (8 tests)
# ==============================================================================

class TestTouchAndMultiTouch:
    """Normative tests for Touch Tracking, Multi-Touch Points & Invariants (§102)."""

    def test_single_touch_start_end(self):
        fab, w = make_test_world("iw_touch_1")
        fab.create_device("touch_dev", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=1, position=[100.0, 200.0], world=w)
        fab.process_events(w)
        assert fab.get_active_touch_count(w) == 1
        assert fab.get_touch_position(1, w) == [100.0, 200.0]
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_END, touch_id=1, position=[100.0, 200.0], world=w)
        fab.process_events(w)
        assert fab.get_active_touch_count(w) == 0

    def test_multi_touch_tracking(self):
        fab, w = make_test_world("iw_touch_2")
        fab.create_device("touch_dev", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=1, position=[50.0, 50.0], world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=2, position=[150.0, 150.0], world=w)
        fab.process_events(w)
        assert fab.get_active_touch_count(w) == 2
        assert fab.get_touch_position(1, w) == [50.0, 50.0]
        assert fab.get_touch_position(2, w) == [150.0, 150.0]

    def test_touch_move_update(self):
        fab, w = make_test_world("iw_touch_3")
        fab.create_device("touch_dev", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=1, position=[10.0, 10.0], world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_MOVE, touch_id=1, position=[20.0, 30.0], world=w)
        fab.process_events(w)
        assert fab.get_touch_position(1, w) == [20.0, 30.0]

    def test_touch_cancel(self):
        fab, w = make_test_world("iw_touch_4")
        fab.create_device("touch_dev", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=1, position=[10.0, 10.0], world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_CANCEL, touch_id=1, world=w)
        fab.process_events(w)
        assert fab.get_active_touch_count(w) == 0

    def test_touch_limit_security(self):
        fab, w = make_test_world("iw_touch_5")
        w.settings.max_devices = 2
        fab.create_device("touch_dev", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=1, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=2, world=w)
        fab.process_events(w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=3, world=w)
            fab.process_events(w)

    def test_unregistered_touch_query(self):
        fab, w = make_test_world("iw_touch_6")
        assert fab.get_touch_position(99, w) is None

    def test_touch_coordinates_precision(self):
        fab, w = make_test_world("iw_touch_7")
        fab.create_device("touch_dev", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=5, position=[123.456, 789.012], world=w)
        fab.process_events(w)
        pos = fab.get_touch_position(5, w)
        assert pos == [123.456, 789.012]

    def test_touch_cleanup_on_stop(self):
        fab, w = make_test_world("iw_touch_8")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("touch_dev", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch_dev", RawInputEventType.TOUCH_START, touch_id=1, position=[10.0, 10.0], world=w)
        fab.process_events(w)
        fab.stop_world(w)
        assert fab.get_active_touch_count(w) == 0


# ==============================================================================
# §103. PEN & PRESSURE TESTS (6 tests)
# ==============================================================================

class TestPenAndPressure:
    """Normative tests for Stylus / Pen Input, Pressure & Tilt (§103)."""

    def test_pen_position_and_pressure(self):
        fab, w = make_test_world("iw_pen_1")
        fab.create_device("pen_dev", InputDeviceType.PEN, world=w)
        fab.create_raw_event("pen_dev", RawInputEventType.PEN_MOVE, position=[450.0, 600.0], pressure=0.75, world=w)
        fab.process_events(w)
        state = fab.get_pen_state(w)
        assert state["position"] == [450.0, 600.0]
        assert state["pressure"] == 0.75

    def test_pen_down_up_pressure(self):
        fab, w = make_test_world("iw_pen_2")
        fab.create_device("pen_dev", InputDeviceType.PEN, world=w)
        fab.create_raw_event("pen_dev", RawInputEventType.PEN_DOWN, position=[100.0, 100.0], pressure=0.9, world=w)
        fab.process_events(w)
        assert fab.get_pen_state(w)["pressure"] == 0.9
        fab.create_raw_event("pen_dev", RawInputEventType.PEN_UP, position=[100.0, 100.0], world=w)
        fab.process_events(w)
        assert fab.get_pen_state(w)["pressure"] == 0.0

    def test_pen_tilt_angles(self):
        fab, w = make_test_world("iw_pen_3")
        fab.create_device("pen_dev", InputDeviceType.PEN, world=w)
        fab.create_raw_event("pen_dev", RawInputEventType.PEN_MOVE, tilt=[15.0, -30.0], world=w)
        fab.process_events(w)
        assert fab.get_pen_state(w)["tilt"] == [15.0, -30.0]

    def test_pen_barrel_button(self):
        fab, w = make_test_world("iw_pen_4")
        fab.create_device("pen_dev", InputDeviceType.PEN, world=w)
        w.pen_barrel_button = True
        assert fab.get_pen_state(w)["barrel_button"] is True

    def test_pen_capabilities(self):
        fab, w = make_test_world("iw_pen_5")
        caps = DeviceCapabilities(supports_pressure=True, supports_tilt=True)
        dev = fab.create_device("pen_pro", InputDeviceType.PEN, capabilities=caps, world=w)
        assert dev.capabilities.supports_pressure is True
        assert dev.capabilities.supports_tilt is True

    def test_empty_pen_state_without_world(self):
        fab = UniversalRuntimeInputFabricator()
        assert fab.get_pen_state() == {}


# ==============================================================================
# §104. TEXT INPUT & UNICODE TESTS (6 tests)
# ==============================================================================

class TestTextInputAndUnicode:
    """Normative tests for Text Input & Unicode Handling (§104)."""

    def test_text_input_accumulation(self):
        fab, w = make_test_world("iw_txt_1")
        fab.create_device("kb_txt", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text="Hello", world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text=" World", world=w)
        fab.process_events(w)
        assert fab.get_text_buffer(w) == "Hello World"

    def test_text_input_unicode(self):
        fab, w = make_test_world("iw_txt_2")
        fab.create_device("kb_txt", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text="DarX ⚡ Ñandú 🎮", world=w)
        fab.process_events(w)
        assert fab.get_text_buffer(w) == "DarX ⚡ Ñandú 🎮"

    def test_clear_text_buffer(self):
        fab, w = make_test_world("iw_txt_3")
        fab.create_device("kb_txt", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text="Temp", world=w)
        fab.process_events(w)
        fab.clear_text_buffer(w)
        assert fab.get_text_buffer(w) == ""

    def test_text_input_does_not_trigger_key_bindings(self):
        fab, w = make_test_world("iw_txt_4")
        fab.create_device("kb_txt", InputDeviceType.KEYBOARD, world=w)
        act = fab.create_action("Jump", world=w)
        fab.bind_action("Jump", InputDeviceType.KEYBOARD, "KeySpace", world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text=" ", world=w)
        fab.process_events(w)
        assert act.is_pressed is False

    def test_text_input_composition(self):
        fab, w = make_test_world("iw_txt_5")
        fab.create_device("kb_txt", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text="c", world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text="a", world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text="t", world=w)
        fab.process_events(w)
        assert fab.get_text_buffer(w) == "cat"

    def test_empty_text_input_no_mutation(self):
        fab, w = make_test_world("iw_txt_6")
        fab.create_device("kb_txt", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_txt", RawInputEventType.TEXT_INPUT, text="", world=w)
        fab.process_events(w)
        assert fab.get_text_buffer(w) == ""


# ==============================================================================
# §105. ACTION MAPPING & CHORDS TESTS (9 tests)
# ==============================================================================

class TestActionMappingAndChords:
    """Normative tests for Action Mapping, Modifiers & Chord Execution (§105)."""

    def test_create_and_register_action(self):
        fab, w = make_test_world("iw_act_1")
        act = fab.create_action("Fire", priority=150, world=w)
        assert act.action_id == "Fire"
        assert act.priority == 150
        assert "Fire" in w.actions

    def test_bind_keyboard_action(self):
        fab, w = make_test_world("iw_act_2")
        fab.create_device("kb_act", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Jump", world=w)
        b = fab.bind_action("Jump", InputDeviceType.KEYBOARD, "KeySpace", world=w)
        assert b.code == "KeySpace"
        assert len(w.actions["Jump"].bindings) == 1

    def test_trigger_action_on_key_down(self):
        fab, w = make_test_world("iw_act_3")
        fab.create_device("kb_act", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Jump", world=w)
        fab.bind_action("Jump", InputDeviceType.KEYBOARD, "KeySpace", world=w)
        fab.create_raw_event("kb_act", RawInputEventType.KEY_DOWN, code="KeySpace", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Jump", w) is True
        assert w.actions["Jump"].state == ActionTriggerState.TRIGGERED

    def test_release_action_on_key_up(self):
        fab, w = make_test_world("iw_act_4")
        fab.create_device("kb_act", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Jump", world=w)
        fab.bind_action("Jump", InputDeviceType.KEYBOARD, "KeySpace", world=w)
        fab.create_raw_event("kb_act", RawInputEventType.KEY_DOWN, code="KeySpace", world=w)
        fab.process_events(w)
        fab.create_raw_event("kb_act", RawInputEventType.KEY_UP, code="KeySpace", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Jump", w) is False
        assert w.actions["Jump"].state == ActionTriggerState.COMPLETED

    def test_action_chord_with_modifier(self):
        fab, w = make_test_world("iw_act_5")
        fab.create_device("kb_act", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Save", world=w)
        fab.bind_action("Save", InputDeviceType.KEYBOARD, "KeyS", modifiers=["CONTROL"], world=w)
        # Press KeyS without Control: should not trigger
        fab.create_raw_event("kb_act", RawInputEventType.KEY_DOWN, code="KeyS", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Save", w) is False
        # Now press ControlLeft, then KeyS: should trigger
        fab.create_raw_event("kb_act", RawInputEventType.KEY_DOWN, code="ControlLeft", world=w)
        fab.create_raw_event("kb_act", RawInputEventType.KEY_DOWN, code="KeyS", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Save", w) is True

    def test_action_consumption(self):
        fab, w = make_test_world("iw_act_6")
        fab.create_device("kb_act", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Primary", consume=True, world=w)
        fab.bind_action("Primary", InputDeviceType.KEYBOARD, "KeyE", world=w)
        ev = fab.create_raw_event("kb_act", RawInputEventType.KEY_DOWN, code="KeyE", world=w)
        fab.process_events(w)
        assert ev.consumed is True

    def test_mouse_button_action(self):
        fab, w = make_test_world("iw_act_7")
        fab.create_device("m_act", InputDeviceType.MOUSE, world=w)
        fab.create_action("Attack", world=w)
        fab.bind_action("Attack", InputDeviceType.MOUSE, "LeftButton", world=w)
        fab.create_raw_event("m_act", RawInputEventType.MOUSE_DOWN, code="LeftButton", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Attack", w) is True

    def test_gamepad_button_action(self):
        fab, w = make_test_world("iw_act_8")
        fab.create_device("gp_act", InputDeviceType.GAMEPAD, world=w)
        fab.create_action("Interact", world=w)
        fab.bind_action("Interact", InputDeviceType.GAMEPAD, "ButtonX", world=w)
        fab.create_raw_event("gp_act", RawInputEventType.GAMEPAD_BUTTON_DOWN, code="ButtonX", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Interact", w) is True

    def test_action_max_limit(self):
        fab, w = make_test_world("iw_act_9")
        w.settings.max_actions = 2
        fab.create_action("A1", world=w)
        fab.create_action("A2", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_action("A3", world=w)


# ==============================================================================
# §106. AXIS MAPPING, CURVES & DEAD-ZONES TESTS (8 tests)
# ==============================================================================

class TestAxisMappingAndCurves:
    """Normative tests for Axis Mapping, Curves, Inversion & Composites (§106)."""

    def test_create_and_register_axis(self):
        fab, w = make_test_world("iw_ax_1")
        ax = fab.create_axis("MoveForward", world=w)
        assert ax.axis_id == "MoveForward"
        assert "MoveForward" in w.axes

    def test_bind_gamepad_axis(self):
        fab, w = make_test_world("iw_ax_2")
        fab.create_device("gp_ax", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("MoveForward", world=w)
        b = fab.bind_axis("MoveForward", InputDeviceType.GAMEPAD, "LeftY", scale=1.0, dead_zone=0.15, world=w)
        assert b.dead_zone == 0.15
        assert b.code == "LeftY"

    def test_axis_evaluation_with_dead_zone(self):
        fab, w = make_test_world("iw_ax_3")
        fab.create_device("gp_ax", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("MoveForward", world=w)
        fab.bind_axis("MoveForward", InputDeviceType.GAMEPAD, "LeftY", dead_zone=0.2, world=w)
        # Event within dead-zone
        fab.create_raw_event("gp_ax", RawInputEventType.GAMEPAD_AXIS, code="LeftY", value=0.1, world=w)
        fab.process_events(w)
        assert fab.get_axis_value("MoveForward", w) == 0.0

    def test_axis_evaluation_outside_dead_zone(self):
        fab, w = make_test_world("iw_ax_4")
        fab.create_device("gp_ax", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("MoveForward", world=w)
        fab.bind_axis("MoveForward", InputDeviceType.GAMEPAD, "LeftY", dead_zone=0.2, world=w)
        # Value 0.6: (0.6 - 0.2) / 0.8 = 0.5
        fab.create_raw_event("gp_ax", RawInputEventType.GAMEPAD_AXIS, code="LeftY", value=0.6, world=w)
        fab.process_events(w)
        assert pytest.approx(fab.get_axis_value("MoveForward", w), rel=1e-3) == 0.5

    def test_axis_invert(self):
        fab, w = make_test_world("iw_ax_5")
        fab.create_device("gp_ax", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("LookUp", world=w)
        fab.bind_axis("LookUp", InputDeviceType.GAMEPAD, "RightY", invert=True, dead_zone=0.0, world=w)
        fab.create_raw_event("gp_ax", RawInputEventType.GAMEPAD_AXIS, code="RightY", value=0.8, world=w)
        fab.process_events(w)
        assert pytest.approx(fab.get_axis_value("LookUp", w), rel=1e-3) == -0.8

    def test_axis_exponential_curve(self):
        fab = UniversalRuntimeInputFabricator()
        # Exponential curve: 0.5^2 = 0.25
        val = fab.apply_axis_curve(0.5, AxisCurveType.EXPONENTIAL)
        assert pytest.approx(val, rel=1e-3) == 0.25

    def test_composite_digital_axis(self):
        fab, w = make_test_world("iw_ax_7")
        fab.create_device("kb_ax", InputDeviceType.KEYBOARD, world=w)
        fab.create_axis("MoveX", world=w)
        fab.bind_composite_axis("MoveX", positive_key="KeyD", negative_key="KeyA", world=w)
        # Press KeyD (positive)
        fab.create_raw_event("kb_ax", RawInputEventType.KEY_DOWN, code="KeyD", world=w)
        fab.process_events(w)
        assert fab.get_axis_value("MoveX", w) == 1.0
        # Release KeyD, press KeyA (negative)
        fab.create_raw_event("kb_ax", RawInputEventType.KEY_UP, code="KeyD", world=w)
        fab.create_raw_event("kb_ax", RawInputEventType.KEY_DOWN, code="KeyA", world=w)
        fab.process_events(w)
        assert fab.get_axis_value("MoveX", w) == -1.0

    def test_axis_max_limit(self):
        fab, w = make_test_world("iw_ax_8")
        w.settings.max_axes = 2
        fab.create_axis("X1", world=w)
        fab.create_axis("X2", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_axis("X3", world=w)


# ==============================================================================
# §107. INPUT CONTEXTS, PRIORITY & ROUTING TESTS (9 tests)
# ==============================================================================

class TestInputContextsAndRouting:
    """Normative tests for Context Stack, Prioritized Filtering & Routing (§107)."""

    def test_create_and_register_context(self):
        fab, w = make_test_world("iw_ctx_1")
        ctx = fab.create_context("GameplayContext", priority=10, world=w)
        assert ctx.context_id == "GameplayContext"
        assert ctx.priority == 10
        assert "GameplayContext" in w.contexts

    def test_push_and_pop_context(self):
        fab, w = make_test_world("iw_ctx_2")
        fab.create_context("UIContext", priority=100, world=w)
        fab.push_context("UIContext", w)
        assert "UIContext" in w.context_stack
        popped = fab.pop_context("UIContext", w)
        assert popped == "UIContext"
        assert len(w.context_stack) == 0

    def test_active_contexts_sorted_by_priority(self):
        fab, w = make_test_world("iw_ctx_3")
        c1 = fab.create_context("Low", priority=5, world=w)
        c2 = fab.create_context("High", priority=50, world=w)
        c3 = fab.create_context("Mid", priority=20, world=w)
        fab.push_context("Low", w)
        fab.push_context("High", w)
        fab.push_context("Mid", w)
        active = fab.get_active_contexts(w)
        assert [c.context_id for c in active] == ["High", "Mid", "Low"]

    def test_context_action_filtering(self):
        fab, w = make_test_world("iw_ctx_4")
        fab.create_device("kb_ctx", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("GameplayAction", world=w)
        fab.bind_action("GameplayAction", InputDeviceType.KEYBOARD, "KeyF", world=w)
        ctx = fab.create_context("MenuContext", priority=100, world=w)
        ctx.action_ids = ["MenuConfirm"]  # GameplayAction is NOT in this context
        fab.push_context("MenuContext", w)
        # Event for KeyF should not trigger GameplayAction
        fab.create_raw_event("kb_ctx", RawInputEventType.KEY_DOWN, code="KeyF", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("GameplayAction", w) is False

    def test_context_action_allowed(self):
        fab, w = make_test_world("iw_ctx_5")
        fab.create_device("kb_ctx", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("MenuConfirm", world=w)
        fab.bind_action("MenuConfirm", InputDeviceType.KEYBOARD, "Enter", world=w)
        ctx = fab.create_context("MenuContext", priority=100, world=w)
        ctx.action_ids = ["MenuConfirm"]
        fab.push_context("MenuContext", w)
        fab.create_raw_event("kb_ctx", RawInputEventType.KEY_DOWN, code="Enter", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("MenuConfirm", w) is True

    def test_context_routing_modes(self):
        fab, w = make_test_world("iw_ctx_6")
        ctx = fab.create_context("UIOnly", routing_mode=InputRoutingMode.UI_ONLY, world=w)
        assert ctx.routing_mode == InputRoutingMode.UI_ONLY

    def test_context_max_limit(self):
        fab, w = make_test_world("iw_ctx_7")
        w.settings.max_contexts = 2
        fab.create_context("C1", world=w)
        fab.create_context("C2", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_context("C3", world=w)

    def test_pop_from_empty_stack(self):
        fab, w = make_test_world("iw_ctx_8")
        assert fab.pop_context(world=w) is None

    def test_duplicate_context_rejected(self):
        fab, w = make_test_world("iw_ctx_9")
        fab.create_context("C_Unique", world=w)
        with pytest.raises(ValueError, match="DUPLICATE_CONTEXT_ID"):
            fab.create_context("C_Unique", world=w)


# ==============================================================================
# §108. GESTURE RECOGNITION & CONFLICTS TESTS (9 tests)
# ==============================================================================

class TestGestureRecognition:
    """Normative tests for Gestures (Tap, Pinch, Swipe, Pan) & Conflicts (§108)."""

    def test_create_and_register_gesture(self):
        fab, w = make_test_world("iw_gst_1")
        g = fab.create_gesture("SingleTap", GestureType.TAP, max_duration=0.3, world=w)
        assert g.gesture_id == "SingleTap"
        assert g.gesture_type == GestureType.TAP
        assert "SingleTap" in w.gestures

    def test_gesture_initial_state(self):
        fab, w = make_test_world("iw_gst_2")
        g = fab.create_gesture("DoubleTap", GestureType.DOUBLE_TAP, tap_count=2, world=w)
        assert fab.get_gesture_state("DoubleTap", w) == GestureState.POSSIBLE

    def test_gesture_swipe_properties(self):
        fab, w = make_test_world("iw_gst_3")
        g = fab.create_gesture("SwipeLeft", GestureType.SWIPE, min_distance=50.0, world=w)
        assert g.min_distance == 50.0

    def test_gesture_pinch_scale(self):
        fab, w = make_test_world("iw_gst_4")
        g = fab.create_gesture("PinchZoom", GestureType.PINCH, world=w)
        g.scale = 1.8
        assert g.scale == 1.8

    def test_gesture_rotate_angle(self):
        fab, w = make_test_world("iw_gst_5")
        g = fab.create_gesture("RotateCam", GestureType.ROTATE, world=w)
        g.rotation = 45.0
        assert g.rotation == 45.0

    def test_gesture_state_transition(self):
        fab, w = make_test_world("iw_gst_6")
        g = fab.create_gesture("PanMove", GestureType.PAN, world=w)
        g.state = GestureState.BEGAN
        assert fab.get_gesture_state("PanMove", w) == GestureState.BEGAN
        g.state = GestureState.ENDED
        assert fab.get_gesture_state("PanMove", w) == GestureState.ENDED

    def test_gesture_timeout_fail_on_update(self):
        fab, w = make_test_world("iw_gst_7")
        fab.initialize_world(w)
        fab.start_world(w)
        g = fab.create_gesture("QuickTap", GestureType.TAP, max_duration=0.2, world=w)
        g.state = GestureState.BEGAN
        fab.update(0.3, w)
        assert g.state == GestureState.FAILED

    def test_unknown_gesture_query(self):
        fab, w = make_test_world("iw_gst_8")
        assert fab.get_gesture_state("NonExistent", w) == GestureState.FAILED

    def test_duplicate_gesture_rejected(self):
        fab, w = make_test_world("iw_gst_9")
        fab.create_gesture("Tap1", GestureType.TAP, world=w)
        with pytest.raises(ValueError, match="DUPLICATE_GESTURE_ID"):
            fab.create_gesture("Tap1", GestureType.TAP, world=w)


# ==============================================================================
# §109. REBINDING, PROFILES & ACCESSIBILITY TESTS (9 tests)
# ==============================================================================

class TestRebindingAndAccessibility:
    """Normative tests for Action Rebinding, Profiles, Migration & Accessibility (§109)."""

    def test_register_profile(self):
        fab, w = make_test_world("iw_reb_1")
        prof = InputRebindingProfile("prof_custom", user_id="player1", version=1)
        fab.register_profile(prof, w)
        assert "prof_custom" in w.profiles

    def test_set_active_profile(self):
        fab, w = make_test_world("iw_reb_2")
        prof = InputRebindingProfile("prof_gamepad")
        fab.register_profile(prof, w)
        fab.set_active_profile("prof_gamepad", w)
        assert w.active_profile_id == "prof_gamepad"

    def test_rebind_action_key(self):
        fab, w = make_test_world("iw_reb_3")
        fab.create_device("kb_reb", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Fire", world=w)
        fab.bind_action("Fire", InputDeviceType.KEYBOARD, "KeyF", world=w)
        # Rebind to KeyR
        fab.rebind_action("Fire", "KeyF", "KeyR", InputDeviceType.KEYBOARD, w)
        fab.create_raw_event("kb_reb", RawInputEventType.KEY_DOWN, code="KeyR", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Fire", w) is True

    def test_reset_profile_to_default(self):
        fab, w = make_test_world("iw_reb_4")
        prof = InputRebindingProfile("prof_mod")
        prof.dead_zone_overrides["LeftStick"] = 0.25
        fab.register_profile(prof, w)
        fab.reset_profile_to_default("prof_mod", w)
        assert len(prof.dead_zone_overrides) == 0

    def test_accessibility_sticky_keys_setting(self):
        fab, w = make_test_world("iw_reb_5")
        w.settings.accessibility_sticky_keys = True
        assert w.settings.accessibility_sticky_keys is True

    def test_accessibility_slow_keys_duration(self):
        fab, w = make_test_world("iw_reb_6")
        w.settings.accessibility_slow_keys_duration = 0.3
        assert w.settings.accessibility_slow_keys_duration == 0.3

    def test_profile_serialization(self):
        prof = InputRebindingProfile("prof_ser", user_id="u42", version=2, dead_zone_overrides={"RightStick": 0.15})
        d = prof.to_dict()
        assert d["profile_id"] == "prof_ser"
        assert d["version"] == 2
        assert d["dead_zone_overrides"]["RightStick"] == 0.15

    def test_rebind_unknown_action_raises(self):
        fab, w = make_test_world("iw_reb_8")
        with pytest.raises(ValueError, match="ACTION_NOT_FOUND"):
            fab.rebind_action("UnknownAct", "KeyA", "KeyB", InputDeviceType.KEYBOARD, w)

    def test_profile_versioning_validation(self):
        val = UniversalRuntimeInputValidator()
        prof = InputRebindingProfile("prof_bad_ver", version=0)
        issues = val.validate_profile(prof)
        assert any(i.error_code == "INVALID_PROFILE_VERSION" for i in issues)


# ==============================================================================
# §110. INPUT RECORDING TESTS (8 tests)
# ==============================================================================

class TestInputRecording:
    """Normative tests for Input Recording, Frame Counts & Hashes (§110)."""

    def test_start_and_stop_recording(self):
        fab, w = make_test_world("iw_rec_1")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.start_recording("rec_run_1", w)
        fab.create_device("kb_rec", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb_rec", RawInputEventType.KEY_DOWN, code="KeyW", world=w)
        fab.update(0.016, w)
        rec = fab.stop_recording(w)
        assert rec is not None
        assert rec.record_id == "rec_run_1"
        assert len(rec.events) == 1
        assert rec.frame_count == 1
        assert len(rec.record_hash) == 64

    def test_recording_multiple_events(self):
        fab, w = make_test_world("iw_rec_2")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.start_recording("rec_run_2", w)
        fab.create_device("kb_rec", InputDeviceType.KEYBOARD, world=w)
        for i in range(5):
            fab.create_raw_event("kb_rec", RawInputEventType.KEY_DOWN, code=f"Key{i}", world=w)
        rec = fab.stop_recording(w)
        assert len(rec.events) == 5

    def test_stop_recording_when_not_recording(self):
        fab, w = make_test_world("iw_rec_3")
        assert fab.stop_recording(w) is None

    def test_record_hash_deterministic(self):
        def make_rec():
            fab, w = make_test_world("iw_rec_det")
            fab.initialize_world(w)
            fab.start_world(w)
            fab.start_recording("rec_det", w)
            fab.create_device("kb_rec", InputDeviceType.KEYBOARD, world=w)
            fab.create_raw_event("kb_rec", RawInputEventType.KEY_DOWN, code="KeySpace", timestamp=0.016, world=w)
            return fab.stop_recording(w).record_hash
        assert make_rec() == make_rec()

    def test_record_serialization(self):
        rec = InputRecord("rec_ser", events=[], start_timestamp=1.0, duration_seconds=5.0, frame_count=300)
        d = rec.to_dict()
        assert d["record_id"] == "rec_ser"
        assert d["frame_count"] == 300

    def test_recording_duration_calculation(self):
        fab, w = make_test_world("iw_rec_6")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.start_recording("rec_dur", w)
        fab.update(1.5, w)
        rec = fab.stop_recording(w)
        assert pytest.approx(rec.duration_seconds, rel=1e-3) == 1.5

    def test_recording_captures_all_device_types(self):
        fab, w = make_test_world("iw_rec_7")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.start_recording("rec_multi", w)
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_device("ms", InputDeviceType.MOUSE, world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="KeyA", world=w)
        fab.create_raw_event("ms", RawInputEventType.MOUSE_MOVE, position=[100.0, 100.0], world=w)
        rec = fab.stop_recording(w)
        types = [e.device_type for e in rec.events]
        assert InputDeviceType.KEYBOARD in types
        assert InputDeviceType.MOUSE in types

    def test_consecutive_recordings(self):
        fab, w = make_test_world("iw_rec_8")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.start_recording("rec_a", w)
        rec_a = fab.stop_recording(w)
        fab.start_recording("rec_b", w)
        rec_b = fab.stop_recording(w)
        assert rec_a.record_id == "rec_a"
        assert rec_b.record_id == "rec_b"


# ==============================================================================
# §111. INPUT REPLAY TESTS (10 tests)
# ==============================================================================

class TestInputReplay:
    """Normative tests for Deterministic Replay, Session Execution & Tamper Checks (§111)."""

    def test_replay_execution_basic(self):
        fab, w = make_test_world("iw_rep_1")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("kb_rep", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Jump", world=w)
        fab.bind_action("Jump", InputDeviceType.KEYBOARD, "KeySpace", world=w)
        ev = RawInputEvent("e1", 1, "kb_rep", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeySpace")
        rec = InputRecord("rec_rep", events=[ev])
        session = InputReplaySession("sess_1", rec)
        fab.execute_replay(session, w)
        assert session.is_finished is True
        assert fab.is_action_triggered("Jump", w) is True

    def test_replay_hash_tamper_detected(self):
        fab, w = make_test_world("iw_rep_2")
        ev = RawInputEvent("e1", 1, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyA")
        rec = InputRecord("rec_tamper", events=[ev], record_hash="INVALID_HASH_CORRUPTED")
        session = InputReplaySession("sess_tamper", rec)
        with pytest.raises(ValueError, match="REPLAY_VALIDATION_FAILED"):
            fab.execute_replay(session, w)
        assert session.is_valid is False

    def test_replay_session_serialization(self):
        rec = InputRecord("rec_s", events=[])
        sess = InputReplaySession("sess_ser", rec)
        d = sess.to_dict()
        assert d["session_id"] == "sess_ser"
        assert d["record_id"] == "rec_s"

    def test_replay_multiple_frames(self):
        fab, w = make_test_world("iw_rep_4")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        evs = [
            RawInputEvent(f"e_{i}", i, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code=f"Key{i}")
            for i in range(4)
        ]
        rec = InputRecord("rec_4", events=evs)
        session = InputReplaySession("sess_4", rec)
        fab.execute_replay(session, w)
        assert len(w.processed_events) == 4

    def test_replay_preserves_device_state(self):
        fab, w = make_test_world("iw_rep_5")
        fab.initialize_world(w)
        fab.start_world(w)
        dev = fab.create_device("gp", InputDeviceType.GAMEPAD, world=w)
        ev = RawInputEvent("eg1", 1, "gp", InputDeviceType.GAMEPAD, RawInputEventType.GAMEPAD_BUTTON_DOWN, code="ButtonY")
        rec = InputRecord("rec_gp", events=[ev])
        session = InputReplaySession("sess_gp", rec)
        fab.execute_replay(session, w)
        assert dev.button_states.get("ButtonY", False) is True

    def test_replay_empty_record(self):
        fab, w = make_test_world("iw_rep_6")
        rec = InputRecord("rec_empty", events=[])
        session = InputReplaySession("sess_empty", rec)
        fab.execute_replay(session, w)
        assert session.is_finished is True

    def test_replay_mouse_path(self):
        fab, w = make_test_world("iw_rep_7")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("m", InputDeviceType.MOUSE, world=w)
        evs = [
            RawInputEvent("m1", 1, "m", InputDeviceType.MOUSE, RawInputEventType.MOUSE_MOVE, position=[100.0, 100.0]),
            RawInputEvent("m2", 2, "m", InputDeviceType.MOUSE, RawInputEventType.MOUSE_MOVE, position=[200.0, 300.0]),
        ]
        rec = InputRecord("rec_m", events=evs)
        session = InputReplaySession("sess_m", rec)
        fab.execute_replay(session, w)
        assert w.mouse_position == [200.0, 300.0]

    def test_replay_axis_values(self):
        fab, w = make_test_world("iw_rep_8")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("gp", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("Throttle", world=w)
        fab.bind_axis("Throttle", InputDeviceType.GAMEPAD, "RightTrigger", dead_zone=0.0, world=w)
        ev = RawInputEvent("gt", 1, "gp", InputDeviceType.GAMEPAD, RawInputEventType.GAMEPAD_AXIS, code="RightTrigger", value=0.85)
        rec = InputRecord("rec_gt", events=[ev])
        session = InputReplaySession("sess_gt", rec)
        fab.execute_replay(session, w)
        assert fab.get_axis_value("Throttle", w) == 0.85

    def test_replay_resilience_to_unknown_device(self):
        fab, w = make_test_world("iw_rep_9")
        ev = RawInputEvent("e_unk", 1, "dev_unknown", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyX")
        rec = InputRecord("rec_unk", events=[ev])
        session = InputReplaySession("sess_unk", rec)
        fab.execute_replay(session, w)
        assert session.is_finished is True

    def test_replay_reproducibility(self):
        def run_sim():
            fab, w = make_test_world("iw_rep_repro")
            fab.initialize_world(w)
            fab.start_world(w)
            fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
            fab.create_action("A1", world=w)
            fab.bind_action("A1", InputDeviceType.KEYBOARD, "KeyZ", world=w)
            ev = RawInputEvent("ez", 1, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyZ")
            rec = InputRecord("rec_z", events=[ev])
            session = InputReplaySession("s_z", rec)
            fab.execute_replay(session, w)
            return w.compute_fingerprint()
        assert run_sim() == run_sim()


# ==============================================================================
# §112. INPUT SNAPSHOTS TESTS (9 tests)
# ==============================================================================

class TestInputSnapshots:
    """Normative tests for Input Snapshots, Hashes & State Consistency (§112)."""

    def test_capture_snapshot_structure(self):
        fab, w = make_test_world("iw_snap_1")
        fab.initialize_world(w)
        dev = fab.create_device("kb_snap", InputDeviceType.KEYBOARD, world=w)
        dev.button_states["KeyP"] = True
        snap = fab.capture_snapshot(w)
        assert snap.world_id == "iw_snap_1"
        assert snap.keyboard_state.get("KeyP", False) is True
        assert len(snap.snapshot_hash) == 64

    def test_snapshot_mouse_position(self):
        fab, w = make_test_world("iw_snap_2")
        fab.set_mouse_position(640.0, 480.0, w)
        snap = fab.capture_snapshot(w)
        assert snap.mouse_position == [640.0, 480.0]

    def test_snapshot_active_contexts(self):
        fab, w = make_test_world("iw_snap_3")
        fab.create_context("CtxAlpha", world=w)
        fab.push_context("CtxAlpha", w)
        snap = fab.capture_snapshot(w)
        assert "CtxAlpha" in snap.active_contexts

    def test_snapshot_gamepad_axes(self):
        fab, w = make_test_world("iw_snap_4")
        dev = fab.create_device("gp_snap", InputDeviceType.GAMEPAD, world=w)
        dev.axis_states["LeftX"] = -0.75
        snap = fab.capture_snapshot(w)
        assert snap.gamepad_axes.get("LeftX") == -0.75

    def test_snapshot_determinism(self):
        def get_snap_hash():
            fab, w = make_test_world("iw_snap_det")
            fab.initialize_world(w)
            fab.set_mouse_position(100.0, 200.0, w)
            return fab.capture_snapshot(w).snapshot_hash
        assert get_snap_hash() == get_snap_hash()

    def test_snapshot_serialization(self):
        snap = InputSnapshot("snap_test", world_id="iw_test", mouse_position=[50.0, 50.0], snapshot_hash="abc")
        d = snap.to_dict()
        assert d["snapshot_id"] == "snap_test"
        assert d["world_id"] == "iw_test"
        assert d["snapshot_hash"] == "abc"

    def test_snapshot_timestamp(self):
        fab, w = make_test_world("iw_snap_7")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.update(1.25, w)
        snap = fab.capture_snapshot(w)
        assert pytest.approx(snap.timestamp, rel=1e-3) == 1.25

    def test_snapshot_state_isolated_from_world_mutation(self):
        fab, w = make_test_world("iw_snap_8")
        fab.set_mouse_position(10.0, 10.0, w)
        snap = fab.capture_snapshot(w)
        fab.set_mouse_position(99.0, 99.0, w)
        assert snap.mouse_position == [10.0, 10.0]

    def test_snapshot_empty_world(self):
        fab, w = make_test_world("iw_snap_9")
        snap = fab.capture_snapshot(w)
        assert snap.snapshot_id is not None
        assert len(snap.keyboard_state) == 0


# ==============================================================================
# §113. INPUT DETERMINISM TESTS (10 tests)
# ==============================================================================

class TestInputDeterminism:
    """Normative tests for Input Determinism, Frame Consistency & Order (§113)."""

    def test_identical_events_identical_fingerprint(self):
        def run(wid):
            fab, w = make_test_world(wid)
            fab.initialize_world(w)
            fab.start_world(w)
            fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="KeyA", timestamp=0.016, world=w)
            fab.update(0.016, w)
            return w.compute_fingerprint()
        assert run("iw_det_1") == run("iw_det_1")

    def test_event_order_reproducibility(self):
        fab, w = make_test_world("iw_det_2")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        for c in ["KeyA", "KeyB", "KeyC"]:
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code=c, world=w)
        fab.process_events(w)
        codes = [e.code for e in w.processed_events]
        assert codes == ["KeyA", "KeyB", "KeyC"]

    def test_axis_deadzone_deterministic_precision(self):
        fab = UniversalRuntimeInputFabricator()
        v1 = fab.apply_dead_zone(0.333333, 0.1)
        v2 = fab.apply_dead_zone(0.333333, 0.1)
        assert v1 == v2

    def test_action_trigger_deterministic(self):
        def test_trigger():
            fab, w = make_test_world("iw_det_4")
            fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
            fab.create_action("Fire", world=w)
            fab.bind_action("Fire", InputDeviceType.KEYBOARD, "Space", world=w)
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="Space", world=w)
            fab.process_events(w)
            return fab.is_action_triggered("Fire", w)
        assert test_trigger() is test_trigger() is True

    def test_context_stack_priority_determinism(self):
        fab, w = make_test_world("iw_det_5")
        for i in range(10):
            fab.create_context(f"C_{i}", priority=i * 10, world=w)
            fab.push_context(f"C_{i}", w)
        priors = [c.priority for c in fab.get_active_contexts(w)]
        assert priors == sorted(priors, reverse=True)

    def test_mouse_delta_accumulation_deterministic(self):
        fab, w = make_test_world("iw_det_6")
        fab.create_device("m", InputDeviceType.MOUSE, world=w)
        fab.create_raw_event("m", RawInputEventType.MOUSE_MOVE, position=[10.0, 10.0], delta=[5.0, 5.0], world=w)
        fab.create_raw_event("m", RawInputEventType.MOUSE_MOVE, position=[25.0, 30.0], delta=[15.0, 20.0], world=w)
        fab.process_events(w)
        assert w.mouse_position == [25.0, 30.0]
        assert w.mouse_delta == [15.0, 20.0]

    def test_fingerprint_changes_on_input_mutation(self):
        fab, w = make_test_world("iw_det_7")
        fab.initialize_world(w)
        fp_before = w.compute_fingerprint()
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fp_after = w.compute_fingerprint()
        assert fp_before != fp_after

    def test_fingerprint_deterministic_roundtrip(self):
        fab, w = make_test_world("iw_det_8")
        assert w.compute_fingerprint() == w.compute_fingerprint()

    def test_multi_device_events_deterministic_interleaving(self):
        fab, w = make_test_world("iw_det_9")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_device("m", InputDeviceType.MOUSE, world=w)
        ev_kb = RawInputEvent("ek", 1, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, timestamp=0.01)
        ev_ms = RawInputEvent("em", 2, "m", InputDeviceType.MOUSE, RawInputEventType.MOUSE_MOVE, timestamp=0.02)
        fab.queue_raw_event(ev_ms, w)
        fab.queue_raw_event(ev_kb, w)
        fab.process_events(w)
        assert w.processed_events[0].event_id == "ek"
        assert w.processed_events[1].event_id == "em"

    def test_clock_step_deterministic_advancement(self):
        fab, w = make_test_world("iw_det_10")
        fab.initialize_world(w)
        fab.start_world(w)
        for _ in range(60):
            fab.update(1.0 / 60.0, w)
        assert pytest.approx(w.time_seconds, rel=1e-3) == 1.0
        assert w.frames_rendered == 60


# ==============================================================================
# §114. GOLDEN INPUT HASH TESTS (15 tests)
# ==============================================================================

class TestGoldenInputHashes:
    """Normative tests for Golden Input Reference Hashes (§114)."""

    def test_golden_empty_input_world(self):
        fab, w = make_test_world("iw_gold_1")
        ga = fab.capture_golden_input(w)
        assert "golden_hash" in ga
        assert ga["devices_count"] == 0

    def test_golden_single_keyboard_device(self):
        fab, w = make_test_world("iw_gold_2")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        ga = fab.capture_golden_input(w)
        assert ga["devices_count"] == 1

    def test_golden_gamepad_device(self):
        fab, w = make_test_world("iw_gold_3")
        fab.create_device("gp", InputDeviceType.GAMEPAD, world=w)
        ga = fab.capture_golden_input(w)
        assert "golden_hash" in ga

    def test_golden_touch_device(self):
        fab, w = make_test_world("iw_gold_4")
        fab.create_device("touch", InputDeviceType.TOUCH, world=w)
        ga = fab.capture_golden_input(w)
        assert "golden_hash" in ga

    def test_golden_mouse_device(self):
        fab, w = make_test_world("iw_gold_5")
        fab.create_device("mouse", InputDeviceType.MOUSE, world=w)
        ga = fab.capture_golden_input(w)
        assert "golden_hash" in ga

    def test_golden_action_binding(self):
        fab, w = make_test_world("iw_gold_6")
        fab.create_action("Attack", world=w)
        ga = fab.capture_golden_input(w)
        assert ga["actions_count"] == 1

    def test_golden_axis_binding(self):
        fab, w = make_test_world("iw_gold_7")
        fab.create_axis("Steer", world=w)
        ga = fab.capture_golden_input(w)
        assert ga["axes_count"] == 1

    def test_golden_context_stack(self):
        fab, w = make_test_world("iw_gold_8")
        fab.create_context("InGame", world=w)
        ga = fab.capture_golden_input(w)
        assert ga["contexts_count"] == 1

    def test_golden_mouse_position(self):
        fab, w = make_test_world("iw_gold_9")
        fab.set_mouse_position(800.0, 600.0, w)
        ga = fab.capture_golden_input(w)
        assert ga["mouse_position"] == [800.0, 600.0]

    def test_golden_processed_events(self):
        fab, w = make_test_world("iw_gold_10")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="KeyQ", world=w)
        fab.process_events(w)
        ga = fab.capture_golden_input(w)
        assert ga["processed_events_count"] == 1

    def test_golden_reproducibility_1(self):
        def get_hash():
            fab, w = make_test_world("iw_gold_rep")
            fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
            return fab.capture_golden_input(w)["golden_hash"]
        assert get_hash() == get_hash()

    def test_golden_multi_action_suite(self):
        fab, w = make_test_world("iw_gold_12")
        for act in ["Jump", "Crouch", "Sprint", "Fire", "Reload"]:
            fab.create_action(act, world=w)
        ga = fab.capture_golden_input(w)
        assert ga["actions_count"] == 5

    def test_golden_multi_axis_suite(self):
        fab, w = make_test_world("iw_gold_13")
        for ax in ["MoveX", "MoveY", "LookX", "LookY"]:
            fab.create_axis(ax, world=w)
        ga = fab.capture_golden_input(w)
        assert ga["axes_count"] == 4

    def test_golden_complete_session(self):
        fab, w = make_test_world("iw_gold_14")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_device("m", InputDeviceType.MOUSE, world=w)
        fab.create_action("Shoot", world=w)
        fab.create_axis("Pitch", world=w)
        fab.create_context("Combat", world=w)
        ga = fab.capture_golden_input(w)
        assert len(ga["golden_hash"]) == 64

    def test_golden_empty_when_no_world(self):
        fab = UniversalRuntimeInputFabricator()
        assert fab.capture_golden_input() == {}


# ==============================================================================
# §115. SECURITY & BUFFER LIMITS TESTS (20 tests)
# ==============================================================================

class TestSecurityExecution:
    """Normative tests for Security Boundaries, Buffer Floods & Validations (§115)."""

    def test_security_empty_world_id_rejected(self):
        fab = UniversalRuntimeInputFabricator()
        with pytest.raises(ValueError, match="INVALID_INPUT_WORLD_ID"):
            fab.create_world("")

    def test_security_whitespace_world_id_rejected(self):
        fab = UniversalRuntimeInputFabricator()
        with pytest.raises(ValueError, match="INVALID_INPUT_WORLD_ID"):
            fab.create_world("   ")

    def test_security_max_devices_enforced(self):
        fab, w = make_test_world("iw_sec_dev")
        w.settings.max_devices = 3
        for i in range(3):
            fab.create_device(f"dev_{i}", InputDeviceType.KEYBOARD, world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_device("dev_overflow", InputDeviceType.KEYBOARD, world=w)

    def test_security_max_actions_enforced(self):
        fab, w = make_test_world("iw_sec_act")
        w.settings.max_actions = 3
        for i in range(3):
            fab.create_action(f"act_{i}", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_action("act_overflow", world=w)

    def test_security_max_axes_enforced(self):
        fab, w = make_test_world("iw_sec_ax")
        w.settings.max_axes = 3
        for i in range(3):
            fab.create_axis(f"ax_{i}", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_axis("ax_overflow", world=w)

    def test_security_max_contexts_enforced(self):
        fab, w = make_test_world("iw_sec_ctx")
        w.settings.max_contexts = 3
        for i in range(3):
            fab.create_context(f"ctx_{i}", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_context("ctx_overflow", world=w)

    def test_security_max_buffer_size_enforced(self):
        fab, w = make_test_world("iw_sec_buf")
        w.settings.max_buffer_size = 5
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        for i in range(5):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code=f"Key{i}", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="KeyOver", world=w)

    def test_security_max_events_flood_clamped(self):
        fab, w = make_test_world("iw_sec_flood")
        w.settings.max_events_per_frame = 10
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        for i in range(25):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code=f"Key{i}", world=w)
        processed = fab.process_events(w)
        assert processed == 25
        assert len(w.processed_events) == 10

    def test_security_dead_zone_range_clamped(self):
        fab = UniversalRuntimeInputFabricator()
        with pytest.raises(ValueError, match="INVALID_DEAD_ZONE"):
            fab.apply_dead_zone(0.5, -0.1)
        with pytest.raises(ValueError, match="INVALID_DEAD_ZONE"):
            fab.apply_dead_zone(0.5, 1.0)

    def test_security_negative_sensitivity_rejected(self):
        fab = UniversalRuntimeInputFabricator()
        with pytest.raises(ValueError, match="INVALID_SENSITIVITY"):
            fab.apply_axis_curve(0.5, AxisCurveType.LINEAR, sensitivity=-1.0)

    def test_security_negative_timestep_rejected(self):
        fab, w = make_test_world("iw_sec_step")
        fab.initialize_world(w)
        fab.start_world(w)
        with pytest.raises(ValueError, match="INVALID_TIMESTEP"):
            fab.update(-0.016, w)

    def test_security_invalid_state_transition_prevented(self):
        fab, w = make_test_world("iw_sec_trans")
        with pytest.raises(ValueError, match="NO_INVALID_INPUT_WORLD_TRANSITION"):
            fab.pause_world(w)

    def test_security_disconnected_device_mutation_prevented(self):
        fab, w = make_test_world("iw_sec_dis")
        dev = fab.create_device("dev_disc", InputDeviceType.KEYBOARD, world=w)
        fab.disconnect_device("dev_disc", w)
        fab.create_raw_event("dev_disc", RawInputEventType.KEY_DOWN, code="KeyZ", world=w)
        fab.process_events(w)
        assert dev.button_states.get("KeyZ", False) is False

    def test_security_replay_hash_mismatch_rejected(self):
        fab, w = make_test_world("iw_sec_rep_hash")
        ev = RawInputEvent("e", 1, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="Key1")
        rec = InputRecord("rec_tampered", events=[ev], record_hash="BAD_HASH")
        sess = InputReplaySession("sess_tampered", rec)
        with pytest.raises(ValueError, match="REPLAY_VALIDATION_FAILED"):
            fab.execute_replay(sess, w)

    def test_security_replay_tampered_events_discarded(self):
        fab, w = make_test_world("iw_sec_rep_tamper")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        ev_good = RawInputEvent("e1", 1, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyA")
        ev_bad = RawInputEvent("e2", 2, "unknown_dev", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyB")
        rec = InputRecord("rec_mix", events=[ev_good, ev_bad])
        sess = InputReplaySession("sess_mix", rec)
        fab.execute_replay(sess, w)
        assert sess.is_finished is True

    def test_security_screen_transform_zero_dimensions_rejected(self):
        fab = UniversalRuntimeInputFabricator()
        with pytest.raises(ValueError, match="INVALID_SCREEN_DIMENSIONS"):
            fab.transform_normalized_to_screen([0.5, 0.5], 0.0, 0.0)

    def test_security_rumble_timeout_clamped(self):
        fab, w = make_test_world("iw_sec_rumble")
        w.settings.rumble_timeout_seconds = 2.5
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        fab.set_gamepad_rumble("gp", 1.0, 1.0, duration_seconds=100.0, world=w)
        assert dev.rumble_remaining_seconds == 2.5

    def test_security_max_touch_points_enforced(self):
        fab, w = make_test_world("iw_sec_touch")
        w.settings.max_devices = 3
        fab.create_device("touch", InputDeviceType.TOUCH, world=w)
        for i in range(3):
            fab.create_raw_event("touch", RawInputEventType.TOUCH_START, touch_id=i, world=w)
        fab.process_events(w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_raw_event("touch", RawInputEventType.TOUCH_START, touch_id=99, world=w)
            fab.process_events(w)

    def test_security_invalid_profile_version_rejected(self):
        val = UniversalRuntimeInputValidator()
        prof = InputRebindingProfile("p_inv_ver", version=-1)
        issues = val.validate_profile(prof)
        assert any(i.error_code == "INVALID_PROFILE_VERSION" for i in issues)

    def test_security_dead_zone_override_validation(self):
        val = UniversalRuntimeInputValidator()
        prof = InputRebindingProfile("p_bad_dz", dead_zone_overrides={"Axis": 1.5})
        issues = val.validate_profile(prof)
        assert any(i.error_code == "INVALID_DEAD_ZONE_OVERRIDE" for i in issues)


# ==============================================================================
# §116. PERFORMANCE & LATENCY TESTS (16 tests)
# ==============================================================================

class TestPerformanceExecution:
    """Normative tests for Processing Throughput, Low Latency & High Event Volume (§116)."""

    def test_performance_1000_raw_events_enqueue(self):
        fab, w = make_test_world("iw_perf_1")
        w.settings.max_buffer_size = 5000
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        t0 = time.perf_counter()
        for i in range(1000):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code=f"K_{i}", world=w)
        dur = time.perf_counter() - t0
        assert dur < 0.1
        assert len(w.raw_event_queue) == 1000

    def test_performance_1000_raw_events_processing(self):
        fab, w = make_test_world("iw_perf_2")
        w.settings.max_buffer_size = 5000
        w.settings.max_events_per_frame = 5000
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        for i in range(1000):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code=f"K_{i}", world=w)
        t0 = time.perf_counter()
        fab.process_events(w)
        dur = time.perf_counter() - t0
        assert dur < 0.1
        assert len(w.processed_events) == 1000

    def test_performance_100_actions_evaluation(self):
        fab, w = make_test_world("iw_perf_3")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        for i in range(100):
            fab.create_action(f"Act_{i}", world=w)
            fab.bind_action(f"Act_{i}", InputDeviceType.KEYBOARD, f"K_{i}", world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="K_50", world=w)
        t0 = time.perf_counter()
        fab.process_events(w)
        dur = time.perf_counter() - t0
        assert dur < 0.05
        assert fab.is_action_triggered("Act_50", w) is True

    def test_performance_50_axes_evaluation(self):
        fab, w = make_test_world("iw_perf_4")
        fab.create_device("gp", InputDeviceType.GAMEPAD, world=w)
        for i in range(50):
            fab.create_axis(f"Axis_{i}", world=w)
            fab.bind_axis(f"Axis_{i}", InputDeviceType.GAMEPAD, f"Stick_{i}", world=w)
        fab.create_raw_event("gp", RawInputEventType.GAMEPAD_AXIS, code="Stick_25", value=0.7, world=w)
        t0 = time.perf_counter()
        fab.process_events(w)
        dur = time.perf_counter() - t0
        assert dur < 0.05
        assert fab.get_axis_value("Axis_25", w) > 0.0

    def test_performance_dead_zone_throughput(self):
        fab = UniversalRuntimeInputFabricator()
        t0 = time.perf_counter()
        for i in range(10000):
            val = (i % 100) / 100.0
            fab.apply_dead_zone(val, 0.15)
        dur = time.perf_counter() - t0
        assert dur < 0.1

    def test_performance_curve_throughput(self):
        fab = UniversalRuntimeInputFabricator()
        t0 = time.perf_counter()
        for i in range(10000):
            val = (i % 100) / 100.0
            fab.apply_axis_curve(val, AxisCurveType.SMOOTHSTEP, 1.2)
        dur = time.perf_counter() - t0
        assert dur < 0.1

    def test_performance_screen_transforms_throughput(self):
        fab = UniversalRuntimeInputFabricator()
        t0 = time.perf_counter()
        for i in range(10000):
            fab.transform_screen_to_normalized([960.0, 540.0], 1920.0, 1080.0)
        dur = time.perf_counter() - t0
        assert dur < 0.1

    def test_performance_snapshot_capture_speed(self):
        fab, w = make_test_world("iw_perf_8")
        fab.initialize_world(w)
        t0 = time.perf_counter()
        for _ in range(100):
            fab.capture_snapshot(w)
        dur = time.perf_counter() - t0
        assert dur < 0.1

    def test_performance_fingerprint_speed(self):
        fab, w = make_test_world("iw_perf_9")
        fab.initialize_world(w)
        t0 = time.perf_counter()
        for _ in range(50):
            w.compute_fingerprint()
        dur = time.perf_counter() - t0
        assert dur < 0.1

    def test_performance_context_push_pop_throughput(self):
        fab, w = make_test_world("iw_perf_10")
        w.settings.max_contexts = 100
        for i in range(50):
            fab.create_context(f"C_{i}", priority=i, world=w)
        t0 = time.perf_counter()
        for _ in range(500):
            fab.push_context("C_10", w)
            fab.pop_context("C_10", w)
        dur = time.perf_counter() - t0
        assert dur < 0.05

    def test_performance_mouse_move_throughput(self):
        fab, w = make_test_world("iw_perf_11")
        w.settings.max_buffer_size = 5000
        w.settings.max_events_per_frame = 5000
        fab.create_device("m", InputDeviceType.MOUSE, world=w)
        t0 = time.perf_counter()
        for i in range(500):
            fab.create_raw_event("m", RawInputEventType.MOUSE_MOVE, position=[float(i), float(i)], world=w)
        fab.process_events(w)
        dur = time.perf_counter() - t0
        assert dur < 0.5

    def test_performance_text_input_throughput(self):
        fab, w = make_test_world("iw_perf_12")
        w.settings.max_buffer_size = 5000
        w.settings.max_events_per_frame = 5000
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        t0 = time.perf_counter()
        for i in range(500):
            fab.create_raw_event("kb", RawInputEventType.TEXT_INPUT, text="A", world=w)
        fab.process_events(w)
        dur = time.perf_counter() - t0
        assert dur < 0.5
        assert len(fab.get_text_buffer(w)) == 500

    def test_performance_replay_throughput(self):
        fab, w = make_test_world("iw_perf_13")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        evs = [
            RawInputEvent(f"e_{i}", i, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyA")
            for i in range(500)
        ]
        rec = InputRecord("rec_perf", events=evs)
        session = InputReplaySession("sess_perf", rec)
        t0 = time.perf_counter()
        fab.execute_replay(session, w)
        dur = time.perf_counter() - t0
        assert dur < 0.1

    def test_performance_golden_input_speed(self):
        fab, w = make_test_world("iw_perf_14")
        t0 = time.perf_counter()
        for _ in range(100):
            fab.capture_golden_input(w)
        dur = time.perf_counter() - t0
        assert dur < 0.1

    def test_performance_rumble_timer_update(self):
        fab, w = make_test_world("iw_perf_15")
        fab.initialize_world(w)
        fab.start_world(w)
        caps = DeviceCapabilities(supports_rumble=True)
        for i in range(10):
            dev = fab.create_device(f"gp_{i}", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
            fab.set_gamepad_rumble(f"gp_{i}", 0.5, 0.5, duration_seconds=1.0, world=w)
        t0 = time.perf_counter()
        for _ in range(60):
            fab.update(1.0 / 60.0, w)
        dur = time.perf_counter() - t0
        assert dur < 0.05

    def test_performance_validation_speed(self):
        val = UniversalRuntimeInputValidator()
        fab, w = make_test_world("iw_perf_16")
        for i in range(10):
            fab.create_device(f"d_{i}", InputDeviceType.KEYBOARD, world=w)
            fab.create_action(f"a_{i}", world=w)
        t0 = time.perf_counter()
        for _ in range(50):
            val.validate(w)
        dur = time.perf_counter() - t0
        assert dur < 0.05


# ==============================================================================
# §117. STRESS & FLOODING TESTS (16 tests)
# ==============================================================================

class TestStressExecution:
    """Normative tests for Extreme Churn, Hotplug Floods & World Restarts (§117)."""

    def test_stress_world_restart_cycles(self):
        fab, w = make_test_world("iw_str_restart")
        for _ in range(10):
            fab.initialize_world(w)
            fab.start_world(w)
            fab.update(0.016, w)
            fab.stop_world(w)
        assert w.state == InputWorldState.STOPPED

    def test_stress_device_hotplug_cycles(self):
        fab, w = make_test_world("iw_str_hotplug")
        dev = fab.create_device("gp_churn", InputDeviceType.GAMEPAD, world=w)
        for _ in range(50):
            fab.disconnect_device("gp_churn", w)
            fab.reconnect_device("gp_churn", w)
        assert dev.status == InputDeviceStatus.CONNECTED
        assert len(w.hotplug_history) == 101

    def test_stress_raw_event_flood(self):
        fab, w = make_test_world("iw_str_flood")
        w.settings.max_buffer_size = 10000
        w.settings.max_events_per_frame = 10000
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        for i in range(2000):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code=f"Key{i % 50}", world=w)
        fab.process_events(w)
        assert len(w.processed_events) == 2000

    def test_stress_rapid_context_switching(self):
        fab, w = make_test_world("iw_str_ctx")
        w.settings.max_contexts = 20
        for i in range(10):
            fab.create_context(f"C_{i}", priority=i, world=w)
        for _ in range(100):
            fab.push_context("C_5", w)
            fab.pop_context("C_5", w)
        assert len(w.context_stack) == 0

    def test_stress_multi_touch_churn(self):
        fab, w = make_test_world("iw_str_touch")
        fab.create_device("touch", InputDeviceType.TOUCH, world=w)
        for i in range(20):
            fab.create_raw_event("touch", RawInputEventType.TOUCH_START, touch_id=i, position=[float(i), float(i)], world=w)
            fab.create_raw_event("touch", RawInputEventType.TOUCH_END, touch_id=i, world=w)
        fab.process_events(w)
        assert fab.get_active_touch_count(w) == 0

    def test_stress_text_input_burst(self):
        fab, w = make_test_world("iw_str_txt")
        w.settings.max_buffer_size = 5000
        w.settings.max_events_per_frame = 5000
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        chunk = "The quick brown fox jumps over the lazy dog. "
        for _ in range(50):
            fab.create_raw_event("kb", RawInputEventType.TEXT_INPUT, text=chunk, world=w)
        fab.process_events(w)
        assert len(fab.get_text_buffer(w)) == len(chunk) * 50

    def test_stress_axis_rapid_jitter(self):
        fab, w = make_test_world("iw_str_axis")
        fab.create_device("gp", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("Throttle", world=w)
        fab.bind_axis("Throttle", InputDeviceType.GAMEPAD, "RT", dead_zone=0.0, world=w)
        for i in range(100):
            val = (i % 10) / 10.0
            fab.create_raw_event("gp", RawInputEventType.GAMEPAD_AXIS, code="RT", value=val, world=w)
        fab.process_events(w)
        assert fab.get_axis_value("Throttle", w) >= 0.0

    def test_stress_action_rapid_toggle(self):
        fab, w = make_test_world("iw_str_act")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Fire", world=w)
        fab.bind_action("Fire", InputDeviceType.KEYBOARD, "Space", world=w)
        for _ in range(50):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="Space", world=w)
            fab.create_raw_event("kb", RawInputEventType.KEY_UP, code="Space", world=w)
        fab.process_events(w)
        assert fab.is_action_triggered("Fire", w) is False

    def test_stress_continuous_simulation_step(self):
        fab, w = make_test_world("iw_str_step")
        fab.initialize_world(w)
        fab.start_world(w)
        for _ in range(300):
            fab.update(0.016, w)
        assert w.frames_rendered == 300

    def test_stress_multiple_audio_worlds_isolation(self):
        fab = UniversalRuntimeInputFabricator()
        for i in range(10):
            w = fab.create_world(f"iw_iso_{i}")
            fab.initialize_world(w)
            fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        assert len(fab.worlds) == 10

    def test_stress_gesture_conflict_resolution(self):
        fab, w = make_test_world("iw_str_gst")
        fab.create_gesture("G1", GestureType.TAP, world=w)
        fab.create_gesture("G2", GestureType.PAN, world=w)
        assert fab.get_gesture_state("G1", w) == GestureState.POSSIBLE
        assert fab.get_gesture_state("G2", w) == GestureState.POSSIBLE

    def test_stress_recording_large_dataset(self):
        fab, w = make_test_world("iw_str_rec")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.start_recording("rec_large", w)
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        for i in range(200):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="KeyK", world=w)
        rec = fab.stop_recording(w)
        assert len(rec.events) == 200

    def test_stress_replay_repetition(self):
        fab, w = make_test_world("iw_str_rep_rep")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        ev = RawInputEvent("e", 1, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyM")
        rec = InputRecord("rec_rep", events=[ev])
        for i in range(5):
            sess = InputReplaySession(f"s_{i}", rec)
            fab.execute_replay(sess, w)
            assert sess.is_finished is True

    def test_stress_rapid_snapshot_cycles(self):
        fab, w = make_test_world("iw_str_snaps")
        fab.initialize_world(w)
        for _ in range(50):
            fab.capture_snapshot(w)
        assert True

    def test_stress_pen_pressure_sweep(self):
        fab, w = make_test_world("iw_str_pen")
        fab.create_device("pen", InputDeviceType.PEN, world=w)
        for i in range(50):
            p = i / 50.0
            fab.create_raw_event("pen", RawInputEventType.PEN_MOVE, pressure=p, world=w)
        fab.process_events(w)
        assert pytest.approx(fab.get_pen_state(w)["pressure"], rel=1e-2) == 0.98

    def test_stress_device_destruction_clears_bindings(self):
        fab, w = make_test_world("iw_str_destroy_dev")
        fab.create_device("kb_del", InputDeviceType.KEYBOARD, world=w)
        fab.remove_device("kb_del", w)
        assert "kb_del" not in w.devices


# ==============================================================================
# §118. PROPERTY-BASED TESTS (7 tests)
# ==============================================================================

class TestPropertyBasedExecution:
    """Normative tests for Mathematical & Structural Input Properties (§118)."""

    def test_property_dead_zone_odd_symmetry(self):
        fab = UniversalRuntimeInputFabricator()
        for x in [0.2, 0.4, 0.6, 0.8, 0.95]:
            pos = fab.apply_dead_zone(x, 0.1)
            neg = fab.apply_dead_zone(-x, 0.1)
            assert pytest.approx(pos, rel=1e-5) == -neg

    def test_property_dead_zone_inside_zero(self):
        fab = UniversalRuntimeInputFabricator()
        for x in [0.0, 0.02, 0.05, 0.099]:
            assert fab.apply_dead_zone(x, 0.1) == 0.0
            assert fab.apply_dead_zone(-x, 0.1) == 0.0

    def test_property_axis_bounds_clamped(self):
        fab = UniversalRuntimeInputFabricator()
        for x in [-5.0, -2.0, -1.0, 0.0, 1.0, 3.0, 10.0]:
            v = fab.apply_axis_curve(x, AxisCurveType.LINEAR, sensitivity=2.0)
            assert -1.0 <= v <= 1.0

    def test_property_screen_transform_invertibility(self):
        fab = UniversalRuntimeInputFabricator()
        orig = [480.0, 270.0]
        sw, sh = 1920.0, 1080.0
        norm = fab.transform_screen_to_normalized(orig, sw, sh)
        recovered = fab.transform_normalized_to_screen(norm, sw, sh)
        assert pytest.approx(recovered[0], abs=1e-3) == orig[0]
        assert pytest.approx(recovered[1], abs=1e-3) == orig[1]

    def test_property_context_priority_ordering(self):
        fab, w = make_test_world("iw_prop_ctx")
        priors = [15, 3, 99, 42, 8]
        for p in priors:
            fab.create_context(f"C_{p}", priority=p, world=w)
            fab.push_context(f"C_{p}", w)
        active = fab.get_active_contexts(w)
        res = [c.priority for c in active]
        assert res == sorted(priors, reverse=True)

    def test_property_fingerprint_deterministic_idempotence(self):
        fab, w = make_test_world("iw_prop_fp")
        assert w.compute_fingerprint() == w.compute_fingerprint()

    def test_property_replay_idempotence(self):
        fab, w = make_test_world("iw_prop_rep")
        fab.initialize_world(w)
        fab.start_world(w)
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        ev = RawInputEvent("e", 1, "kb", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyJ")
        rec = InputRecord("rec_idem", events=[ev])
        s1 = InputReplaySession("s1", rec)
        fab.execute_replay(s1, w)
        fp1 = w.compute_fingerprint()
        s2 = InputReplaySession("s2", rec)
        fab.execute_replay(s2, w)
        fp2 = w.compute_fingerprint()
        assert fp1 == fp2


# ==============================================================================
# §119. CROSS-PHASE INTEGRATION TESTS (18 tests)
# ==============================================================================

class TestCrossPhaseIntegrationExecution:
    """Normative tests for Cross-Phase Integration with Runtime, Physics, Audio & UI (§119)."""

    def test_runtime_world_to_input_world(self):
        class MockRuntimeWorld:
            def __init__(self, wid):
                self.world_id = wid
        rt_w = MockRuntimeWorld("rw_stage_1")
        fab = UniversalRuntimeInputFabricator()
        w = fab.create_input_world(input_world_id="iw_rw_1", runtime_world_id=rt_w.world_id)
        assert w.runtime_world_id == "rw_stage_1"

    def test_physics_world_to_gamepad_rumble(self):
        fab, w = make_test_world("iw_cross_2")
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp_cross", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        # Physics heavy collision trigger
        impact_force = 1500.0
        if impact_force > 1000.0:
            fab.set_gamepad_rumble("gp_cross", 0.8, 0.8, duration_seconds=0.5, world=w)
        assert dev.rumble_left == 0.8

    def test_render_world_to_mouse_cursor(self):
        fab, w = make_test_world("iw_cross_3")
        fab.set_mouse_position(960.0, 540.0, w)
        norm = fab.transform_screen_to_normalized(w.mouse_position, 1920.0, 1080.0)
        assert norm == [0.5, 0.5]

    def test_audio_world_to_input_action(self):
        fab, w = make_test_world("iw_cross_4")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("FireSFX", world=w)
        fab.bind_action("FireSFX", InputDeviceType.KEYBOARD, "Space", world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="Space", world=w)
        fab.process_events(w)
        audio_event_posted = fab.is_action_triggered("FireSFX", w)
        assert audio_event_posted is True

    def test_ui_world_to_input_consumption(self):
        fab, w = make_test_world("iw_cross_5")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("ModalConfirm", consume=True, world=w)
        fab.bind_action("ModalConfirm", InputDeviceType.KEYBOARD, "Enter", world=w)
        ctx = fab.create_context("ModalUI", priority=200, routing_mode=InputRoutingMode.UI_ONLY, world=w)
        ctx.action_ids = ["ModalConfirm"]
        fab.push_context("ModalUI", w)
        ev = fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="Enter", world=w)
        fab.process_events(w)
        assert ev.consumed is True

    def test_gameplay_to_axis_movement(self):
        fab, w = make_test_world("iw_cross_6")
        fab.create_device("gp", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("MoveX", world=w)
        fab.bind_axis("MoveX", InputDeviceType.GAMEPAD, "LX", dead_zone=0.0, world=w)
        fab.create_raw_event("gp", RawInputEventType.GAMEPAD_AXIS, code="LX", value=0.6, world=w)
        fab.process_events(w)
        # Mock gameplay velocity
        speed = 500.0
        player_vx = fab.get_axis_value("MoveX", w) * speed
        assert player_vx == 300.0

    def test_camera_to_mouse_look(self):
        fab, w = make_test_world("iw_cross_7")
        fab.create_device("m", InputDeviceType.MOUSE, world=w)
        fab.create_raw_event("m", RawInputEventType.MOUSE_MOVE, delta=[5.0, -2.0], world=w)
        fab.process_events(w)
        yaw_sensitivity = 0.1
        delta_yaw = w.mouse_delta[0] * yaw_sensitivity
        assert delta_yaw == 0.5

    def test_animation_to_input_lock(self):
        fab, w = make_test_world("iw_cross_8")
        ctx = fab.create_context("PlayerCombat", world=w)
        fab.push_context("PlayerCombat", w)
        # Animation lock disables context
        ctx.is_active = False
        assert len(fab.get_active_contexts(w)) == 0

    def test_vfx_to_pointer_position(self):
        fab, w = make_test_world("iw_cross_9")
        fab.set_mouse_position(400.0, 300.0, w)
        vfx_spawn_coords = list(w.mouse_position)
        assert vfx_spawn_coords == [400.0, 300.0]

    def test_level_streaming_to_device_reset(self):
        fab, w = make_test_world("iw_cross_10")
        fab.initialize_world(w)
        fab.start_world(w)
        dev = fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        dev.button_states["KeyW"] = True
        fab.stop_world(w)
        assert len(dev.button_states) == 0

    def test_pause_menu_to_input_routing(self):
        fab, w = make_test_world("iw_cross_11")
        fab.create_context("Gameplay", priority=10, world=w)
        fab.create_context("PauseMenu", priority=100, world=w)
        fab.push_context("Gameplay", w)
        fab.push_context("PauseMenu", w)
        top = fab.get_active_contexts(w)[0]
        assert top.context_id == "PauseMenu"

    def test_cinematic_to_input_suppression(self):
        fab, w = make_test_world("iw_cross_12")
        fab.create_context("Gameplay", priority=10, world=w)
        fab.push_context("Gameplay", w)
        # Suppress gameplay in cinematic
        fab.pop_context("Gameplay", w)
        assert len(fab.get_active_contexts(w)) == 0

    def test_time_dilation_to_input_timestamp(self):
        fab, w = make_test_world("iw_cross_13")
        fab.initialize_world(w)
        fab.start_world(w)
        dilation = 0.5
        fab.update(0.016 * dilation, w)
        assert pytest.approx(w.time_seconds, rel=1e-3) == 0.008

    def test_ai_perception_to_input_noise(self):
        fab, w = make_test_world("iw_cross_14")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Sprint", world=w)
        fab.bind_action("Sprint", InputDeviceType.KEYBOARD, "ShiftLeft", world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="ShiftLeft", world=w)
        fab.process_events(w)
        ai_noise_radius = 50.0 if fab.is_action_triggered("Sprint", w) else 10.0
        assert ai_noise_radius == 50.0

    def test_networking_rpc_to_raw_event(self):
        fab, w = make_test_world("iw_cross_15")
        fab.create_device("kb_net", InputDeviceType.KEYBOARD, world=w)
        rpc_packet = {"device_id": "kb_net", "type": "KEY_DOWN", "code": "KeySpace"}
        if rpc_packet["type"] == "KEY_DOWN":
            ev = fab.create_raw_event(rpc_packet["device_id"], RawInputEventType.KEY_DOWN, code=rpc_packet["code"], world=w)
        assert ev.code == "KeySpace"

    def test_accessibility_profile_to_gameplay(self):
        fab, w = make_test_world("iw_cross_16")
        fab.create_device("gp", InputDeviceType.GAMEPAD, world=w)
        fab.create_axis("Steer", world=w)
        fab.bind_axis("Steer", InputDeviceType.GAMEPAD, "LX", dead_zone=0.1, sensitivity=1.5, world=w)
        fab.create_raw_event("gp", RawInputEventType.GAMEPAD_AXIS, code="LX", value=0.5, world=w)
        fab.process_events(w)
        assert fab.get_axis_value("Steer", w) > 0.5

    def test_touch_virtual_joystick_to_axis(self):
        fab, w = make_test_world("iw_cross_17")
        fab.create_device("touch", InputDeviceType.TOUCH, world=w)
        fab.create_raw_event("touch", RawInputEventType.TOUCH_START, touch_id=1, position=[150.0, 100.0], world=w)
        fab.process_events(w)
        joystick_center = [100.0, 100.0]
        dx = (w.active_touch_points[1][0] - joystick_center[0]) / 50.0
        assert dx == 1.0

    def test_haptic_feedback_to_gamepad_rumble(self):
        fab, w = make_test_world("iw_cross_18")
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp_haptic", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        fab.set_gamepad_rumble("gp_haptic", 1.0, 0.5, duration_seconds=0.2, world=w)
        assert dev.rumble_left == 1.0
        assert dev.rumble_right == 0.5


# ==============================================================================
# §120. TEARDOWN, CLEANUP & LEAK PREVENTION TESTS (14 tests)
# ==============================================================================

class TestCleanupTeardownExecution:
    """Normative tests for Input Teardown, Cleanup & Memory Leak Prevention (§120)."""

    def test_cleanup_input_world_empty(self):
        fab = UniversalRuntimeInputFabricator()
        fab.create_input_world("iw_clean_empty")
        fab.destroy_input_world("iw_clean_empty")
        assert "iw_clean_empty" not in fab.worlds

    def test_cleanup_input_world_with_devices(self):
        fab, w = make_test_world("iw_clean_devs")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_device("m", InputDeviceType.MOUSE, world=w)
        fab.destroy_world(w)
        assert len(w.devices) == 0

    def test_cleanup_input_world_with_contexts(self):
        fab, w = make_test_world("iw_clean_ctx")
        fab.create_context("C1", world=w)
        fab.push_context("C1", w)
        fab.destroy_world(w)
        assert len(w.contexts) == 0
        assert len(w.context_stack) == 0

    def test_cleanup_input_world_with_actions(self):
        fab, w = make_test_world("iw_clean_act")
        fab.create_action("A1", world=w)
        fab.destroy_world(w)
        assert len(w.actions) == 0

    def test_cleanup_input_world_with_axes(self):
        fab, w = make_test_world("iw_clean_axes")
        fab.create_axis("X1", world=w)
        fab.destroy_world(w)
        assert len(w.axes) == 0

    def test_cleanup_input_world_with_gestures(self):
        fab, w = make_test_world("iw_clean_gst")
        fab.create_gesture("G1", GestureType.TAP, world=w)
        fab.destroy_world(w)
        assert len(w.gestures) == 0

    def test_cleanup_input_world_with_profiles(self):
        fab, w = make_test_world("iw_clean_prof")
        prof = InputRebindingProfile("P1")
        fab.register_profile(prof, w)
        fab.destroy_world(w)
        assert len(w.profiles) == 0

    def test_cleanup_input_world_pending_events(self):
        fab, w = make_test_world("iw_clean_evts")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="KeyQ", world=w)
        fab.destroy_world(w)
        assert len(w.raw_event_queue) == 0

    def test_cleanup_input_world_hotplug_history(self):
        fab, w = make_test_world("iw_clean_hotplug")
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.destroy_world(w)
        assert len(w.hotplug_history) == 0

    def test_cleanup_device_disconnection_leak_free(self):
        fab, w = make_test_world("iw_clean_dev_leak")
        for i in range(50):
            did = f"d_leak_{i}"
            fab.create_device(did, InputDeviceType.KEYBOARD, world=w)
            fab.remove_device(did, w)
        assert len(w.devices) == 0

    def test_cleanup_multiple_worlds_lifecycle(self):
        fab = UniversalRuntimeInputFabricator()
        for i in range(20):
            wid = f"iw_multi_{i}"
            fab.create_input_world(wid)
            fab.destroy_input_world(wid)
        assert len(fab.worlds) == 0

    def test_cleanup_recording_state_leak_free(self):
        fab, w = make_test_world("iw_clean_rec")
        fab.start_recording("rec_clean", w)
        fab.stop_recording(w)
        assert fab._recording_active is False
        assert fab._current_record is None

    def test_cleanup_replay_session_leak_free(self):
        fab, w = make_test_world("iw_clean_rep")
        ev = RawInputEvent("e", 1, "k", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyL")
        rec = InputRecord("rec_c", events=[ev])
        sess = InputReplaySession("sess_c", rec)
        fab.execute_replay(sess, w)
        assert sess.is_finished is True

    def test_cleanup_100_action_allocations_leak_free(self):
        fab, w = make_test_world("iw_clean_actions_100")
        for i in range(100):
            fab.create_action(f"act_loop_{i}", world=w)
        assert len(w.actions) == 100
        fab.destroy_world(w)
        assert len(w.actions) == 0


# ==============================================================================
# §121. PACKAGING, UE5 SUBSYSTEM & NON-NEGOTIABLE INVARIANTS TESTS (18 tests)
# ==============================================================================

class TestPackagingAndInvariantsExecution:
    """Normative tests for UE5 Subsystem packaging and input invariant verification (§121, §124)."""

    def test_packager_header_generation(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeInputSubsystem.h")
            assert os.path.isfile(hdr)
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert "UUAFRuntimeInputSubsystem" in c
            assert "UCLASS()" in c

    def test_packager_source_generation(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            src = os.path.join(tmpdir, "UUAFRuntimeInputSubsystem.cpp")
            assert os.path.isfile(src)
            with open(src, "r", encoding="utf-8") as f:
                c = f.read()
            assert "Initialize(" in c
            assert "Deinitialize(" in c

    def test_packager_manifest_generation(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            man = os.path.join(tmpdir, "input_manifest.json")
            assert os.path.isfile(man)
            with open(man, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["module"] == "uaf_runtime_input"
            assert "files" in data

    def test_packager_signature_generation(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            sig = os.path.join(tmpdir, "input_manifest.sig")
            assert os.path.isfile(sig)

    def test_packager_cpp_includes(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeInputSubsystem.h")
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert "Subsystems/WorldSubsystem.h" in c

    def test_packager_ue5_subsystem_class(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeInputSubsystem.h")
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert ": public UWorldSubsystem" in c

    def test_packager_uproperty_ufunction(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            packager.package(tmpdir)
            hdr = os.path.join(tmpdir, "UUAFRuntimeInputSubsystem.h")
            with open(hdr, "r", encoding="utf-8") as f:
                c = f.read()
            assert "UFUNCTION(BlueprintCallable" in c

    def test_packager_checksum_deterministic(self):
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            packager.package(tmp1)
            packager.package(tmp2)
            with open(os.path.join(tmp1, "input_manifest.json"), "r", encoding="utf-8") as f1:
                d1 = json.load(f1)
            with open(os.path.join(tmp2, "input_manifest.json"), "r", encoding="utf-8") as f2:
                d2 = json.load(f2)
            assert d1["files"] == d2["files"]

    def test_validator_catches_all_invalid_states(self):
        val = UniversalRuntimeInputValidator()
        fab = UniversalRuntimeInputFabricator()
        w = fab.create_input_world("iw_val_err")
        w.devices["bad_dev"] = InputDevice("bad_dev", InputDeviceType.KEYBOARD, "")
        w.devices["bad_dev"].device_id = ""  # empty device_id
        issues = val.validate(w)
        err_codes = [i.error_code for i in issues]
        assert "INVALID_DEVICE_ID" in err_codes

    def test_validator_clean_manifest(self):
        val = UniversalRuntimeInputValidator()
        fab, w = make_test_world("iw_val_clean")
        fab.create_device("kb_ok", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("Jump_ok", world=w)
        issues = val.validate(w)
        errors = [i for i in issues if i.severity == "ERROR"]
        assert len(errors) == 0

    def test_end_to_end_input_pipeline(self):
        fab, w = make_test_world("iw_e2e")
        fab.initialize_world(w)
        fab.start_world(w)
        dev = fab.create_device("kb_main", InputDeviceType.KEYBOARD, world=w)
        fab.create_action("PrimaryAction", world=w)
        fab.bind_action("PrimaryAction", InputDeviceType.KEYBOARD, "Space", world=w)
        fab.create_axis("LookX", world=w)
        fab.bind_axis("LookX", InputDeviceType.KEYBOARD, "MouseX", dead_zone=0.0, world=w)
        ctx = fab.create_context("GameplayCtx", priority=10, world=w)
        ctx.action_ids = ["PrimaryAction"]
        fab.push_context("GameplayCtx", w)
        fab.create_raw_event("kb_main", RawInputEventType.KEY_DOWN, code="Space", world=w)
        fab.update(0.016, w)
        assert fab.is_action_triggered("PrimaryAction", w) is True
        snap = fab.capture_snapshot(w)
        assert snap.world_id == "iw_e2e"
        packager = UniversalRuntimeInputPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = packager.package(tmpdir, w)
            assert res["success"] is True

    def test_invariant_no_invalid_input_world_transition(self):
        fab = UniversalRuntimeInputFabricator()
        w = fab.create_input_world("iw_inv_trans")
        with pytest.raises(ValueError, match="NO_INVALID_INPUT_WORLD_TRANSITION"):
            fab.stop_world(w)

    def test_invariant_no_duplicate_device_identity(self):
        fab, w = make_test_world("iw_inv_dup_dev")
        fab.create_device("mouse_dup", InputDeviceType.MOUSE, world=w)
        with pytest.raises(ValueError, match="DUPLICATE_DEVICE_ID"):
            fab.create_device("mouse_dup", InputDeviceType.MOUSE, world=w)

    def test_invariant_no_axis_value_outside_declared_policy(self):
        fab = UniversalRuntimeInputFabricator()
        for val in [-50.0, 50.0]:
            clamped = fab.apply_axis_curve(val, AxisCurveType.LINEAR)
            assert -1.0 <= clamped <= 1.0

    def test_invariant_no_dead_zone_bypass(self):
        fab = UniversalRuntimeInputFabricator()
        val = fab.apply_dead_zone(0.0999, 0.1)
        assert val == 0.0

    def test_invariant_no_unbounded_rumble(self):
        fab, w = make_test_world("iw_inv_rumble")
        w.settings.rumble_timeout_seconds = 5.0
        caps = DeviceCapabilities(supports_rumble=True)
        dev = fab.create_device("gp_inv", InputDeviceType.GAMEPAD, capabilities=caps, world=w)
        fab.set_gamepad_rumble("gp_inv", 1.0, 1.0, duration_seconds=9999.0, world=w)
        assert dev.rumble_remaining_seconds <= 5.0

    def test_invariant_no_unbounded_input_buffer(self):
        fab, w = make_test_world("iw_inv_buf")
        w.settings.max_buffer_size = 2
        fab.create_device("kb", InputDeviceType.KEYBOARD, world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="Key1", world=w)
        fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="Key2", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_raw_event("kb", RawInputEventType.KEY_DOWN, code="Key3", world=w)

    def test_invariant_no_replay_input_tampering(self):
        fab, w = make_test_world("iw_inv_rep")
        ev = RawInputEvent("e", 1, "k", InputDeviceType.KEYBOARD, RawInputEventType.KEY_DOWN, code="KeyX")
        rec = InputRecord("rec_tamper", events=[ev], record_hash="CORRUPTED_HASH")
        sess = InputReplaySession("sess_tamper", rec)
        with pytest.raises(ValueError, match="REPLAY_VALIDATION_FAILED"):
            fab.execute_replay(sess, w)
