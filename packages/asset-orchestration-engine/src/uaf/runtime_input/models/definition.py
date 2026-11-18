"""
Universal Runtime Input World Models (UAF-81.77).
Defines device abstractions, raw input events, action/axis bindings,
input contexts, gestures, rebinding profiles, replay, and input invariants.
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union


def copy_dict_deterministic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Returns a deterministically sorted copy of a dictionary."""
    return {k: data[k] for k in sorted(data.keys())}


class InputWorldState(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class InputDeviceType(str, Enum):
    KEYBOARD = "KEYBOARD"
    MOUSE = "MOUSE"
    POINTER = "POINTER"
    GAMEPAD = "GAMEPAD"
    TOUCH = "TOUCH"
    PEN = "PEN"


class InputDeviceStatus(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class RawInputEventType(str, Enum):
    KEY_DOWN = "KEY_DOWN"
    KEY_UP = "KEY_UP"
    MOUSE_MOVE = "MOUSE_MOVE"
    MOUSE_DOWN = "MOUSE_DOWN"
    MOUSE_UP = "MOUSE_UP"
    MOUSE_WHEEL = "MOUSE_WHEEL"
    GAMEPAD_AXIS = "GAMEPAD_AXIS"
    GAMEPAD_BUTTON_DOWN = "GAMEPAD_BUTTON_DOWN"
    GAMEPAD_BUTTON_UP = "GAMEPAD_BUTTON_UP"
    TOUCH_START = "TOUCH_START"
    TOUCH_MOVE = "TOUCH_MOVE"
    TOUCH_END = "TOUCH_END"
    TOUCH_CANCEL = "TOUCH_CANCEL"
    PEN_MOVE = "PEN_MOVE"
    PEN_DOWN = "PEN_DOWN"
    PEN_UP = "PEN_UP"
    TEXT_INPUT = "TEXT_INPUT"


class DeadZoneMode(str, Enum):
    NONE = "NONE"
    AXIAL = "AXIAL"
    RADIAL = "RADIAL"


class AxisCurveType(str, Enum):
    LINEAR = "LINEAR"
    EXPONENTIAL = "EXPONENTIAL"
    LOGARITHMIC = "LOGARITHMIC"
    SMOOTHSTEP = "SMOOTHSTEP"
    SENSITIVITY_CURVE = "SENSITIVITY_CURVE"


class GestureType(str, Enum):
    TAP = "TAP"
    DOUBLE_TAP = "DOUBLE_TAP"
    LONG_PRESS = "LONG_PRESS"
    PAN = "PAN"
    PINCH = "PINCH"
    SWIPE = "SWIPE"
    ROTATE = "ROTATE"


class GestureState(str, Enum):
    POSSIBLE = "POSSIBLE"
    BEGAN = "BEGAN"
    CHANGED = "CHANGED"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class InputRoutingMode(str, Enum):
    ROUTE_ALL = "ROUTE_ALL"
    ROUTE_FIRST_CONSUMED = "ROUTE_FIRST_CONSUMED"
    UI_ONLY = "UI_ONLY"
    GAMEPLAY_ONLY = "GAMEPLAY_ONLY"


class InputModifierKey(str, Enum):
    SHIFT = "SHIFT"
    CONTROL = "CONTROL"
    ALT = "ALT"
    META = "META"


class ActionTriggerState(str, Enum):
    NONE = "NONE"
    TRIGGERED = "TRIGGERED"
    STARTED = "STARTED"
    ONGOING = "ONGOING"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"


@dataclass
class DeviceCapabilities:
    supports_buttons: bool = True
    button_count: int = 128
    supports_axes: bool = False
    axis_count: int = 0
    supports_touch: bool = False
    max_touch_points: int = 0
    supports_pressure: bool = False
    supports_tilt: bool = False
    supports_rumble: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supports_buttons": self.supports_buttons,
            "button_count": self.button_count,
            "supports_axes": self.supports_axes,
            "axis_count": self.axis_count,
            "supports_touch": self.supports_touch,
            "max_touch_points": self.max_touch_points,
            "supports_pressure": self.supports_pressure,
            "supports_tilt": self.supports_tilt,
            "supports_rumble": self.supports_rumble,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class InputDevice:
    device_id: str
    device_type: InputDeviceType
    vendor_id: str = ""
    product_id: str = ""
    instance_id: int = 0
    status: InputDeviceStatus = InputDeviceStatus.CONNECTED
    capabilities: DeviceCapabilities = field(default_factory=DeviceCapabilities)
    button_states: Dict[str, bool] = field(default_factory=dict)
    axis_states: Dict[str, float] = field(default_factory=dict)
    rumble_left: float = 0.0
    rumble_right: float = 0.0
    rumble_remaining_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_type": self.device_type.value,
            "vendor_id": self.vendor_id,
            "product_id": self.product_id,
            "instance_id": self.instance_id,
            "status": self.status.value,
            "capabilities": self.capabilities.to_dict(),
            "button_states": copy_dict_deterministic(self.button_states),
            "axis_states": {k: round(float(v), 6) for k, v in sorted(self.axis_states.items())},
            "rumble_left": round(float(self.rumble_left), 6),
            "rumble_right": round(float(self.rumble_right), 6),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class RawInputEvent:
    event_id: str
    sequence_number: int
    device_id: str
    device_type: InputDeviceType
    event_type: RawInputEventType
    code: str = ""
    value: float = 0.0
    position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    delta: List[float] = field(default_factory=lambda: [0.0, 0.0])
    pressure: float = 1.0
    tilt: List[float] = field(default_factory=lambda: [0.0, 0.0])
    touch_id: int = 0
    text: str = ""
    modifiers: List[str] = field(default_factory=list)
    timestamp: float = 0.0
    consumed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "sequence_number": self.sequence_number,
            "device_id": self.device_id,
            "device_type": self.device_type.value,
            "event_type": self.event_type.value,
            "code": self.code,
            "value": round(float(self.value), 6),
            "position": [round(float(p), 6) for p in self.position],
            "delta": [round(float(d), 6) for d in self.delta],
            "pressure": round(float(self.pressure), 6),
            "tilt": [round(float(t), 6) for t in self.tilt],
            "touch_id": self.touch_id,
            "text": self.text,
            "modifiers": sorted(self.modifiers),
            "timestamp": round(float(self.timestamp), 6),
            "consumed": self.consumed,
        }


@dataclass
class ActionBinding:
    binding_id: str
    device_type: InputDeviceType
    code: str
    modifiers: List[str] = field(default_factory=list)
    chords: List[str] = field(default_factory=list)
    hold_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "device_type": self.device_type.value,
            "code": self.code,
            "modifiers": sorted(self.modifiers),
            "chords": sorted(self.chords),
            "hold_time": round(float(self.hold_time), 6),
        }


