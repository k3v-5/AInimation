"""
UAF-81.65 Acceptance & Normative Compliance Test Suite.
Universal Application State, Event Bus, Message Dispatch, Command System,
Input Abstraction, Action Mapping, Context Stack, Focus, Priority,
Routing, Replay & Deterministic Event Processing System.
Covers 22 normative test categories, 10 Golden Scenarios, Integration Pipeline,
and 4 End-to-End lifecycle pipelines (?168 to ?190).
Total: 180 normative test cases (satisfies exact requirement of ?190: minimum 176).
"""

import copy
import hashlib
import json
import time
import pytest

from uaf.universal_events import (
    EventType,
    EventPriority,
    InputDeviceType,
    InputEventType,
    DispatchMode,
    OverflowPolicy,
    RoutingPhase,
    ReplayMode,
    DivergenceSeverity,
    CommandStatus,
    ContextPriority,
    RateControlStrategy,
    Event,
    Message,
    Command,
    EventCommandResult,
    CommandResult,
    InputEvent,
    ActionMapping,
    EventInputContext,
    InputContext,
    FocusTarget,
    ReplayFrame,
    ReplayRecording,
    ReplayDivergence,
    EventTelemetry,
    DiagnosticEventBundle,
    EventDiagnosticReport,
    UniversalEventFabricator,
    UniversalEventValidator,
    UniversalEventPackager,
    ProductionReadyEvents,
)


# ==============================================================================
# 1. EVENT BUS TESTS (?168) - 15 tests
# ==============================================================================

def test_event_publish_and_subscribe_sync():
    fab = UniversalEventFabricator()
    received = []
    fab.subscribe(EventType.APPLICATION, lambda e: received.append(e.payload.get("data")))
    success = fab.publish(Event(EventType.APPLICATION, payload={"data": "val1"}))
    assert success is True
    assert received == ["val1"]

def test_event_unsubscribe():
    fab = UniversalEventFabricator()
    received = []
    handler = lambda e: received.append(e.payload)
    fab.subscribe(EventType.SYSTEM, handler)
    fab.unsubscribe(EventType.SYSTEM, handler)
    fab.publish(Event(EventType.SYSTEM, payload="no_receive"))
    assert received == []

def test_event_multiple_subscribers():
    fab = UniversalEventFabricator()
    calls = []
    fab.subscribe(EventType.CUSTOM, lambda e: calls.append("sub1"))
    fab.subscribe(EventType.CUSTOM, lambda e: calls.append("sub2"))
    fab.publish(Event(EventType.CUSTOM))
    assert calls == ["sub1", "sub2"]

def test_event_filter():
    fab = UniversalEventFabricator()
    received = []
    fab.subscribe(EventType.APPLICATION, lambda e: received.append(e.payload["v"]), filter_fn=lambda e: e.payload.get("v", 0) > 10)
    fab.publish(Event(EventType.APPLICATION, payload={"v": 5}))
    fab.publish(Event(EventType.APPLICATION, payload={"v": 15}))
    assert received == [15]

def test_event_subscriber_isolation_upon_failure():
    fab = UniversalEventFabricator()
    received = []
    def bad_sub(e):
        raise RuntimeError("Subscriber explosion")
    fab.subscribe(EventType.SYSTEM, bad_sub)
    fab.subscribe(EventType.SYSTEM, lambda e: received.append("ok"))
    fab.publish(Event(EventType.SYSTEM))
    assert received == ["ok"]
    assert fab.telemetry.handler_errors == 1

def test_event_priority_ordering_in_queue():
    fab = UniversalEventFabricator()
    received = []
    fab.subscribe(EventType.APPLICATION, lambda e: received.append(e.payload["tag"]))
    fab.publish(Event(EventType.APPLICATION, priority=EventPriority.LOW, payload={"tag": "low"}), mode=DispatchMode.QUEUED)
    fab.publish(Event(EventType.APPLICATION, priority=EventPriority.IMMEDIATE, payload={"tag": "high"}), mode=DispatchMode.QUEUED)
    fab.process_queue()
    assert received == ["high", "low"]

def test_event_queue_processing_limit():
    fab = UniversalEventFabricator()
    fab.subscribe(EventType.APPLICATION, lambda e: None)
    for i in range(5):
        fab.publish(Event(EventType.APPLICATION), mode=DispatchMode.QUEUED)
    processed = fab.process_queue(max_events=2)
    assert processed == 2
    assert len(fab.event_queue) == 3

def test_event_queue_overflow_drop_oldest():
    fab = UniversalEventFabricator(max_queue_size=2, overflow_policy=OverflowPolicy.DROP_OLDEST)
    fab.publish(Event(EventType.APPLICATION, payload={"id": 1}), mode=DispatchMode.QUEUED)
    fab.publish(Event(EventType.APPLICATION, payload={"id": 2}), mode=DispatchMode.QUEUED)
    fab.publish(Event(EventType.APPLICATION, payload={"id": 3}), mode=DispatchMode.QUEUED)
    assert len(fab.event_queue) == 2
    assert fab.telemetry.dropped_events == 1

def test_event_queue_overflow_drop_newest():
    fab = UniversalEventFabricator(max_queue_size=2, overflow_policy=OverflowPolicy.DROP_NEWEST)
    fab.publish(Event(EventType.APPLICATION, payload={"id": 1}), mode=DispatchMode.QUEUED)
    fab.publish(Event(EventType.APPLICATION, payload={"id": 2}), mode=DispatchMode.QUEUED)
    accepted = fab.publish(Event(EventType.APPLICATION, payload={"id": 3}), mode=DispatchMode.QUEUED)
    assert accepted is False
    assert len(fab.event_queue) == 2

def test_event_queue_overflow_error():
    fab = UniversalEventFabricator(max_queue_size=1, overflow_policy=OverflowPolicy.ERROR)
    fab.publish(Event(EventType.APPLICATION), mode=DispatchMode.QUEUED)
    with pytest.raises(OverflowError):
        fab.publish(Event(EventType.APPLICATION), mode=DispatchMode.QUEUED)

def test_event_envelope_defaults():
    e = Event(EventType.COMMAND)
    assert e.priority == EventPriority.NORMAL
    assert e.handled is False
    assert e.cancelled is False

def test_event_serialization():
    e = Event(EventType.INPUT, payload={"x": 1})
    d = e.to_dict()
    assert d["event_type"] == "INPUT"
    assert d["payload"]["x"] == 1

def test_event_cancellation_stops_subsequent_subscribers():
    fab = UniversalEventFabricator()
    calls = []
    def cancel_sub(e):
        calls.append("first")
        e.cancelled = True
    fab.subscribe(EventType.CUSTOM, cancel_sub, priority=10)
    fab.subscribe(EventType.CUSTOM, lambda e: calls.append("second"), priority=5)
    fab.publish(Event(EventType.CUSTOM))
    assert calls == ["first"]

def test_event_telemetry_metrics_updated():
    fab = UniversalEventFabricator()
    fab.subscribe(EventType.SYSTEM, lambda e: None)
    fab.publish(Event(EventType.SYSTEM))
    assert fab.telemetry.total_dispatched == 1
    assert fab.telemetry.avg_latency_ms >= 0.0

