"""
Universal Runtime Input Fabricator (UAF-81.77).
Implements the runtime input engine, device management, event normalization,
action and axis mappings, context stack, gestures, recording, and replay.
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ..models.definition import (
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
)


class UniversalRuntimeInputFabricator:
    """Normative fabricator and lifecycle controller for Runtime Input Worlds."""

    def __init__(self) -> None:
        self.worlds: Dict[str, InputWorld] = {}
        self.active_world: Optional[InputWorld] = None
        self._sequence_counter: int = 0
        self._recording_active: bool = False
        self._current_record: Optional[InputRecord] = None

    # --------------------------------------------------------------------------
    # 1. World Lifecycle
    # --------------------------------------------------------------------------

    def create_world(
        self,
        input_world_id: str,
        runtime_world_id: str = "",
        settings: Optional[InputWorldSettings] = None,
    ) -> InputWorld:
        if not input_world_id or not input_world_id.strip():
            raise ValueError("INVALID_INPUT_WORLD_ID: World ID cannot be empty.")
        if input_world_id in self.worlds:
            raise ValueError(f"DUPLICATE_INPUT_WORLD_ID: World '{input_world_id}' already exists.")

        world = InputWorld(
            input_world_id=input_world_id,
            runtime_world_id=runtime_world_id,
            state=InputWorldState.CREATED,
            settings=settings or InputWorldSettings(),
        )
        self.worlds[input_world_id] = world
        self.active_world = world
        return world

    create_input_world = create_world

    def get_world(self, input_world_id: str) -> Optional[InputWorld]:
        return self.worlds.get(input_world_id)

    def initialize_world(self, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (InputWorldState.CREATED, InputWorldState.INITIALIZING, InputWorldState.STOPPED):
            raise ValueError(f"NO_INVALID_INPUT_WORLD_TRANSITION: Cannot initialize from '{target.state.value}'.")

        target.state = InputWorldState.READY
        target.content_fingerprint = target.compute_fingerprint()

    def start_world(self, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (InputWorldState.READY, InputWorldState.PAUSED, InputWorldState.STOPPED):
            raise ValueError(f"NO_INVALID_INPUT_WORLD_TRANSITION: Cannot start world from '{target.state.value}'.")

        target.state = InputWorldState.RUNNING

    start_input = start_world

    def pause_world(self, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state != InputWorldState.RUNNING:
            raise ValueError(f"NO_INVALID_INPUT_WORLD_TRANSITION: Cannot pause from '{target.state.value}'.")

        target.state = InputWorldState.PAUSED

    def stop_world(self, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (InputWorldState.RUNNING, InputWorldState.PAUSED):
            raise ValueError(f"NO_INVALID_INPUT_WORLD_TRANSITION: Cannot stop from '{target.state.value}'.")

        # Clear active inputs
        target.raw_event_queue.clear()
        for dev in target.devices.values():
            dev.button_states.clear()
            dev.axis_states.clear()
            dev.rumble_left = 0.0
            dev.rumble_right = 0.0
            dev.rumble_remaining_seconds = 0.0
        target.modifiers_state.clear()
        target.mouse_buttons.clear()
        target.active_touch_points.clear()
        for act in target.actions.values():
            act.state = ActionTriggerState.NONE
            act.is_pressed = False
            act.value = 0.0
        for ax in target.axes.values():
            ax.raw_value = 0.0
            ax.value = 0.0
        target.state = InputWorldState.STOPPED

    def advance_state(self, world_id_or_world: Any, new_state: InputWorldState) -> None:
        if isinstance(world_id_or_world, str):
            target = self.worlds.get(world_id_or_world)
        else:
            target = world_id_or_world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.state = new_state

    def destroy_world(self, world_or_id: Optional[Union[InputWorld, str]] = None) -> None:
        if isinstance(world_or_id, str):
            target = self.worlds.get(world_or_id)
            if not target:
                raise ValueError(f"WORLD_NOT_FOUND: '{world_or_id}'")
            del self.worlds[world_or_id]
        else:
            target = world_or_id or self.active_world
            if target and target.input_world_id in self.worlds:
                del self.worlds[target.input_world_id]

        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        target.devices.clear()
        target.contexts.clear()
        target.context_stack.clear()
        target.actions.clear()
        target.axes.clear()
        target.gestures.clear()
        target.profiles.clear()
        target.raw_event_queue.clear()
        target.processed_events.clear()
        target.hotplug_history.clear()
        target.modifiers_state.clear()
        target.mouse_buttons.clear()
        target.active_touch_points.clear()
        target.state = InputWorldState.DESTROYED
        if self.active_world is target:
            self.active_world = None

    destroy_input_world = destroy_world

    def reset(self) -> None:
        self.worlds.clear()
        self.active_world = None
        self._sequence_counter = 0
        self._recording_active = False
        self._current_record = None

    # --------------------------------------------------------------------------
    # 2. Device Management & Hotplug
    # --------------------------------------------------------------------------

    def register_device(self, device: InputDevice, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.devices) >= target.settings.max_devices:
            raise ValueError("SECURITY_VIOLATION: Max input devices limit exceeded.")
        if device.device_id in target.devices:
            raise ValueError(f"DUPLICATE_DEVICE_ID: Device '{device.device_id}' already registered.")

        target.devices[device.device_id] = device
        ev = DeviceHotplugEvent(
            event_id=f"hotplug_{len(target.hotplug_history) + 1}",
            device_id=device.device_id,
            is_connected=True,
            timestamp=target.time_seconds,
        )
        target.hotplug_history.append(ev)

    def create_device(
        self,
        device_id: str,
        device_type: InputDeviceType,
        capabilities: Optional[DeviceCapabilities] = None,
        vendor_id: str = "",
        product_id: str = "",
        instance_id: int = 0,
        world: Optional[InputWorld] = None,
    ) -> InputDevice:
        dev = InputDevice(
            device_id=device_id,
            device_type=device_type,
            vendor_id=vendor_id,
            product_id=product_id,
            instance_id=instance_id,
            capabilities=capabilities or DeviceCapabilities(),
        )
        self.register_device(dev, world)
        return dev

    def disconnect_device(self, device_id: str, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        dev = target.devices[device_id]
        dev.status = InputDeviceStatus.DISCONNECTED
        dev.button_states.clear()
        dev.axis_states.clear()
        dev.rumble_left = 0.0
        dev.rumble_right = 0.0
        dev.rumble_remaining_seconds = 0.0
        ev = DeviceHotplugEvent(
            event_id=f"hotplug_{len(target.hotplug_history) + 1}",
            device_id=device_id,
            is_connected=False,
            timestamp=target.time_seconds,
        )
        target.hotplug_history.append(ev)

    def reconnect_device(self, device_id: str, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        dev = target.devices[device_id]
        dev.status = InputDeviceStatus.CONNECTED
        ev = DeviceHotplugEvent(
            event_id=f"hotplug_{len(target.hotplug_history) + 1}",
            device_id=device_id,
            is_connected=True,
            timestamp=target.time_seconds,
        )
        target.hotplug_history.append(ev)

    def get_device(self, device_id: str, world: Optional[InputWorld] = None) -> Optional[InputDevice]:
        target = world or self.active_world
        if not target:
            return None
        return target.devices.get(device_id)

    def remove_device(self, device_id: str, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        del target.devices[device_id]

    # --------------------------------------------------------------------------
    # 3. Raw Events & Queue
    # --------------------------------------------------------------------------

    def queue_raw_event(self, event: RawInputEvent, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.raw_event_queue) >= target.settings.max_buffer_size:
            raise ValueError("SECURITY_VIOLATION: Input event buffer overflow.")

        # Assign sequence if not assigned
        if event.sequence_number == 0:
            self._sequence_counter += 1
            event.sequence_number = self._sequence_counter

        target.raw_event_queue.append(event)
        if self._recording_active and self._current_record is not None:
            self._current_record.events.append(copy.deepcopy(event))

    def create_raw_event(
        self,
        device_id: str,
        event_type: RawInputEventType,
        code: str = "",
        value: float = 0.0,
        position: Optional[List[float]] = None,
        delta: Optional[List[float]] = None,
        pressure: float = 1.0,
        tilt: Optional[List[float]] = None,
        touch_id: int = 0,
        text: str = "",
        modifiers: Optional[List[str]] = None,
        timestamp: Optional[float] = None,
        world: Optional[InputWorld] = None,
    ) -> RawInputEvent:
        target = world or self.active_world
        self._sequence_counter += 1
        t = target.time_seconds if (target and timestamp is None) else (timestamp or 0.0)

        dev_type = InputDeviceType.KEYBOARD
        if target and device_id in target.devices:
            dev_type = target.devices[device_id].device_type

        ev = RawInputEvent(
            event_id=f"ev_{self._sequence_counter}",
            sequence_number=self._sequence_counter,
            device_id=device_id,
            device_type=dev_type,
            event_type=event_type,
            code=code,
            value=value,
            position=position or [0.0, 0.0],
            delta=delta or [0.0, 0.0],
            pressure=pressure,
            tilt=tilt or [0.0, 0.0],
            touch_id=touch_id,
            text=text,
            modifiers=modifiers or [],
            timestamp=t,
        )
        self.queue_raw_event(ev, target)
        return ev

    # --------------------------------------------------------------------------
    # 4. Normalization, Processing & State Evaluation
    # --------------------------------------------------------------------------

    def process_events(self, world: Optional[InputWorld] = None) -> int:
        target = world or self.active_world
        if not target:
            return 0

        # Sort events deterministically by timestamp, then sequence_number
        events = sorted(target.raw_event_queue, key=lambda e: (e.timestamp, e.sequence_number))
        count = len(events)

        # Flood protection per frame
        if count > target.settings.max_events_per_frame:
            events = events[:target.settings.max_events_per_frame]

        for ev in events:
            dev = target.devices.get(ev.device_id)
            if not dev or dev.status != InputDeviceStatus.CONNECTED:
                continue

            # Update hardware state
            if ev.event_type == RawInputEventType.KEY_DOWN:
                dev.button_states[ev.code] = True
                if ev.code in ("ShiftLeft", "ShiftRight", "Shift"):
                    target.modifiers_state.add("SHIFT")
                elif ev.code in ("ControlLeft", "ControlRight", "Ctrl", "Control"):
                    target.modifiers_state.add("CONTROL")
                elif ev.code in ("AltLeft", "AltRight", "Alt"):
                    target.modifiers_state.add("ALT")
                elif ev.code in ("MetaLeft", "MetaRight", "Meta"):
                    target.modifiers_state.add("META")

            elif ev.event_type == RawInputEventType.KEY_UP:
                dev.button_states[ev.code] = False
                if ev.code in ("ShiftLeft", "ShiftRight", "Shift"):
                    target.modifiers_state.discard("SHIFT")
                elif ev.code in ("ControlLeft", "ControlRight", "Ctrl", "Control"):
                    target.modifiers_state.discard("CONTROL")
                elif ev.code in ("AltLeft", "AltRight", "Alt"):
                    target.modifiers_state.discard("ALT")
                elif ev.code in ("MetaLeft", "MetaRight", "Meta"):
                    target.modifiers_state.discard("META")

            elif ev.event_type == RawInputEventType.MOUSE_MOVE:
                target.mouse_position = list(ev.position)
                target.mouse_delta = list(ev.delta)

            elif ev.event_type == RawInputEventType.MOUSE_DOWN:
                target.mouse_buttons[ev.code] = True
                dev.button_states[ev.code] = True

            elif ev.event_type == RawInputEventType.MOUSE_UP:
                target.mouse_buttons[ev.code] = False
                dev.button_states[ev.code] = False

            elif ev.event_type == RawInputEventType.GAMEPAD_BUTTON_DOWN:
                dev.button_states[ev.code] = True

            elif ev.event_type == RawInputEventType.GAMEPAD_BUTTON_UP:
                dev.button_states[ev.code] = False

            elif ev.event_type == RawInputEventType.GAMEPAD_AXIS:
                dev.axis_states[ev.code] = ev.value

            elif ev.event_type == RawInputEventType.TOUCH_START:
                if len(target.active_touch_points) >= target.settings.max_devices:
                    raise ValueError("SECURITY_VIOLATION: Max touch points limit exceeded.")
                target.active_touch_points[ev.touch_id] = list(ev.position)

            elif ev.event_type == RawInputEventType.TOUCH_MOVE:
                target.active_touch_points[ev.touch_id] = list(ev.position)

            elif ev.event_type in (RawInputEventType.TOUCH_END, RawInputEventType.TOUCH_CANCEL):
                if ev.touch_id in target.active_touch_points:
                    del target.active_touch_points[ev.touch_id]

            elif ev.event_type == RawInputEventType.PEN_MOVE:
                target.pen_position = list(ev.position)
                target.pen_pressure = ev.pressure
                target.pen_tilt = list(ev.tilt)

            elif ev.event_type == RawInputEventType.PEN_DOWN:
                target.pen_position = list(ev.position)
                target.pen_pressure = ev.pressure
                dev.button_states[ev.code or "Tip"] = True

            elif ev.event_type == RawInputEventType.PEN_UP:
                target.pen_pressure = 0.0
                dev.button_states[ev.code or "Tip"] = False

            elif ev.event_type == RawInputEventType.TEXT_INPUT:
                target.text_buffer += ev.text

            # Evaluate context stack and action/axis mappings
            self._evaluate_actions_and_axes(ev, target)

            target.processed_events.append(ev)

        target.raw_event_queue.clear()
        return count

    def _evaluate_actions_and_axes(self, event: RawInputEvent, world: InputWorld) -> None:
        active_contexts = self.get_active_contexts(world)

        # Evaluate Actions
        for act in world.actions.values():
            # Check if allowed by context
            in_context = not active_contexts or any(act.action_id in ctx.action_ids for ctx in active_contexts)
            if not in_context:
                continue

            for b in act.bindings:
                if b.code == event.code and b.device_type == event.device_type:
                    # Check modifiers
                    mod_match = all(m in world.modifiers_state for m in b.modifiers)
                    if mod_match:
                        if event.event_type in (
                            RawInputEventType.KEY_DOWN,
                            RawInputEventType.MOUSE_DOWN,
                            RawInputEventType.GAMEPAD_BUTTON_DOWN,
                        ):
                            act.is_pressed = True
                            act.value = 1.0
                            act.state = ActionTriggerState.TRIGGERED
                            if act.consume:
                                event.consumed = True
                        elif event.event_type in (
                            RawInputEventType.KEY_UP,
                            RawInputEventType.MOUSE_UP,
                            RawInputEventType.GAMEPAD_BUTTON_UP,
                        ):
                            act.is_pressed = False
                            act.value = 0.0
                            act.state = ActionTriggerState.COMPLETED

        # Evaluate Axes
        for ax in world.axes.values():
            in_context = not active_contexts or any(ax.axis_id in ctx.axis_ids for ctx in active_contexts)
            if not in_context:
                continue

            for b in ax.bindings:
                if b.code == event.code and b.device_type == event.device_type:
                    val = event.value
                    # Apply dead zone
                    dz_val = self.apply_dead_zone(val, b.dead_zone, b.dead_zone_mode)
                    # Apply curve & sensitivity
                    c_val = self.apply_axis_curve(dz_val, b.curve, b.sensitivity)
                    final_val = c_val * b.scale * (-1.0 if b.invert else 1.0)
                    ax.raw_value = val
                    ax.value = max(-1.0, min(1.0, final_val))

            # Check composite digital axes (e.g. W/S or A/D)
            if ax.composite_positive or ax.composite_negative:
                pos_active = any(dev.button_states.get(ax.composite_positive, False) for dev in world.devices.values())
                neg_active = any(dev.button_states.get(ax.composite_negative, False) for dev in world.devices.values())
                v = 0.0
                if pos_active:
                    v += 1.0
                if neg_active:
                    v -= 1.0
                ax.value = max(-1.0, min(1.0, v))

    # --------------------------------------------------------------------------
    # 5. Keyboard & Modifiers
    # --------------------------------------------------------------------------

    def is_key_pressed(self, key_code: str, world: Optional[InputWorld] = None) -> bool:
        target = world or self.active_world
        if not target:
            return False
        return any(dev.button_states.get(key_code, False) for dev in target.devices.values())

    def is_modifier_active(self, modifier: str, world: Optional[InputWorld] = None) -> bool:
        target = world or self.active_world
        if not target:
            return False
        return modifier.upper() in target.modifiers_state

    # --------------------------------------------------------------------------
    # 6. Mouse & Coordinate Transforms
    # --------------------------------------------------------------------------

    def set_mouse_position(self, x: float, y: float, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.mouse_delta = [x - target.mouse_position[0], y - target.mouse_position[1]]
        target.mouse_position = [x, y]

    def set_mouse_captured(self, captured: bool, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.mouse_captured = captured

    def transform_screen_to_normalized(self, pos: List[float], screen_width: float, screen_height: float) -> List[float]:
        if screen_width <= 0.0 or screen_height <= 0.0:
            raise ValueError("INVALID_SCREEN_DIMENSIONS: Screen width and height must be > 0.")
        nx = max(0.0, min(1.0, pos[0] / screen_width))
        ny = max(0.0, min(1.0, pos[1] / screen_height))
        return [round(nx, 6), round(ny, 6)]

    def transform_normalized_to_screen(self, pos: List[float], screen_width: float, screen_height: float) -> List[float]:
        if screen_width <= 0.0 or screen_height <= 0.0:
            raise ValueError("INVALID_SCREEN_DIMENSIONS: Screen width and height must be > 0.")
        sx = pos[0] * screen_width
        sy = pos[1] * screen_height
        return [round(sx, 6), round(sy, 6)]

    # --------------------------------------------------------------------------
    # 7. Gamepad, Dead-Zones, Curves & Rumble
    # --------------------------------------------------------------------------

    def apply_dead_zone(self, value: float, dead_zone: float, mode: DeadZoneMode = DeadZoneMode.AXIAL) -> float:
        if dead_zone < 0.0 or dead_zone >= 1.0:
            raise ValueError(f"INVALID_DEAD_ZONE: dead_zone must be in [0, 1) ({dead_zone}).")
        mag = abs(value)
        if mag <= dead_zone:
            return 0.0
        # Linear rescaling outside dead-zone
        sign = 1.0 if value >= 0.0 else -1.0
        rescaled = sign * (mag - dead_zone) / (1.0 - dead_zone)
        return max(-1.0, min(1.0, rescaled))

    def apply_axis_curve(self, value: float, curve: AxisCurveType, sensitivity: float = 1.0) -> float:
        if sensitivity < 0.0:
            raise ValueError(f"INVALID_SENSITIVITY: Sensitivity cannot be negative ({sensitivity}).")

        sign = 1.0 if value >= 0.0 else -1.0
        mag = abs(value)

        if curve == AxisCurveType.EXPONENTIAL:
            res = sign * (mag ** 2) * sensitivity
        elif curve == AxisCurveType.LOGARITHMIC:
            res = sign * math.log10(1.0 + 9.0 * mag) * sensitivity
        elif curve == AxisCurveType.SMOOTHSTEP:
            # Hermite curve 3x^2 - 2x^3
            res = sign * (3.0 * (mag ** 2) - 2.0 * (mag ** 3)) * sensitivity
        elif curve == AxisCurveType.SENSITIVITY_CURVE:
            res = sign * (mag ** 1.5) * sensitivity
        else:  # LINEAR default
            res = value * sensitivity

        return max(-1.0, min(1.0, res))

    def set_gamepad_rumble(
        self,
        device_id: str,
        left: float,
        right: float,
        duration_seconds: float = 1.0,
        world: Optional[InputWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        dev = target.devices[device_id]
        if not dev.capabilities.supports_rumble:
            return

        clamped_duration = min(duration_seconds, target.settings.rumble_timeout_seconds)
        dev.rumble_left = max(0.0, min(1.0, left))
        dev.rumble_right = max(0.0, min(1.0, right))
        dev.rumble_remaining_seconds = clamped_duration

    def stop_gamepad_rumble(self, device_id: str, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target or device_id not in target.devices:
            raise ValueError(f"DEVICE_NOT_FOUND: '{device_id}'")
        dev = target.devices[device_id]
        dev.rumble_left = 0.0
        dev.rumble_right = 0.0
        dev.rumble_remaining_seconds = 0.0

    # --------------------------------------------------------------------------
    # 8. Touch & Pen
    # --------------------------------------------------------------------------

    def get_active_touch_count(self, world: Optional[InputWorld] = None) -> int:
        target = world or self.active_world
        return len(target.active_touch_points) if target else 0

    def get_touch_position(self, touch_id: int, world: Optional[InputWorld] = None) -> Optional[List[float]]:
        target = world or self.active_world
        return target.active_touch_points.get(touch_id) if target else None

    def get_pen_state(self, world: Optional[InputWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}
        return {
            "position": list(target.pen_position),
            "pressure": target.pen_pressure,
            "tilt": list(target.pen_tilt),
            "barrel_button": target.pen_barrel_button,
        }

    # --------------------------------------------------------------------------
    # 9. Text Input
    # --------------------------------------------------------------------------

    def get_text_buffer(self, world: Optional[InputWorld] = None) -> str:
        target = world or self.active_world
        return target.text_buffer if target else ""

    def clear_text_buffer(self, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if target:
            target.text_buffer = ""

    # --------------------------------------------------------------------------
    # 10. Actions & Axes
    # --------------------------------------------------------------------------

    def register_action(self, action: InputAction, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.actions) >= target.settings.max_actions:
            raise ValueError("SECURITY_VIOLATION: Max actions limit exceeded.")
        if action.action_id in target.actions:
            raise ValueError(f"DUPLICATE_ACTION_ID: Action '{action.action_id}' already registered.")
        target.actions[action.action_id] = action

    def create_action(
        self,
        action_id: str,
        priority: int = 100,
        consume: bool = True,
        world: Optional[InputWorld] = None,
    ) -> InputAction:
        act = InputAction(action_id=action_id, priority=priority, consume=consume)
        self.register_action(act, world)
        return act

    def bind_action(
        self,
        action_id: str,
        device_type: InputDeviceType,
        code: str,
        modifiers: Optional[List[str]] = None,
        chords: Optional[List[str]] = None,
        hold_time: float = 0.0,
        world: Optional[InputWorld] = None,
    ) -> ActionBinding:
        target = world or self.active_world
        if not target or action_id not in target.actions:
            raise ValueError(f"ACTION_NOT_FOUND: '{action_id}'")
        binding_id = f"bind_{action_id}_{len(target.actions[action_id].bindings) + 1}"
        binding = ActionBinding(
            binding_id=binding_id,
            device_type=device_type,
            code=code,
            modifiers=modifiers or [],
            chords=chords or [],
            hold_time=hold_time,
        )
        target.actions[action_id].bindings.append(binding)
        return binding

    def is_action_triggered(self, action_id: str, world: Optional[InputWorld] = None) -> bool:
        target = world or self.active_world
        if not target or action_id not in target.actions:
            return False
        return target.actions[action_id].is_pressed

    def register_axis(self, axis: InputAxis, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.axes) >= target.settings.max_axes:
            raise ValueError("SECURITY_VIOLATION: Max axes limit exceeded.")
        if axis.axis_id in target.axes:
            raise ValueError(f"DUPLICATE_AXIS_ID: Axis '{axis.axis_id}' already registered.")
        target.axes[axis.axis_id] = axis

    def create_axis(self, axis_id: str, world: Optional[InputWorld] = None) -> InputAxis:
        ax = InputAxis(axis_id=axis_id)
        self.register_axis(ax, world)
        return ax

    def bind_axis(
        self,
        axis_id: str,
        device_type: InputDeviceType,
        code: str,
        scale: float = 1.0,
        dead_zone: float = 0.1,
        dead_zone_mode: DeadZoneMode = DeadZoneMode.AXIAL,
        sensitivity: float = 1.0,
        curve: AxisCurveType = AxisCurveType.LINEAR,
        invert: bool = False,
        world: Optional[InputWorld] = None,
    ) -> AxisBinding:
        target = world or self.active_world
        if not target or axis_id not in target.axes:
            raise ValueError(f"AXIS_NOT_FOUND: '{axis_id}'")
        binding_id = f"bind_ax_{axis_id}_{len(target.axes[axis_id].bindings) + 1}"
        binding = AxisBinding(
            binding_id=binding_id,
            device_type=device_type,
            code=code,
            scale=scale,
            dead_zone=dead_zone,
            dead_zone_mode=dead_zone_mode,
            sensitivity=sensitivity,
            curve=curve,
            invert=invert,
        )
        target.axes[axis_id].bindings.append(binding)
        return binding

    def bind_composite_axis(
        self,
        axis_id: str,
        positive_key: str,
        negative_key: str,
        scale: float = 1.0,
        world: Optional[InputWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target or axis_id not in target.axes:
            raise ValueError(f"AXIS_NOT_FOUND: '{axis_id}'")
        ax = target.axes[axis_id]
        ax.composite_positive = positive_key
        ax.composite_negative = negative_key

    def get_axis_value(self, axis_id: str, world: Optional[InputWorld] = None) -> float:
        target = world or self.active_world
        if not target or axis_id not in target.axes:
            return 0.0
        return target.axes[axis_id].value

    # --------------------------------------------------------------------------
    # 11. Context Stack, Priority & Routing
    # --------------------------------------------------------------------------

    def register_context(self, context: InputContext, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if len(target.contexts) >= target.settings.max_contexts:
            raise ValueError("SECURITY_VIOLATION: Max contexts limit exceeded.")
        if context.context_id in target.contexts:
            raise ValueError(f"DUPLICATE_CONTEXT_ID: Context '{context.context_id}' already exists.")
        target.contexts[context.context_id] = context

    def create_context(
        self,
        context_id: str,
        priority: int = 0,
        routing_mode: InputRoutingMode = InputRoutingMode.ROUTE_ALL,
        consume_unhandled: bool = False,
        world: Optional[InputWorld] = None,
    ) -> InputContext:
        ctx = InputContext(
            context_id=context_id,
            priority=priority,
            routing_mode=routing_mode,
            consume_unhandled=consume_unhandled,
        )
        self.register_context(ctx, world)
        return ctx

    def push_context(self, context_id: str, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target or context_id not in target.contexts:
            raise ValueError(f"CONTEXT_NOT_FOUND: '{context_id}'")
        if context_id not in target.context_stack:
            target.context_stack.append(context_id)

    def pop_context(self, context_id: Optional[str] = None, world: Optional[InputWorld] = None) -> Optional[str]:
        target = world or self.active_world
        if not target or not target.context_stack:
            return None
        if context_id is None:
            return target.context_stack.pop()
        if context_id in target.context_stack:
            target.context_stack.remove(context_id)
            return context_id
        return None

    def get_active_contexts(self, world: Optional[InputWorld] = None) -> List[InputContext]:
        target = world or self.active_world
        if not target:
            return []
        active = [target.contexts[cid] for cid in target.context_stack if cid in target.contexts and target.contexts[cid].is_active]
        return sorted(active, key=lambda c: c.priority, reverse=True)

    # --------------------------------------------------------------------------
    # 12. Gestures
    # --------------------------------------------------------------------------

    def register_gesture(self, gesture: GestureBinding, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if gesture.gesture_id in target.gestures:
            raise ValueError(f"DUPLICATE_GESTURE_ID: Gesture '{gesture.gesture_id}' already registered.")
        target.gestures[gesture.gesture_id] = gesture

    def create_gesture(
        self,
        gesture_id: str,
        gesture_type: GestureType,
        min_duration: float = 0.0,
        max_duration: float = 0.5,
        min_distance: float = 10.0,
        tap_count: int = 1,
        world: Optional[InputWorld] = None,
    ) -> GestureBinding:
        g = GestureBinding(
            gesture_id=gesture_id,
            gesture_type=gesture_type,
            min_duration=min_duration,
            max_duration=max_duration,
            min_distance=min_distance,
            tap_count=tap_count,
        )
        self.register_gesture(g, world)
        return g

    def get_gesture_state(self, gesture_id: str, world: Optional[InputWorld] = None) -> GestureState:
        target = world or self.active_world
        if not target or gesture_id not in target.gestures:
            return GestureState.FAILED
        return target.gestures[gesture_id].state

    # --------------------------------------------------------------------------
    # 13. Rebinding & Profiles
    # --------------------------------------------------------------------------

    def register_profile(self, profile: InputRebindingProfile, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.profiles[profile.profile_id] = profile

    def set_active_profile(self, profile_id: str, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target or profile_id not in target.profiles:
            raise ValueError(f"PROFILE_NOT_FOUND: '{profile_id}'")
        target.active_profile_id = profile_id

    def rebind_action(
        self,
        action_id: str,
        old_code: str,
        new_code: str,
        device_type: InputDeviceType,
        world: Optional[InputWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target or action_id not in target.actions:
            raise ValueError(f"ACTION_NOT_FOUND: '{action_id}'")
        act = target.actions[action_id]
        for b in act.bindings:
            if b.code == old_code and b.device_type == device_type:
                b.code = new_code
                return
        # If not found, create new binding
        self.bind_action(action_id, device_type, new_code, world=target)

    def reset_profile_to_default(self, profile_id: str, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target or profile_id not in target.profiles:
            raise ValueError(f"PROFILE_NOT_FOUND: '{profile_id}'")
        p = target.profiles[profile_id]
        p.action_overrides.clear()
        p.axis_overrides.clear()
        p.dead_zone_overrides.clear()
        p.sensitivity_overrides.clear()

    # --------------------------------------------------------------------------
    # 14. Recording, Snapshots & Replay
    # --------------------------------------------------------------------------

    def create_snapshot(self, world: Optional[InputWorld] = None) -> InputSnapshot:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        kb_state: Dict[str, bool] = {}
        for dev in target.devices.values():
            if dev.device_type == InputDeviceType.KEYBOARD:
                kb_state.update(dev.button_states)

        gp_axes: Dict[str, float] = {}
        gp_buttons: Dict[str, bool] = {}
        for dev in target.devices.values():
            if dev.device_type == InputDeviceType.GAMEPAD:
                gp_axes.update(dev.axis_states)
                gp_buttons.update(dev.button_states)

        data = {
            "kb": copy_dict_deterministic(kb_state),
            "mouse_pos": target.mouse_position,
            "mouse_btn": copy_dict_deterministic(target.mouse_buttons),
            "gp_axes": gp_axes,
            "gp_btn": copy_dict_deterministic(gp_buttons),
            "ctx": sorted(target.context_stack),
        }
        serialized = json.dumps(data, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        return InputSnapshot(
            snapshot_id=f"snap_{int(target.time_seconds * 1000)}",
            world_id=target.input_world_id,
            timestamp=target.time_seconds,
            keyboard_state=kb_state,
            mouse_position=list(target.mouse_position),
            mouse_buttons=dict(target.mouse_buttons),
            gamepad_axes=gp_axes,
            gamepad_buttons=gp_buttons,
            active_contexts=list(target.context_stack),
            snapshot_hash=h,
        )

    capture_snapshot = create_snapshot

    def start_recording(self, record_id: str, world: Optional[InputWorld] = None) -> InputRecord:
        target = world or self.active_world
        t = target.time_seconds if target else 0.0
        rec = InputRecord(record_id=record_id, start_timestamp=t)
        self._current_record = rec
        self._recording_active = True
        return rec

    def stop_recording(self, world: Optional[InputWorld] = None) -> Optional[InputRecord]:
        if not self._recording_active or not self._current_record:
            return None
        rec = self._current_record
        target = world or self.active_world
        rec.duration_seconds = (target.time_seconds if target else 0.0) - rec.start_timestamp
        rec.frame_count = target.frames_rendered if target else 0

        # Compute hash
        serialized = json.dumps([e.to_dict() for e in rec.events], sort_keys=True)
        rec.record_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        self._recording_active = False
        self._current_record = None
        return rec

    def execute_replay(self, session: InputReplaySession, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        # Validate hash if present
        if session.record.record_hash:
            serialized = json.dumps([e.to_dict() for e in session.record.events], sort_keys=True)
            if hashlib.sha256(serialized.encode("utf-8")).hexdigest() != session.record.record_hash:
                session.is_valid = False
                raise ValueError("REPLAY_VALIDATION_FAILED: Record hash mismatch.")

        for ev in session.record.events:
            try:
                self.queue_raw_event(copy.deepcopy(ev), target)
            except ValueError:
                # Discard invalid/tampered event safely
                pass
        self.process_events(target)
        session.is_finished = True

    def capture_golden_input(self, world: Optional[InputWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        data = {
            "world_id": target.input_world_id,
            "devices_count": len(target.devices),
            "contexts_count": len(target.contexts),
            "actions_count": len(target.actions),
            "axes_count": len(target.axes),
            "mouse_position": target.mouse_position,
            "processed_events_count": len(target.processed_events),
        }
        serialized = json.dumps(data, sort_keys=True)
        data["golden_hash"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return data

    # --------------------------------------------------------------------------
    # 15. Simulation Update Step
    # --------------------------------------------------------------------------

    def update(self, delta_time: float, world: Optional[InputWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state == InputWorldState.PAUSED:
            return
        if target.state not in (InputWorldState.RUNNING, InputWorldState.READY):
            raise ValueError(f"NO_UPDATE_BEFORE_INITIALIZATION: InputWorld state is '{target.state.value}'.")
        if delta_time < 0.0:
            raise ValueError("INVALID_TIMESTEP: delta_time cannot be negative.")

        target.time_seconds += delta_time
        target.frames_rendered += 1

        # Process any pending raw events
        if target.raw_event_queue:
            self.process_events(target)

        # Update rumble timers
        for dev in target.devices.values():
            if dev.rumble_remaining_seconds > 0.0:
                dev.rumble_remaining_seconds = max(0.0, dev.rumble_remaining_seconds - delta_time)
                if dev.rumble_remaining_seconds <= 0.0:
                    dev.rumble_left = 0.0
                    dev.rumble_right = 0.0

        # Update gesture elapsed timers
        for g in target.gestures.values():
            if g.state in (GestureState.BEGAN, GestureState.CHANGED):
                g.elapsed_time += delta_time
                if g.elapsed_time > g.max_duration:
                    g.state = GestureState.FAILED

        target.content_fingerprint = target.compute_fingerprint()

    # --------------------------------------------------------------------------
    # 16. Debug Input Data
    # --------------------------------------------------------------------------

    def get_debug_input_data(self, world: Optional[InputWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        return {
            "world_id": target.input_world_id,
            "state": target.state.value,
            "devices": {k: d.status.value for k, d in target.devices.items()},
            "active_contexts": list(target.context_stack),
            "triggered_actions": [a for a, act in target.actions.items() if act.is_pressed],
            "axis_values": {a: ax.value for a, ax in target.axes.items()},
            "mouse_position": target.mouse_position,
            "modifiers": sorted(list(target.modifiers_state)),
        }