@dataclass
class InputAction:
    action_id: str
    bindings: List[ActionBinding] = field(default_factory=list)
    state: ActionTriggerState = ActionTriggerState.NONE
    is_pressed: bool = False
    value: float = 0.0
    priority: int = 100
    consume: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "bindings": [b.to_dict() for b in self.bindings],
            "state": self.state.value,
            "is_pressed": self.is_pressed,
            "value": round(float(self.value), 6),
            "priority": self.priority,
            "consume": self.consume,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class AxisBinding:
    binding_id: str
    device_type: InputDeviceType
    code: str
    scale: float = 1.0
    dead_zone: float = 0.1
    dead_zone_mode: DeadZoneMode = DeadZoneMode.AXIAL
    sensitivity: float = 1.0
    curve: AxisCurveType = AxisCurveType.LINEAR
    invert: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "device_type": self.device_type.value,
            "code": self.code,
            "scale": round(float(self.scale), 6),
            "dead_zone": round(float(self.dead_zone), 6),
            "dead_zone_mode": self.dead_zone_mode.value,
            "sensitivity": round(float(self.sensitivity), 6),
            "curve": self.curve.value,
            "invert": self.invert,
        }


@dataclass
class InputAxis:
    axis_id: str
    bindings: List[AxisBinding] = field(default_factory=list)
    raw_value: float = 0.0
    value: float = 0.0
    composite_positive: str = ""
    composite_negative: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "axis_id": self.axis_id,
            "bindings": [b.to_dict() for b in self.bindings],
            "raw_value": round(float(self.raw_value), 6),
            "value": round(float(self.value), 6),
            "composite_positive": self.composite_positive,
            "composite_negative": self.composite_negative,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class GestureBinding:
    gesture_id: str
    gesture_type: GestureType
    state: GestureState = GestureState.POSSIBLE
    min_duration: float = 0.0
    max_duration: float = 0.5
    min_distance: float = 10.0
    tap_count: int = 1
    touch_points: int = 1
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0])
    scale: float = 1.0
    rotation: float = 0.0
    start_position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    current_position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    elapsed_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gesture_id": self.gesture_id,
            "gesture_type": self.gesture_type.value,
            "state": self.state.value,
            "min_duration": round(float(self.min_duration), 6),
            "max_duration": round(float(self.max_duration), 6),
            "min_distance": round(float(self.min_distance), 6),
            "tap_count": self.tap_count,
            "touch_points": self.touch_points,
            "velocity": [round(float(v), 6) for v in self.velocity],
            "scale": round(float(self.scale), 6),
            "rotation": round(float(self.rotation), 6),
        }