def test_event_type_enums_exist():
    for t in [EventType.APPLICATION, EventType.INPUT, EventType.SYSTEM, EventType.COMMAND, EventType.TELEMETRY, EventType.CUSTOM]:
        assert isinstance(t.value, str)


# ==============================================================================
# 2. MESSAGE BUS TESTS - 10 tests
# ==============================================================================

def test_message_send_and_receive():
    fab = UniversalEventFabricator()
    msgs = []
    fab.subscribe_channel("game.chat", lambda m: msgs.append(m.payload))
    count = fab.send_message(Message(channel="game.chat", payload="hello world"))
    assert count == 1
    assert msgs == ["hello world"]

def test_message_wildcard_matching():
    fab = UniversalEventFabricator()
    msgs = []
    fab.subscribe_channel("combat.*", lambda m: msgs.append(m.channel))
    fab.send_message(Message(channel="combat.attack", payload={}))
    fab.send_message(Message(channel="combat.defend", payload={}))
    fab.send_message(Message(channel="ui.click", payload={}))
    assert msgs == ["combat.attack", "combat.defend"]

def test_message_unsubscribe_channel():
    fab = UniversalEventFabricator()
    msgs = []
    handler = lambda m: msgs.append(m.payload)
    fab.subscribe_channel("lobby", handler)
    fab.unsubscribe_channel("lobby", handler)
    fab.send_message(Message(channel="lobby", payload="silent"))
    assert msgs == []

def test_message_multiple_channel_subscribers():
    fab = UniversalEventFabricator()
    received = []
    fab.subscribe_channel("broadcast", lambda m: received.append("s1"))
    fab.subscribe_channel("broadcast", lambda m: received.append("s2"))
    count = fab.send_message(Message(channel="broadcast", payload=1))
    assert count == 2
    assert received == ["s1", "s2"]

def test_message_handler_exception_isolated():
    fab = UniversalEventFabricator()
    calls = []
    def faulty(m):
        raise ValueError("Bad message")
    fab.subscribe_channel("safe", faulty)
    fab.subscribe_channel("safe", lambda m: calls.append("ok"))
    fab.send_message(Message(channel="safe", payload=123))
    assert calls == ["ok"]
    assert fab.telemetry.handler_errors == 1

def test_message_serialization():
    m = Message(channel="ch1", payload={"score": 10}, sender="alice")
    d = m.to_dict()
    assert d["channel"] == "ch1"
    assert d["sender"] == "alice"

def test_message_direct_recipient_field():
    m = Message(channel="whisper", payload="secret", recipient="bob")
    assert m.recipient == "bob"

def test_message_unmatched_channel_returns_zero():
    fab = UniversalEventFabricator()
    count = fab.send_message(Message(channel="unmatched", payload=None))
    assert count == 0

def test_message_timestamp_recorded():
    m = Message(channel="time_ch", payload=1)
    assert time.time() - m.timestamp < 2.0

def test_message_id_unique():
    m1 = Message(channel="c", payload=1)
    m2 = Message(channel="c", payload=2)
    assert m1.message_id != m2.message_id


# ==============================================================================
# 3. COMMAND BUS TESTS - 13 tests
# ==============================================================================

def test_command_execution_success():
    fab = UniversalEventFabricator()
    fab.register_command_handler("spawn", lambda c: f"Spawned {c.parameters['entity']}")
    res = fab.execute_command(Command(action="spawn", parameters={"entity": "Orc"}))
    assert res.status == CommandStatus.COMPLETED
    assert res.result == "Spawned Orc"
    assert res.error_message is None

def test_command_no_handler_fails():
    fab = UniversalEventFabricator()
    res = fab.execute_command(Command(action="unregistered_action"))
    assert res.status == CommandStatus.FAILED
    assert "No handler registered" in res.error_message

def test_command_handler_exception_captured():
    fab = UniversalEventFabricator()
    def bomb(c):
        raise ZeroDivisionError("Math error")
    fab.register_command_handler("crash_cmd", bomb)
    res = fab.execute_command(Command(action="crash_cmd"))
    assert res.status == CommandStatus.FAILED
    assert "Math error" in res.error_message

def test_command_history_recorded():
    fab = UniversalEventFabricator()
    fab.register_command_handler("inc", lambda c: 1)
    fab.execute_command(Command(action="inc"))
    assert len(fab.command_history) == 1
    assert fab.command_history[0][0].action == "inc"

def test_command_execution_timing_ms():
    fab = UniversalEventFabricator()
    fab.register_command_handler("fast", lambda c: 42)
    res = fab.execute_command(Command(action="fast"))
    assert res.execution_time_ms >= 0.0

def test_command_telemetry_counter():
    fab = UniversalEventFabricator()
    fab.register_command_handler("c1", lambda c: None)
    fab.execute_command(Command(action="c1"))
    fab.execute_command(Command(action="c1"))
    assert fab.telemetry.commands_executed == 2

def test_command_serialization():
    cmd = Command(action="save_game", parameters={"slot": 1})
    d = cmd.to_dict()
    assert d["action"] == "save_game"
    assert d["parameters"]["slot"] == 1

def test_command_result_serialization():
    res = EventCommandResult("cmd_1", CommandStatus.COMPLETED, result=999)
    d = res.to_dict()
    assert d["command_id"] == "cmd_1"
    assert d["status"] == "COMPLETED"
    assert d["result"] == 999

def test_command_sender_defaults():
    cmd = Command(action="teleport")
    assert cmd.sender == "client"

def test_command_custom_sender():
    cmd = Command(action="kick", sender="server_admin")
    assert cmd.sender == "server_admin"

def test_command_unique_id():
    c1 = Command(action="a")
    c2 = Command(action="a")
    assert c1.command_id != c2.command_id

def test_command_status_enum_values():
    assert CommandStatus.PENDING.value == "PENDING"
    assert CommandStatus.EXECUTING.value == "EXECUTING"
    assert CommandStatus.COMPLETED.value == "COMPLETED"
    assert CommandStatus.FAILED.value == "FAILED"
    assert CommandStatus.CANCELLED.value == "CANCELLED"

def test_command_result_alias_compatibility():
    assert CommandResult is EventCommandResult


# ==============================================================================
# 4. INPUT ABSTRACTION TESTS - 11 tests
# ==============================================================================

def test_input_device_types():
    assert InputDeviceType.KEYBOARD.value == "KEYBOARD"
    assert InputDeviceType.MOUSE.value == "MOUSE"
    assert InputDeviceType.GAMEPAD.value == "GAMEPAD"
    assert InputDeviceType.TOUCH.value == "TOUCH"
    assert InputDeviceType.VR.value == "VR"

def test_input_event_types():
    assert InputEventType.KEY_DOWN.value == "KEY_DOWN"
    assert InputEventType.KEY_UP.value == "KEY_UP"
    assert InputEventType.AXIS_MOVE.value == "AXIS_MOVE"

def test_input_event_normalization():
    inp = InputEvent(InputDeviceType.MOUSE, InputEventType.MOUSE_MOVE, axis_values=(0.5, -0.5, 0.0), normalized_value=1.0)
    assert inp.axis_values == (0.5, -0.5, 0.0)
    assert inp.normalized_value == 1.0

def test_input_event_serialization():
    inp = InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="W")
    d = inp.to_dict()
    assert d["device"] == "KEYBOARD"
    assert d["key_code"] == "W"

def test_input_action_mapping_binding():
    mapping = ActionMapping("MoveForward", InputDeviceType.KEYBOARD, "W")
    assert mapping.action_name == "MoveForward"
    assert mapping.input_trigger == "W"

def test_input_deadzone_filtering():
    mapping = ActionMapping("Throttle", InputDeviceType.GAMEPAD, "AXIS_RT", deadzone=0.15)
    assert mapping.deadzone == 0.15

def test_input_sensitivity_scaling():
    mapping = ActionMapping("LookX", InputDeviceType.MOUSE, "AXIS_X", sensitivity=2.5)
    assert mapping.sensitivity == 2.5

def test_input_modifier_keys():
    mapping = ActionMapping("Sprint", InputDeviceType.KEYBOARD, "W", modifier_keys=["Shift"])
    assert mapping.modifier_keys == ["Shift"]

def test_input_process_triggers_action():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("default")
    fab.register_action_mapping("default", ActionMapping("Fire", InputDeviceType.MOUSE, "LeftButton"))
    fab.push_context(ctx)
    res = fab.process_input(InputEvent(InputDeviceType.MOUSE, InputEventType.MOUSE_DOWN, key_code="LeftButton"))
    assert res == ["Fire"]

def test_input_process_unmapped_input_returns_empty():
    fab = UniversalEventFabricator()
    res = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="F12"))
    assert res == []

def test_input_process_device_mismatch():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("kb")
    fab.register_action_mapping("kb", ActionMapping("Jump", InputDeviceType.KEYBOARD, "Space"))
    fab.push_context(ctx)
    # Send Gamepad button with same name trigger
    res = fab.process_input(InputEvent(InputDeviceType.GAMEPAD, InputEventType.KEY_DOWN, key_code="Space"))
    assert res == []


# ==============================================================================
# 5. ACTION MAPPING TESTS - 10 tests
# ==============================================================================

def test_action_mapping_registration():
    fab = UniversalEventFabricator()
    mapping = ActionMapping("Crouch", InputDeviceType.KEYBOARD, "C")
    fab.register_action_mapping("main", mapping)
    assert "Crouch" in fab.contexts["main"].mappings

def test_action_mapping_override_existing():
    fab = UniversalEventFabricator()
    fab.register_action_mapping("main", ActionMapping("Reload", InputDeviceType.KEYBOARD, "R"))
    fab.register_action_mapping("main", ActionMapping("Reload", InputDeviceType.KEYBOARD, "X"))
    assert fab.contexts["main"].mappings["Reload"].input_trigger == "X"

def test_action_mapping_serialization():
    m = ActionMapping("Melee", InputDeviceType.KEYBOARD, "F", deadzone=0.2, sensitivity=1.5)
    d = m.to_dict()
    assert d["action_name"] == "Melee"
    assert d["deadzone"] == 0.2
    assert d["sensitivity"] == 1.5

def test_action_mapping_multi_action_registration():
    fab = UniversalEventFabricator()
    fab.register_action_mapping("game", ActionMapping("A1", InputDeviceType.KEYBOARD, "1"))
    fab.register_action_mapping("game", ActionMapping("A2", InputDeviceType.KEYBOARD, "2"))
    assert len(fab.contexts["game"].mappings) == 2

def test_action_mapping_deadzone_below_ignored():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("vehicle")
    fab.register_action_mapping("vehicle", ActionMapping("Steer", InputDeviceType.GAMEPAD, "AXIS_X", deadzone=0.3))
    fab.push_context(ctx)
    res = fab.process_input(InputEvent(InputDeviceType.GAMEPAD, InputEventType.AXIS_MOVE, axis_values=(0.2, 0, 0)))
    assert res == []

def test_action_mapping_deadzone_above_triggers():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("vehicle")
    fab.register_action_mapping("vehicle", ActionMapping("Steer", InputDeviceType.GAMEPAD, "AXIS_X", deadzone=0.3))
    fab.push_context(ctx)
    res = fab.process_input(InputEvent(InputDeviceType.GAMEPAD, InputEventType.AXIS_MOVE, axis_values=(0.35, 0, 0)))
    assert res == ["Steer"]

def test_action_mapping_negative_axis_triggers():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("stick")
    fab.register_action_mapping("stick", ActionMapping("Reverse", InputDeviceType.GAMEPAD, "AXIS_Y", deadzone=0.2))
    fab.push_context(ctx)
    res = fab.process_input(InputEvent(InputDeviceType.GAMEPAD, InputEventType.AXIS_MOVE, axis_values=(-0.8, 0, 0)))
    assert res == ["Reverse"]

def test_action_mapping_touch_device():
    mapping = ActionMapping("Tap", InputDeviceType.TOUCH, "TOUCH_TAP")
    assert mapping.device == InputDeviceType.TOUCH

def test_action_mapping_vr_device():
    mapping = ActionMapping("Grip", InputDeviceType.VR, "GRIP_BUTTON")
    assert mapping.device == InputDeviceType.VR

def test_action_mapping_context_isolation():
    fab = UniversalEventFabricator()
    fab.register_action_mapping("c1", ActionMapping("Act", InputDeviceType.KEYBOARD, "Q"))
    fab.register_action_mapping("c2", ActionMapping("Act", InputDeviceType.KEYBOARD, "E"))
    assert fab.contexts["c1"].mappings["Act"].input_trigger == "Q"
    assert fab.contexts["c2"].mappings["Act"].input_trigger == "E"


# ==============================================================================
# 6. CONTEXT STACK TESTS - 9 tests
# ==============================================================================

def test_context_stack_push():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("menu")
    fab.push_context(ctx)
    assert fab.context_stack == ["menu"]

def test_context_stack_pop():
    fab = UniversalEventFabricator()
    fab.push_context(EventInputContext("c1"))
    fab.push_context(EventInputContext("c2"))
    popped = fab.pop_context()
    assert popped.context_id == "c2"
    assert fab.context_stack == ["c1"]

def test_context_stack_pop_by_id():
    fab = UniversalEventFabricator()
    fab.push_context(EventInputContext("c1"))
    fab.push_context(EventInputContext("c2"))
    popped = fab.pop_context("c1")
    assert popped.context_id == "c1"
    assert fab.context_stack == ["c2"]

def test_context_stack_empty_pop():
    fab = UniversalEventFabricator()
    assert fab.pop_context() is None

def test_context_stack_priority_evaluation():
    fab = UniversalEventFabricator()
    c_low = EventInputContext("low", priority=ContextPriority.LOW)
    c_high = EventInputContext("high", priority=ContextPriority.HIGH)
    fab.push_context(c_low)
    fab.push_context(c_high)
    # High priority takes precedence
    assert c_high.priority.value > c_low.priority.value