@dataclass
class InputContext:
    context_id: str
    priority: int = 0
    action_ids: List[str] = field(default_factory=list)
    axis_ids: List[str] = field(default_factory=list)
    gesture_ids: List[str] = field(default_factory=list)
    routing_mode: InputRoutingMode = InputRoutingMode.ROUTE_ALL
    consume_unhandled: bool = False
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "priority": self.priority,
            "action_ids": sorted(self.action_ids),
            "axis_ids": sorted(self.axis_ids),
            "gesture_ids": sorted(self.gesture_ids),
            "routing_mode": self.routing_mode.value,
            "consume_unhandled": self.consume_unhandled,
            "is_active": self.is_active,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class InputRebindingProfile:
    profile_id: str
    user_id: str = "default"
    version: int = 1
    action_overrides: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    axis_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    dead_zone_overrides: Dict[str, float] = field(default_factory=dict)
    sensitivity_overrides: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "user_id": self.user_id,
            "version": self.version,
            "action_overrides": copy_dict_deterministic(self.action_overrides),
            "axis_overrides": copy_dict_deterministic(self.axis_overrides),
            "dead_zone_overrides": {k: round(float(v), 6) for k, v in sorted(self.dead_zone_overrides.items())},
            "sensitivity_overrides": {k: round(float(v), 6) for k, v in sorted(self.sensitivity_overrides.items())},
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class InputSnapshot:
    snapshot_id: str
    world_id: str = ""
    timestamp: float = 0.0
    keyboard_state: Dict[str, bool] = field(default_factory=dict)
    mouse_position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    mouse_buttons: Dict[str, bool] = field(default_factory=dict)
    gamepad_axes: Dict[str, float] = field(default_factory=dict)
    gamepad_buttons: Dict[str, bool] = field(default_factory=dict)
    active_contexts: List[str] = field(default_factory=list)
    snapshot_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "world_id": self.world_id,
            "timestamp": round(float(self.timestamp), 6),
            "keyboard_state": copy_dict_deterministic(self.keyboard_state),
            "mouse_position": [round(float(p), 6) for p in self.mouse_position],
            "mouse_buttons": copy_dict_deterministic(self.mouse_buttons),
            "gamepad_axes": {k: round(float(v), 6) for k, v in sorted(self.gamepad_axes.items())},
            "gamepad_buttons": copy_dict_deterministic(self.gamepad_buttons),
            "active_contexts": sorted(self.active_contexts),
            "snapshot_hash": self.snapshot_hash,
        }


@dataclass
class InputRecord:
    record_id: str
    events: List[RawInputEvent] = field(default_factory=list)
    start_timestamp: float = 0.0
    duration_seconds: float = 0.0
    frame_count: int = 0
    record_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "events": [e.to_dict() for e in self.events],
            "start_timestamp": round(float(self.start_timestamp), 6),
            "duration_seconds": round(float(self.duration_seconds), 6),
            "frame_count": self.frame_count,
            "record_hash": self.record_hash,
        }


@dataclass
class InputReplaySession:
    session_id: str
    record: InputRecord
    current_index: int = 0
    is_finished: bool = False
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "record_id": self.record.record_id,
            "current_index": self.current_index,
            "is_finished": self.is_finished,
            "is_valid": self.is_valid,
        }