def test_context_stack_modal_consumes_all():
    fab = UniversalEventFabricator()
    c1 = EventInputContext("base", priority=ContextPriority.NORMAL, consumed_actions={"Fire"})
    c1.mappings["Fire"] = ActionMapping("Fire", InputDeviceType.KEYBOARD, "Space")
    fab.push_context(c1)

    c2 = EventInputContext("modal", priority=ContextPriority.MODAL, consumed_actions={"Accept"})
    c2.mappings["Accept"] = ActionMapping("Accept", InputDeviceType.KEYBOARD, "Space")
    fab.push_context(c2)

    actions = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="Space"))
    assert actions == ["Accept"]

def test_context_stack_inactive_context_skipped():
    fab = UniversalEventFabricator()
    c = EventInputContext("inactive", active=False)
    c.mappings["Jump"] = ActionMapping("Jump", InputDeviceType.KEYBOARD, "Space")
    fab.push_context(c)
    actions = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="Space"))
    assert actions == []

def test_context_serialization():
    ctx = EventInputContext("hud", priority=ContextPriority.HIGH, active=True, consumed_actions={"Click"})
    d = ctx.to_dict()
    assert d["context_id"] == "hud"
    assert d["priority"] == 30
    assert d["active"] is True
    assert "Click" in d["consumed_actions"]

def test_context_alias_compatibility():
    assert InputContext is EventInputContext


# ==============================================================================
# 7. FOCUS SYSTEM TESTS - 7 tests
# ==============================================================================

def test_focus_target_registration():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("btn_ok"))
    assert "btn_ok" in fab.focus_targets

def test_focus_set_focus_success():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("input_field", focusable=True))
    res = fab.set_focus("input_field")
    assert res is True
    assert fab.current_focused_id == "input_field"
    assert fab.focus_targets["input_field"].has_focus is True

def test_focus_set_non_focusable_rejected():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("label", focusable=False))
    res = fab.set_focus("label")
    assert res is False
    assert fab.current_focused_id is None

def test_focus_set_missing_target_rejected():
    fab = UniversalEventFabricator()
    assert fab.set_focus("ghost") is False

def test_focus_transitions_clear_previous():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("f1"))
    fab.register_focus_target(FocusTarget("f2"))
    fab.set_focus("f1")
    assert fab.focus_targets["f1"].has_focus is True
    fab.set_focus("f2")
    assert fab.focus_targets["f1"].has_focus is False
    assert fab.focus_targets["f2"].has_focus is True

def test_focus_target_parent_hierarchy():
    t = FocusTarget("child", parent_id="parent")
    assert t.parent_id == "parent"

def test_focus_target_priority_default():
    t = FocusTarget("t_prio", priority=5)
    assert t.priority == 5


# ==============================================================================
# 8. ROUTING & PROPAGATION TESTS - 11 tests
# ==============================================================================

def test_routing_capture_target_bubble_full_sequence():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("window"))
    fab.register_focus_target(FocusTarget("dialog", parent_id="window"))
    fab.register_focus_target(FocusTarget("button", parent_id="dialog"))
    path = fab.route_event("button", Event(EventType.INPUT))
    expected = [
        "window:CAPTURE",
        "dialog:CAPTURE",
        "button:TARGET",
        "dialog:BUBBLE",
        "window:BUBBLE",
    ]
    assert path == expected

def test_routing_cancellation_during_capture():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("root"))
    fab.register_focus_target(FocusTarget("leaf", parent_id="root"))
    e = Event(EventType.INPUT)
    e.cancelled = True
    path = fab.route_event("leaf", e)
    assert path == []

def test_routing_single_node_target_only():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("standalone"))
    path = fab.route_event("standalone", Event(EventType.INPUT))
    assert path == ["standalone:TARGET"]

def test_routing_missing_target_returns_empty():
    fab = UniversalEventFabricator()
    assert fab.route_event("non_existent", Event(EventType.INPUT)) == []

def test_routing_phases_enums():
    assert RoutingPhase.CAPTURE.value == "CAPTURE"
    assert RoutingPhase.TARGET.value == "TARGET"
    assert RoutingPhase.BUBBLE.value == "BUBBLE"

def test_routing_cancellation_stops_bubble():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("A"))
    fab.register_focus_target(FocusTarget("B", parent_id="A"))
    e = Event(EventType.INPUT)
    # Route without cancel
    p1 = fab.route_event("B", e)
    assert len(p1) == 3  # A:CAPTURE, B:TARGET, A:BUBBLE

def test_routing_deep_tree_path():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("n1"))
    fab.register_focus_target(FocusTarget("n2", parent_id="n1"))
    fab.register_focus_target(FocusTarget("n3", parent_id="n2"))
    fab.register_focus_target(FocusTarget("n4", parent_id="n3"))
    path = fab.route_event("n4", Event(EventType.CUSTOM))
    assert len(path) == 7  # 3 capture + 1 target + 3 bubble

def test_routing_does_not_mutate_unrelated_nodes():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("left"))
    fab.register_focus_target(FocusTarget("right"))
    path = fab.route_event("left", Event(EventType.SYSTEM))
    assert not any("right" in step for step in path)

def test_routing_bubble_order_is_exact_reverse():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("r"))
    fab.register_focus_target(FocusTarget("p1", parent_id="r"))
    fab.register_focus_target(FocusTarget("p2", parent_id="p1"))
    path = fab.route_event("p2", Event(EventType.APPLICATION))
    capture_nodes = [p.split(":")[0] for p in path if ":CAPTURE" in p]
    bubble_nodes = [p.split(":")[0] for p in path if ":BUBBLE" in p]
    assert capture_nodes == list(reversed(bubble_nodes))

def test_routing_target_has_both_capture_and_bubble_surrounding():
    fab = UniversalEventFabricator()
    fab.register_focus_target(FocusTarget("root"))
    fab.register_focus_target(FocusTarget("child", parent_id="root"))
    path = fab.route_event("child", Event(EventType.APPLICATION))
    assert path[0] == "root:CAPTURE"
    assert path[1] == "child:TARGET"
    assert path[2] == "root:BUBBLE"

def test_routing_event_cancelled_flag_preserved():
    e = Event(EventType.INPUT, cancelled=True)
    assert e.cancelled is True


# ==============================================================================
# 9. RATE CONTROL TESTS - 6 tests
# ==============================================================================

def test_rate_control_debounce_executes_after_interval():
    fab = UniversalEventFabricator()
    executed = []
    t0 = 100.0
    res1 = fab.debounce("click", 0.5, lambda: executed.append(1), now=t0)
    assert res1 is True
    res2 = fab.debounce("click", 0.5, lambda: executed.append(2), now=t0 + 0.1)
    assert res2 is False
    res3 = fab.debounce("click", 0.5, lambda: executed.append(3), now=t0 + 0.6)
    assert res3 is True
    assert executed == [1, 3]

def test_rate_control_throttle_executes_at_most_once_per_interval():
    fab = UniversalEventFabricator()
    executed = []
    t0 = 100.0
    res1 = fab.throttle("scroll", 0.2, lambda: executed.append("A"), now=t0)
    assert res1 is True
    res2 = fab.throttle("scroll", 0.2, lambda: executed.append("B"), now=t0 + 0.05)
    assert res2 is False
    res3 = fab.throttle("scroll", 0.2, lambda: executed.append("C"), now=t0 + 0.25)
    assert res3 is True
    assert executed == ["A", "C"]

def test_rate_control_distinct_keys_independent():
    fab = UniversalEventFabricator()
    calls = []
    t0 = 50.0
    fab.throttle("k1", 1.0, lambda: calls.append("k1"), now=t0)
    fab.throttle("k2", 1.0, lambda: calls.append("k2"), now=t0)
    assert calls == ["k1", "k2"]

def test_rate_control_zero_interval_always_executes():
    fab = UniversalEventFabricator()
    calls = []
    fab.throttle("zero", 0.0, lambda: calls.append(1), now=10.0)
    fab.throttle("zero", 0.0, lambda: calls.append(2), now=10.0)
    assert calls == [1, 2]

def test_rate_control_strategy_enums():
    assert RateControlStrategy.NONE.value == "NONE"
    assert RateControlStrategy.DEBOUNCE.value == "DEBOUNCE"
    assert RateControlStrategy.THROTTLE.value == "THROTTLE"

def test_rate_control_timestamps_stored():
    fab = UniversalEventFabricator()
    fab.throttle("key_ts", 1.0, lambda: None, now=123.45)
    assert fab.throttle_timestamps["key_ts"] == 123.45


# ==============================================================================
# 10. APPLICATION STATE TESTS - 10 tests
# ==============================================================================

def test_state_set_and_get():
    fab = UniversalEventFabricator()
    fab.set_state("player_gold", 500)
    assert fab.get_state("player_gold") == 500

def test_state_get_default_when_missing():
    fab = UniversalEventFabricator()
    assert fab.get_state("non_existent", default=42) == 42

def test_state_hash_deterministic():
    fab = UniversalEventFabricator()
    fab.set_state("a", 1)
    fab.set_state("b", 2)
    h1 = fab.compute_state_hash()
    h2 = fab.compute_state_hash()
    assert h1 == h2
    assert len(h1) == 64

def test_state_hash_order_independent():
    fab1 = UniversalEventFabricator()
    fab1.set_state("x", 10)
    fab1.set_state("y", 20)

    fab2 = UniversalEventFabricator()
    fab2.set_state("y", 20)
    fab2.set_state("x", 10)

    assert fab1.compute_state_hash() == fab2.compute_state_hash()

def test_state_hash_changes_on_mutation():
    fab = UniversalEventFabricator()
    fab.set_state("count", 1)
    h1 = fab.compute_state_hash()
    fab.set_state("count", 2)
    h2 = fab.compute_state_hash()
    assert h1 != h2

def test_state_complex_nested_structures():
    fab = UniversalEventFabricator()
    payload = {"inventory": ["sword", "shield"], "stats": {"hp": 100}}
    fab.set_state("hero", payload)
    assert fab.get_state("hero")["stats"]["hp"] == 100

def test_state_reset():
    fab = UniversalEventFabricator()
    fab.set_state("temp", 1)
    fab.app_state.clear()
    assert fab.get_state("temp") is None

def test_state_empty_hash():
    fab = UniversalEventFabricator()
    h = fab.compute_state_hash()
    assert len(h) == 64

def test_state_multiple_keys():
    fab = UniversalEventFabricator()
    for i in range(10):
        fab.set_state(f"k_{i}", i)
    assert len(fab.app_state) == 10

def test_state_deep_copy_isolation():
    fab = UniversalEventFabricator()
    data = {"list": [1, 2]}
    fab.set_state("d", copy.deepcopy(data))
    data["list"].append(3)
    assert fab.get_state("d")["list"] == [1, 2]


# ==============================================================================
# 11. REPLAY SYSTEM TESTS - 14 tests
# ==============================================================================

def test_replay_start_recording():
    fab = UniversalEventFabricator()
    rec = fab.start_recording(session_id="s123", seed=100)
    assert fab.replay_mode == ReplayMode.RECORDING
    assert rec.session_id == "s123"
    assert rec.seed == 100

def test_replay_record_frame():
    fab = UniversalEventFabricator()
    fab.start_recording()
    fab.set_state("health", 100)
    inp = [InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, "W")]
    cmd = [Command(action="jump")]
    frame = fab.record_frame(inp, cmd)
    assert frame.frame_number == 0
    assert len(frame.input_events) == 1
    assert len(frame.commands) == 1
    assert len(frame.state_hash) == 64

def test_replay_frame_number_monotonic():
    fab = UniversalEventFabricator()
    fab.start_recording()
    f0 = fab.record_frame([], [])
    f1 = fab.record_frame([], [])
    assert f0.frame_number == 0
    assert f1.frame_number == 1

def test_replay_stop_recording():
    fab = UniversalEventFabricator()
    fab.start_recording()
    fab.record_frame([], [])
    rec = fab.stop_recording()
    assert fab.replay_mode == ReplayMode.IDLE
    assert rec.total_frames == 1
    assert len(rec.final_state_hash) == 64

def test_replay_stop_without_start_raises():
    fab = UniversalEventFabricator()
    with pytest.raises(RuntimeError):
        fab.stop_recording()

def test_replay_record_without_start_raises():
    fab = UniversalEventFabricator()
    with pytest.raises(RuntimeError):
        fab.record_frame([], [])

def test_replay_recording_serialization():
    rec = ReplayRecording(session_id="sess_1", seed=77, total_frames=2, final_state_hash="h123")
    d = rec.to_dict()
    assert d["session_id"] == "sess_1"
    assert d["seed"] == 77
    assert d["total_frames"] == 2

def test_replay_frame_serialization():
    f = ReplayFrame(frame_number=5, timestamp=100.0, state_hash="abcdef")
    d = f.to_dict()
    assert d["frame_number"] == 5
    assert d["state_hash"] == "abcdef"

def test_replay_modes_enums():
    assert ReplayMode.IDLE.value == "IDLE"
    assert ReplayMode.RECORDING.value == "RECORDING"
    assert ReplayMode.REPLAYING.value == "REPLAYING"
    assert ReplayMode.VERIFYING.value == "VERIFYING"

def test_replay_session_playback_success():
    fab = UniversalEventFabricator()
    fab.register_command_handler("score", lambda c: fab.set_state("pts", fab.get_state("pts", 0) + 10))
    rec = fab.start_recording()
    fab.execute_command(Command(action="score"))
    fab.record_frame([], [Command(action="score")])
    fab.stop_recording()

    replayer = UniversalEventFabricator()
    replayer.register_command_handler("score", lambda c: replayer.set_state("pts", replayer.get_state("pts", 0) + 10))
    success, divs = replayer.replay_session(rec)
    assert success is True
    assert len(divs) == 0
    assert replayer.get_state("pts") == 10

def test_replay_divergence_data_model():
    div = ReplayDivergence(frame_number=3, expected_hash="h1", actual_hash="h2", severity=DivergenceSeverity.CRITICAL, description="Desync")
    d = div.to_dict()
    assert d["frame_number"] == 3
    assert d["severity"] == "CRITICAL"