@dataclass
class DeviceHotplugEvent:
    event_id: str
    device_id: str
    is_connected: bool
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "device_id": self.device_id,
            "is_connected": self.is_connected,
            "timestamp": round(float(self.timestamp), 6),
        }


@dataclass
class InputWorldSettings:
    max_devices: int = 32
    max_events_per_frame: int = 1024
    max_buffer_size: int = 4096
    max_contexts: int = 64
    max_actions: int = 256
    max_axes: int = 128
    rumble_timeout_seconds: float = 5.0
    default_mouse_sensitivity: float = 1.0
    accessibility_sticky_keys: bool = False
    accessibility_slow_keys_duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_devices": self.max_devices,
            "max_events_per_frame": self.max_events_per_frame,
            "max_buffer_size": self.max_buffer_size,
            "max_contexts": self.max_contexts,
            "max_actions": self.max_actions,
            "max_axes": self.max_axes,
            "rumble_timeout_seconds": round(float(self.rumble_timeout_seconds), 6),
            "default_mouse_sensitivity": round(float(self.default_mouse_sensitivity), 6),
            "accessibility_sticky_keys": self.accessibility_sticky_keys,
            "accessibility_slow_keys_duration": round(float(self.accessibility_slow_keys_duration), 6),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class InputWorld:
    input_world_id: str
    runtime_world_id: str = ""
    state: InputWorldState = InputWorldState.CREATED
    settings: InputWorldSettings = field(default_factory=InputWorldSettings)
    devices: Dict[str, InputDevice] = field(default_factory=dict)
    contexts: Dict[str, InputContext] = field(default_factory=dict)
    context_stack: List[str] = field(default_factory=list)
    actions: Dict[str, InputAction] = field(default_factory=dict)
    axes: Dict[str, InputAxis] = field(default_factory=dict)
    gestures: Dict[str, GestureBinding] = field(default_factory=dict)
    profiles: Dict[str, InputRebindingProfile] = field(default_factory=dict)
    active_profile_id: str = "default"
    raw_event_queue: List[RawInputEvent] = field(default_factory=list)
    processed_events: List[RawInputEvent] = field(default_factory=list)
    hotplug_history: List[DeviceHotplugEvent] = field(default_factory=list)
    time_seconds: float = 0.0
    frames_rendered: int = 0
    content_fingerprint: str = ""
    modifiers_state: Set[str] = field(default_factory=set)
    mouse_position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    mouse_delta: List[float] = field(default_factory=lambda: [0.0, 0.0])
    mouse_buttons: Dict[str, bool] = field(default_factory=dict)
    mouse_captured: bool = False
    active_touch_points: Dict[int, List[float]] = field(default_factory=dict)
    pen_position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    pen_pressure: float = 0.0
    pen_tilt: List[float] = field(default_factory=lambda: [0.0, 0.0])
    pen_barrel_button: bool = False
    text_buffer: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_world_id": self.input_world_id,
            "runtime_world_id": self.runtime_world_id,
            "state": self.state.value,
            "settings": self.settings.to_dict(),
            "devices": {k: self.devices[k].to_dict() for k in sorted(self.devices.keys())},
            "contexts": {k: self.contexts[k].to_dict() for k in sorted(self.contexts.keys())},
            "context_stack": list(self.context_stack),
            "actions": {k: self.actions[k].to_dict() for k in sorted(self.actions.keys())},
            "axes": {k: self.axes[k].to_dict() for k in sorted(self.axes.keys())},
            "gestures": {k: self.gestures[k].to_dict() for k in sorted(self.gestures.keys())},
            "profiles": {k: self.profiles[k].to_dict() for k in sorted(self.profiles.keys())},
            "active_profile_id": self.active_profile_id,
            "time_seconds": round(float(self.time_seconds), 6),
            "frames_rendered": self.frames_rendered,
            "modifiers_state": sorted(list(self.modifiers_state)),
            "mouse_position": [round(float(p), 6) for p in self.mouse_position],
            "mouse_captured": self.mouse_captured,
            "content_fingerprint": self.content_fingerprint,
        }

    def compute_fingerprint(self) -> str:
        data = self.to_dict()
        data["content_fingerprint"] = ""
        raw_json = json.dumps(data, indent=2, sort_keys=True)
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