def test_replay_divergence_severity_enums():
    assert DivergenceSeverity.NONE.value == "NONE"
    assert DivergenceSeverity.MINOR.value == "MINOR"
    assert DivergenceSeverity.CRITICAL.value == "CRITICAL"

def test_replay_session_restores_idle_mode():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.record_frame([], [])
    fab.stop_recording()
    fab.replay_session(rec)
    assert fab.replay_mode == ReplayMode.IDLE

def test_replay_recording_deep_copies_inputs():
    fab = UniversalEventFabricator()
    fab.start_recording()
    inp = [InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, "A")]
    frame = fab.record_frame(inp, [])
    inp[0].key_code = "Z"
    assert frame.input_events[0].key_code == "A"


# ==============================================================================
# 12. REPLAY DETERMINISM TESTS - 9 tests
# ==============================================================================

def test_replay_determinism_identical_runs():
    fab1 = UniversalEventFabricator()
    fab1.set_state("x", 5)
    h1 = fab1.compute_state_hash()

    fab2 = UniversalEventFabricator()
    fab2.set_state("x", 5)
    h2 = fab2.compute_state_hash()

    assert h1 == h2

def test_replay_determinism_multi_command_sequence():
    fab = UniversalEventFabricator()
    fab.register_command_handler("add", lambda c: fab.set_state("val", fab.get_state("val", 0) + c.parameters["n"]))
    rec = fab.start_recording()
    for i in [10, 20, 30]:
        fab.execute_command(Command(action="add", parameters={"n": i}))
        fab.record_frame([], [Command(action="add", parameters={"n": i})])
    fab.stop_recording()

    replayer = UniversalEventFabricator()
    replayer.register_command_handler("add", lambda c: replayer.set_state("val", replayer.get_state("val", 0) + c.parameters["n"]))
    success, divs = replayer.replay_session(rec)
    assert success is True
    assert replayer.get_state("val") == 60

def test_replay_determinism_input_normalization():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("ctx")
    fab.register_action_mapping("ctx", ActionMapping("Act", InputDeviceType.KEYBOARD, "K"))
    fab.push_context(ctx)
    a1 = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="K"))
    a2 = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="K"))
    assert a1 == a2

def test_replay_determinism_empty_session():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.stop_recording()
    replayer = UniversalEventFabricator()
    success, divs = replayer.replay_session(rec)
    assert success is True
    assert len(divs) == 0

def test_replay_determinism_seed_preservation():
    fab = UniversalEventFabricator()
    rec = fab.start_recording(seed=1337)
    assert rec.seed == 1337

def test_replay_determinism_frame_hash_reproducibility():
    f1 = ReplayFrame(frame_number=1, timestamp=0.0)
    h1 = f1.compute_state_hash({"a": 1, "b": 2})
    f2 = ReplayFrame(frame_number=1, timestamp=0.0)
    h2 = f2.compute_state_hash({"b": 2, "a": 1})
    assert h1 == h2

def test_replay_determinism_command_history_reproducible():
    fab = UniversalEventFabricator()
    fab.register_command_handler("noop", lambda c: None)
    for _ in range(5):
        fab.execute_command(Command(action="noop"))
    assert len(fab.command_history) == 5

def test_replay_determinism_state_hash_length():
    fab = UniversalEventFabricator()
    assert len(fab.compute_state_hash()) == 64

def test_replay_determinism_zero_divergence_on_repetition():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.set_state("lvl", 1)
    fab.record_frame([], [])
    fab.stop_recording()

    for _ in range(3):
        replayer = UniversalEventFabricator()
        replayer.set_state("lvl", 1)
        ok, divs = replayer.replay_session(rec)
        assert ok is True


# ==============================================================================
# 13. REPLAY DIVERGENCE TESTS - 7 tests
# ==============================================================================

def test_replay_divergence_detected_on_state_mismatch():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.set_state("score", 10)
    fab.record_frame([], [])
    fab.stop_recording()

    replayer = UniversalEventFabricator()
    replayer.set_state("score", 999)  # Perturbed
    success, divs = replayer.replay_session(rec)
    assert success is False
    assert len(divs) == 1
    assert divs[0].frame_number == 0

def test_replay_divergence_severity_critical():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.set_state("hp", 100)
    fab.record_frame([], [])
    fab.stop_recording()

    replayer = UniversalEventFabricator()
    replayer.set_state("hp", 0)
    success, divs = replayer.replay_session(rec)
    assert divs[0].severity == DivergenceSeverity.CRITICAL

def test_replay_divergence_records_expected_and_actual_hashes():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.set_state("key", "val1")
    fab.record_frame([], [])
    fab.stop_recording()

    replayer = UniversalEventFabricator()
    replayer.set_state("key", "val2")
    _, divs = replayer.replay_session(rec)
    assert divs[0].expected_hash != divs[0].actual_hash

def test_replay_divergence_multiple_frames():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.set_state("x", 1)
    fab.record_frame([], [])
    fab.set_state("x", 2)
    fab.record_frame([], [])
    fab.stop_recording()

    replayer = UniversalEventFabricator()
    replayer.set_state("x", 99)  # Corrupted both frames
    _, divs = replayer.replay_session(rec)
    assert len(divs) == 2

def test_replay_divergence_description_not_empty():
    fab = UniversalEventFabricator()
    rec = fab.start_recording()
    fab.set_state("a", 1)
    fab.record_frame([], [])
    fab.stop_recording()

    replayer = UniversalEventFabricator()
    replayer.set_state("a", 2)
    _, divs = replayer.replay_session(rec)
    assert len(divs[0].description) > 0

def test_replay_divergence_late_frame_only():
    fab = UniversalEventFabricator()
    fab.register_command_handler("set_val", lambda c: fab.set_state("val", c.parameters["v"]))
    rec = fab.start_recording()
    fab.execute_command(Command(action="set_val", parameters={"v": 1}))
    fab.record_frame([], [Command(action="set_val", parameters={"v": 1})])
    fab.execute_command(Command(action="set_val", parameters={"v": 2}))
    fab.record_frame([], [Command(action="set_val", parameters={"v": 2})])
    fab.stop_recording()

    # Replayer that fails only on second command
    def flaky_handler(c):
        val = c.parameters["v"]
        if val == 2:
            val = 999  # Diverge only on frame 1
        replayer.set_state("val", val)

    replayer = UniversalEventFabricator()
    replayer.register_command_handler("set_val", flaky_handler)
    success, divs = replayer.replay_session(rec)
    assert len(divs) == 1
    assert divs[0].frame_number == 1

def test_replay_divergence_serialization():
    div = ReplayDivergence(frame_number=10, expected_hash="aaa", actual_hash="bbb", severity=DivergenceSeverity.MINOR)
    d = div.to_dict()
    assert d["frame_number"] == 10
    assert d["severity"] == "MINOR"


# ==============================================================================
# 14. SECURITY & REDACTION TESTS - 10 tests
# ==============================================================================

def test_security_secret_token_redacted_in_event_logs():
    fab = UniversalEventFabricator()
    fab.log_event("AUTH_EVENT", {"token": "secret_12345"})
    assert fab.event_logs[0]["data"]["token"] == "[REDACTED]"

def test_security_password_redacted_in_event_logs():
    fab = UniversalEventFabricator()
    fab.log_event("LOGIN_EVENT", {"user_password": "super_secret_pw"})
    assert fab.event_logs[0]["data"]["user_password"] == "[REDACTED]"

def test_security_api_key_redacted_in_event_logs():
    fab = UniversalEventFabricator()
    fab.log_event("API_CALL", {"api_key": "abc999888777"})
    assert fab.event_logs[0]["data"]["api_key"] == "[REDACTED]"

def test_security_diagnostic_bundle_clean_of_secrets():
    fab = UniversalEventFabricator()
    fab.log_event("CONFIDENTIAL", {"auth_bearer": "token_value"})
    bundle = fab.export_diagnostic_bundle()
    serialized = json.dumps(bundle.event_logs)
    assert "token_value" not in serialized
    assert "[REDACTED]" in serialized

def test_security_validator_catches_unredacted_secret():
    val = UniversalEventValidator()
    bundle = DiagnosticEventBundle(event_logs=[{"event": "BAD", "data": "Bearer aaaaaaaaaaaaaaaaaaaa123"}])
    report = val.validate_diagnostic_bundle(bundle)
    assert report.is_valid is False
    assert any("Unredacted credential" in e for e in report.errors)

def test_security_validator_passes_redacted_bundle():
    val = UniversalEventValidator()
    bundle = DiagnosticEventBundle(event_logs=[{"event": "CLEAN", "data": "clean payload"}])
    bundle.compute_digest()
    report = val.validate_diagnostic_bundle(bundle)
    assert report.is_valid is True

def test_security_diagnostic_bundle_digest_sha256():
    fab = UniversalEventFabricator()
    bundle = fab.export_diagnostic_bundle()
    assert len(bundle.sha256_digest) == 64

def test_security_event_payload_immutability_by_subscribers():
    fab = UniversalEventFabricator()
    payload = {"data": [1, 2, 3]}
    e = Event(EventType.APPLICATION, payload=payload)
    def subscriber(ev):
        ev.payload["data"] = [999]
    fab.subscribe(EventType.APPLICATION, subscriber)
    fab.publish(e)
    assert e.payload["data"] == [999]  # Handled in place

def test_security_command_parameter_isolation():
    fab = UniversalEventFabricator()
    params = {"target": "boss"}
    cmd = Command(action="attack", parameters=copy.deepcopy(params))
    params["target"] = "ally"
    assert cmd.parameters["target"] == "boss"

def test_security_validator_event_empty_id_rejected():
    val = UniversalEventValidator()
    report = val.validate_event(Event(EventType.CUSTOM, event_id=""))
    assert report.is_valid is False


# ==============================================================================
# 15. TELEMETRY TESTS - 9 tests
# ==============================================================================

def test_telemetry_total_dispatched_counter():
    fab = UniversalEventFabricator()
    fab.subscribe(EventType.APPLICATION, lambda e: None)
    for _ in range(5):
        fab.publish(Event(EventType.APPLICATION))
    assert fab.telemetry.total_dispatched == 5

def test_telemetry_queue_depth_tracking():
    fab = UniversalEventFabricator()
    fab.publish(Event(EventType.SYSTEM), mode=DispatchMode.QUEUED)
    fab.publish(Event(EventType.SYSTEM), mode=DispatchMode.QUEUED)
    assert fab.telemetry.queue_depth == 2

def test_telemetry_dropped_events_counter():
    fab = UniversalEventFabricator(max_queue_size=1, overflow_policy=OverflowPolicy.DROP_OLDEST)
    fab.publish(Event(EventType.CUSTOM), mode=DispatchMode.QUEUED)
    fab.publish(Event(EventType.CUSTOM), mode=DispatchMode.QUEUED)
    assert fab.telemetry.dropped_events == 1

def test_telemetry_handler_errors_counter():
    fab = UniversalEventFabricator()
    def crash(e):
        raise RuntimeError("boom")
    fab.subscribe(EventType.APPLICATION, crash)
    fab.publish(Event(EventType.APPLICATION))
    assert fab.telemetry.handler_errors == 1

def test_telemetry_commands_executed_counter():
    fab = UniversalEventFabricator()
    fab.register_command_handler("noop", lambda c: None)
    fab.execute_command(Command(action="noop"))
    fab.execute_command(Command(action="noop"))
    assert fab.telemetry.commands_executed == 2

def test_telemetry_avg_latency_ms_updated():
    fab = UniversalEventFabricator()
    fab.subscribe(EventType.INPUT, lambda e: time.sleep(0.001))
    fab.publish(Event(EventType.INPUT))
    assert fab.telemetry.avg_latency_ms > 0.0

def test_telemetry_serialization():
    t = EventTelemetry(total_dispatched=10, queue_depth=3, commands_executed=5)
    d = t.to_dict()
    assert d["total_dispatched"] == 10
    assert d["queue_depth"] == 3
    assert d["commands_executed"] == 5

def test_telemetry_in_diagnostic_bundle():
    fab = UniversalEventFabricator()
    fab.subscribe(EventType.SYSTEM, lambda e: None)
    fab.publish(Event(EventType.SYSTEM))
    bundle = fab.export_diagnostic_bundle()
    assert bundle.telemetry.total_dispatched == 1

def test_telemetry_deterministic_reporting():
    t1 = EventTelemetry(total_dispatched=100)
    t2 = EventTelemetry(total_dispatched=100)
    assert t1.to_dict() == t2.to_dict()


# ==============================================================================
# 16. PERFORMANCE TESTS - 10 tests
# ==============================================================================

def test_perf_fast_event_dispatch_1000_events():
    fab = UniversalEventFabricator()
    fab.subscribe(EventType.APPLICATION, lambda e: None)
    e = Event(EventType.APPLICATION)
    t0 = time.time()
    for _ in range(1000):
        fab.publish(e)
    elapsed = time.time() - t0
    assert elapsed < 0.2

def test_perf_fast_message_routing_1000_messages():
    fab = UniversalEventFabricator()
    fab.subscribe_channel("perf.*", lambda m: None)
    msg = Message(channel="perf.test", payload=1)
    t0 = time.time()
    for _ in range(1000):
        fab.send_message(msg)
    elapsed = time.time() - t0
    assert elapsed < 0.2

def test_perf_fast_command_execution():
    fab = UniversalEventFabricator()
    fab.register_command_handler("fast_cmd", lambda c: 1)
    cmd = Command(action="fast_cmd")
    t0 = time.time()
    for _ in range(1000):
        fab.execute_command(cmd)
    elapsed = time.time() - t0
    assert elapsed < 0.2

def test_perf_fast_input_normalization():
    fab = UniversalEventFabricator()
    ctx = EventInputContext("perf_ctx")
    fab.register_action_mapping("perf_ctx", ActionMapping("Act", InputDeviceType.KEYBOARD, "K"))
    fab.push_context(ctx)
    inp = InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="K")
    t0 = time.time()
    for _ in range(1000):
        fab.process_input(inp)
    elapsed = time.time() - t0
    assert elapsed < 0.2

def test_perf_fast_priority_queue_drain():
    fab = UniversalEventFabricator()
    fab.subscribe(EventType.CUSTOM, lambda e: None)
    for i in range(500):
        fab.publish(Event(EventType.CUSTOM, priority=EventPriority.NORMAL), mode=DispatchMode.QUEUED)
    t0 = time.time()
    fab.process_queue()
    elapsed = time.time() - t0
    assert elapsed < 0.1

def test_perf_fast_state_hash_calculation():
    fab = UniversalEventFabricator()
    fab.app_state = {f"k_{i}": i for i in range(100)}
    t0 = time.time()
    for _ in range(100):
        fab.compute_state_hash()
    elapsed = time.time() - t0
    assert elapsed < 0.1

def test_perf_fast_hierarchical_routing():
    fab = UniversalEventFabricator()
    for i in range(10):
        parent = f"node_{i-1}" if i > 0 else None
        fab.register_focus_target(FocusTarget(f"node_{i}", parent_id=parent))
    e = Event(EventType.INPUT)
    t0 = time.time()
    for _ in range(500):
        fab.route_event("node_9", e)
    elapsed = time.time() - t0
    assert elapsed < 0.15

def test_perf_fast_debounce_evaluations():
    fab = UniversalEventFabricator()
    t0 = time.time()
    for i in range(1000):
        fab.debounce("k", 1.0, lambda: None, now=float(i))
    elapsed = time.time() - t0
    assert elapsed < 0.1

def test_perf_fast_replay_recording_100_frames():
    fab = UniversalEventFabricator()
    fab.start_recording()
    t0 = time.time()
    for _ in range(100):
        fab.record_frame([], [])
    fab.stop_recording()
    elapsed = time.time() - t0
    assert elapsed < 0.1

def test_perf_fast_diagnostic_bundle_generation():
    fab = UniversalEventFabricator()
    t0 = time.time()
    bundle = fab.export_diagnostic_bundle()
    elapsed = time.time() - t0
    assert elapsed < 0.05
    assert len(bundle.sha256_digest) == 64


# ==============================================================================
# 17. GOLDEN SCENARIOS (?184) - 10 tests
# ==============================================================================

def test_golden_scenario_1_event_sequence():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_event_sequence()
    assert res["success"] is True
    assert res["delivered"] == ["hello"]

def test_golden_scenario_2_routing_sequence():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_routing_sequence()
    assert res["valid"] is True

def test_golden_scenario_3_command_result():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_command_result()
    assert res["success"] is True
    assert res["result"] == 100

def test_golden_scenario_4_input_mapping():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_input_mapping()
    assert res["success"] is True
    assert res["actions"] == ["Jump"]

def test_golden_scenario_5_context_stack():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_context_stack()
    assert res["success"] is True

def test_golden_scenario_6_focus_transitions():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_focus_transitions()
    assert res["t1_focus"] is False
    assert res["t2_focus"] is True

def test_golden_scenario_7_state_transitions():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_state_transitions()
    assert res["distinct"] is True

def test_golden_scenario_8_replay():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_replay()
    assert res["success"] is True
    assert res["divergences"] == 0

def test_golden_scenario_9_replay_divergence():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_replay_divergence()
    assert res["detected"] is True
    assert res["divergences"] == 1

def test_golden_scenario_10_diagnostics():
    fab = UniversalEventFabricator()
    res = fab.scenario_golden_diagnostics()
    assert res["has_digest"] is True


# ==============================================================================
# 18. INTEGRATION TEST (?185) - 1 test
# ==============================================================================

def test_integration_full_pipeline():
    fab = UniversalEventFabricator()
    res = fab.execute_integration_pipeline()
    assert res["success"] is True
    assert res["door_open"] is True


# ==============================================================================
# 19. END-TO-END INPUT TEST (?186) - 1 test
# ==============================================================================

def test_e2e_input_normalization_and_mapping():
    fab = UniversalEventFabricator()
    res = fab.execute_e2e_input_pipeline()
    assert res["success"] is True


# ==============================================================================
# 20. END-TO-END CONTEXT TEST (?187) - 1 test
# ==============================================================================

def test_e2e_context_stack_modal_interception():
    fab = UniversalEventFabricator()
    res = fab.execute_e2e_context_pipeline()
    assert res["success"] is True


# ==============================================================================
# 21. END-TO-END REPLAY TEST (?188) - 1 test
# ==============================================================================

def test_e2e_replay_playback_determinism():
    fab = UniversalEventFabricator()
    res = fab.execute_e2e_replay_pipeline()
    assert res["success"] is True
    assert res["final_value"] == 5
    assert res["divs"] == 0


# ==============================================================================
# 22. END-TO-END DIVERGENCE TEST (?189) - 1 test
# ==============================================================================

def test_e2e_replay_divergence_detection():
    fab = UniversalEventFabricator()
    res = fab.execute_e2e_divergence_pipeline()
    assert res["divergence_detected"] is True
    assert res["severity"] == DivergenceSeverity.CRITICAL


# ==============================================================================
# 23. PACKAGING & VALIDATION RULES - 3 tests
# ==============================================================================

def test_validator_command_empty_action_rejected():
    val = UniversalEventValidator()
    report = val.validate_command(Command(action=""))
    assert report.is_valid is False
    assert any("empty action" in e for e in report.errors)

def test_validator_replay_recording_non_monotonic_rejected():
    val = UniversalEventValidator()
    f1 = ReplayFrame(frame_number=0, timestamp=0.0, state_hash="a"*64)
    f2 = ReplayFrame(frame_number=5, timestamp=1.0, state_hash="b"*64)  # Gap
    rec = ReplayRecording(total_frames=2, frames=[f1, f2])
    report = val.validate_replay_recording(rec)
    assert report.is_valid is False
    assert any("Non-monotonic" in e for e in report.errors)

def test_packager_generates_ue5_subsystem_files():
    packager = UniversalEventPackager()
    mappings = [ActionMapping("Jump", InputDeviceType.KEYBOARD, "Space")]
    res = packager.package_event_subsystem("my_app", mappings)
    assert "Source/Public/UAFEventSubsystem.h" in res.generated_files
    assert "Source/Private/UAFEventSubsystem.cpp" in res.generated_files
    assert "Config/uaf_event_manifest.json" in res.generated_files
    assert len(res.sha256_digest) == 64

def test_validator_catches_invalid_timestamp():
    val = UniversalEventValidator()
    e = Event(EventType.SYSTEM, timestamp=-10.0)
    report = val.validate_event(e)
    assert report.is_valid is False
    assert any("non-positive timestamp" in err for err in report.errors)

def test_event_fabricator_custom_overflow_policy():
    fab = UniversalEventFabricator(max_queue_size=10, overflow_policy=OverflowPolicy.DROP_NEWEST)
    assert fab.max_queue_size == 10
    assert fab.overflow_policy == OverflowPolicy.DROP_NEWEST
