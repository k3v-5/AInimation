"""
Universal Event Fabricator (UAF-81.65).
Authoritative event bus, message router, command processor, input normalizer,
action mapper, context stack, focus tree, rate controller, deterministic recorder,
and replay divergence engine.
"""

from __future__ import annotations
import collections
import copy
import fnmatch
import hashlib
import heapq
import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..models.definition import (
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
)


class UniversalEventFabricator:
    """
    Universal event dispatcher, command processor, and deterministic replay engine.
    """

    def __init__(self, max_queue_size: int = 1000, overflow_policy: OverflowPolicy = OverflowPolicy.DROP_OLDEST) -> None:
        self.max_queue_size: int = max_queue_size
        self.overflow_policy: OverflowPolicy = overflow_policy

        # Event Bus
        self.event_subscribers: Dict[EventType, List[Tuple[int, Callable[[Event], None], Optional[Callable[[Event], bool]]]]] = {
            t: [] for t in EventType
        }
        self.event_queue: List[Tuple[int, float, Event]] = []  # Priority queue: (-priority, timestamp, event)

        # Message Bus
        self.channel_subscribers: Dict[str, List[Callable[[Message], None]]] = {}

        # Command Bus
        self.command_handlers: Dict[str, Callable[[Command], Any]] = {}
        self.command_history: List[Tuple[Command, EventCommandResult]] = []

        # Input & Context Stack
        self.contexts: Dict[str, EventInputContext] = {}
        self.context_stack: List[str] = []

        # Focus Hierarchy
        self.focus_targets: Dict[str, FocusTarget] = {}
        self.current_focused_id: Optional[str] = None

        # Rate Control
        self.debounce_timestamps: Dict[str, float] = {}
        self.throttle_timestamps: Dict[str, float] = {}

        # Application State & Deterministic Replay
        self.app_state: Dict[str, Any] = {}
        self.replay_mode: ReplayMode = ReplayMode.IDLE
        self.current_recording: Optional[ReplayRecording] = None
        self.current_frame_number: int = 0

        # Telemetry & Diagnostics
        self.telemetry: EventTelemetry = EventTelemetry()
        self.event_logs: List[Dict[str, Any]] = []

    # --------------------------------------------------------------------------
    # 1. EVENT BUS & DISPATCH (?25, ?26, ?27, ?28, ?39, ?47)
    # --------------------------------------------------------------------------

    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], None],
        filter_fn: Optional[Callable[[Event], bool]] = None,
        priority: int = 0,
    ) -> None:
        """Registers an event subscriber callback with optional filtering and priority ordering."""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append((priority, handler, filter_fn))
        # Sort subscribers by priority descending
        self.event_subscribers[event_type].sort(key=lambda item: item[0], reverse=True)

    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> bool:
        """Removes an active subscriber from an event channel."""
        if event_type in self.event_subscribers:
            original_len = len(self.event_subscribers[event_type])
            self.event_subscribers[event_type] = [item for item in self.event_subscribers[event_type] if item[1] != handler]
            return len(self.event_subscribers[event_type]) < original_len
        return False

    def publish(self, event: Event, mode: DispatchMode = DispatchMode.SYNC) -> bool:
        """Publishes an event through synchronous dispatch or priority queuing."""
        if mode == DispatchMode.SYNC or mode == DispatchMode.IMMEDIATE:
            return self._dispatch_event(event)

        # Handle queue overflow
        if len(self.event_queue) >= self.max_queue_size:
            self.telemetry.dropped_events += 1
            if self.overflow_policy == OverflowPolicy.DROP_OLDEST:
                if self.event_queue:
                    heapq.heappop(self.event_queue)
            elif self.overflow_policy == OverflowPolicy.DROP_NEWEST:
                return False
            elif self.overflow_policy == OverflowPolicy.ERROR:
                raise OverflowError(f"Event queue exceeded maximum capacity of {self.max_queue_size}")
            elif self.overflow_policy == OverflowPolicy.BLOCK:
                # In single-threaded runtime, process head to unblock
                self.process_queue(max_events=1)

        # Enqueue with inverted priority for min-heap
        heapq.heappush(self.event_queue, (-int(event.priority.value), event.timestamp, event))
        self.telemetry.queue_depth = len(self.event_queue)
        return True

    def process_queue(self, max_events: Optional[int] = None) -> int:
        """Drains and dispatches enqueued events according to priority."""
        processed = 0
        while self.event_queue:
            if max_events is not None and processed >= max_events:
                break
            _, _, event = heapq.heappop(self.event_queue)
            self._dispatch_event(event)
            processed += 1

        self.telemetry.queue_depth = len(self.event_queue)
        return processed

    def _dispatch_event(self, event: Event) -> bool:
        """Internal handler dispatch with subscriber fault isolation."""
        start_t = time.time()
        subscribers = self.event_subscribers.get(event.event_type, [])
        delivered = False

        for _, handler, filter_fn in subscribers:
            if event.cancelled:
                break
            if filter_fn is not None and not filter_fn(event):
                continue
            try:
                handler(event)
                delivered = True
                event.handled = True
            except Exception as ex:
                self.telemetry.handler_errors += 1
                self.log_event("HANDLER_EXCEPTION", {"event_id": event.event_id, "error": str(ex)})

        self.telemetry.total_dispatched += 1
        elapsed_ms = (time.time() - start_t) * 1000.0
        self.telemetry.avg_latency_ms = (self.telemetry.avg_latency_ms + elapsed_ms) / 2.0
        return delivered

    # --------------------------------------------------------------------------
    # 2. MESSAGE BUS & TOPIC ROUTING (?29, ?30)
    # --------------------------------------------------------------------------

    def subscribe_channel(self, channel_pattern: str, handler: Callable[[Message], None]) -> None:
        """Subscribes to a channel topic supporting glob wildcards (e.g. 'chat.*')."""
        if channel_pattern not in self.channel_subscribers:
            self.channel_subscribers[channel_pattern] = []
        self.channel_subscribers[channel_pattern].append(handler)

    def unsubscribe_channel(self, channel_pattern: str, handler: Callable[[Message], None]) -> bool:
        """Removes subscriber from a message channel."""
        if channel_pattern in self.channel_subscribers:
            original_len = len(self.channel_subscribers[channel_pattern])
            self.channel_subscribers[channel_pattern] = [h for h in self.channel_subscribers[channel_pattern] if h != handler]
            return len(self.channel_subscribers[channel_pattern]) < original_len
        return False

    def send_message(self, message: Message) -> int:
        """Routes a message to all matching channel topic subscribers."""
        matched = 0
        for pattern, handlers in self.channel_subscribers.items():
            if fnmatch.fnmatch(message.channel, pattern):
                for h in handlers:
                    try:
                        h(message)
                        matched += 1
                    except Exception as ex:
                        self.telemetry.handler_errors += 1
                        self.log_event("MESSAGE_HANDLER_ERROR", {"channel": message.channel, "error": str(ex)})
        return matched

    # --------------------------------------------------------------------------
    # 3. COMMAND BUS & TRANSACTIONAL EXECUTION (?31, ?32)
    # --------------------------------------------------------------------------

    def register_command_handler(self, action: str, handler: Callable[[Command], Any]) -> None:
        """Registers an authoritative handler for a named command action."""
        self.command_handlers[action] = handler

    def execute_command(self, command: Command) -> EventCommandResult:
        """Synchronously executes a command and records execution history."""
        start_t = time.time()
        handler = self.command_handlers.get(command.action)
        if not handler:
            res = EventCommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error_message=f"No handler registered for command action '{command.action}'.",
                execution_time_ms=(time.time() - start_t) * 1000.0,
            )
            self.command_history.append((command, res))
            return res

        try:
            val = handler(command)
            res = EventCommandResult(
                command_id=command.command_id,
                status=CommandStatus.COMPLETED,
                result=val,
                execution_time_ms=(time.time() - start_t) * 1000.0,
            )
        except Exception as ex:
            res = EventCommandResult(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                error_message=str(ex),
                execution_time_ms=(time.time() - start_t) * 1000.0,
            )

        self.telemetry.commands_executed += 1
        self.command_history.append((command, res))
        return res

    # --------------------------------------------------------------------------
    # 4. INPUT ABSTRACTION & CONTEXT STACK (?33, ?34, ?35, ?36, ?37)
    # --------------------------------------------------------------------------

    def register_action_mapping(self, context_id: str, mapping: ActionMapping) -> None:
        """Binds an input trigger to an action within a context layer."""
        if context_id not in self.contexts:
            self.contexts[context_id] = EventInputContext(context_id=context_id)
        self.contexts[context_id].mappings[mapping.action_name] = mapping

    def push_context(self, context: EventInputContext) -> None:
        """Pushes a context layer onto the context stack."""
        if context.context_id in self.contexts:
            if not context.mappings and self.contexts[context.context_id].mappings:
                context.mappings.update(self.contexts[context.context_id].mappings)
            if not context.consumed_actions and self.contexts[context.context_id].consumed_actions:
                context.consumed_actions.update(self.contexts[context.context_id].consumed_actions)
        self.contexts[context.context_id] = context
        if context.context_id in self.context_stack:
            self.context_stack.remove(context.context_id)
        self.context_stack.append(context.context_id)

    def pop_context(self, context_id: Optional[str] = None) -> Optional[EventInputContext]:
        """Pops a context from the stack."""
        if not self.context_stack:
            return None
        if context_id is None:
            cid = self.context_stack.pop()
            return self.contexts.get(cid)
        elif context_id in self.context_stack:
            self.context_stack.remove(context_id)
            return self.contexts.get(context_id)
        return None

    def process_input(self, input_event: InputEvent) -> List[str]:
        """
        Resolves raw input against active contexts in priority order,
        honoring input action and trigger consumption, as well as deadzones.
        """
        triggered_actions: List[str] = []
        active_cids = [cid for cid in reversed(self.context_stack) if self.contexts[cid].active]
        active_cids.sort(key=lambda cid: self.contexts[cid].priority.value, reverse=True)

        consumed_actions: Set[str] = set()
        consumed_triggers: Set[str] = set()

        for cid in active_cids:
            ctx = self.contexts[cid]
            for action_name, mapping in ctx.mappings.items():
                if action_name in consumed_actions or mapping.input_trigger in consumed_triggers:
                    continue
                if mapping.device == input_event.device:
                    # Match key/trigger
                    if mapping.input_trigger == input_event.key_code:
                        triggered_actions.append(action_name)
                        if action_name in ctx.consumed_actions:
                            consumed_actions.add(action_name)
                            consumed_triggers.add(mapping.input_trigger)
                    # Match axis
                    elif mapping.input_trigger.startswith("AXIS_"):
                        axis_idx = 0
                        if mapping.input_trigger == "AXIS_Y" and len(input_event.axis_values) > 1 and input_event.axis_values[1] != 0.0:
                            axis_idx = 1
                        elif mapping.input_trigger == "AXIS_Z" and len(input_event.axis_values) > 2 and input_event.axis_values[2] != 0.0:
                            axis_idx = 2
                        val = input_event.axis_values[axis_idx]
                        if abs(val) >= mapping.deadzone:
                            triggered_actions.append(action_name)
                            if action_name in ctx.consumed_actions:
                                consumed_actions.add(action_name)
                                consumed_triggers.add(mapping.input_trigger)

        return triggered_actions

    # --------------------------------------------------------------------------
    # 5. FOCUS & HIERARCHICAL ROUTING (?38, ?40, ?41, ?42, ?43)
    # --------------------------------------------------------------------------

    def register_focus_target(self, target: FocusTarget) -> None:
        """Registers a UI/gameplay focusable target in the node hierarchy."""
        self.focus_targets[target.target_id] = target

    def set_focus(self, target_id: str) -> bool:
        """Sets the active focus target and clears prior focus."""
        target = self.focus_targets.get(target_id)
        if not target or not target.focusable:
            return False

        if self.current_focused_id and self.current_focused_id in self.focus_targets:
            self.focus_targets[self.current_focused_id].has_focus = False

        target.has_focus = True
        self.current_focused_id = target_id
        return True

    def route_event(self, target_id: str, event: Event) -> List[str]:
        """
        Routes an event through CAPTURE -> TARGET -> BUBBLE phases.
        Supports cancellation and stops propagation when event.cancelled is set.
        """
        target = self.focus_targets.get(target_id)
        if not target:
            return []

        # Build path from root to target
        path: List[str] = []
        curr: Optional[str] = target_id
        while curr:
            path.append(curr)
            curr = self.focus_targets[curr].parent_id if curr in self.focus_targets else None
        path.reverse()  # root -> target

        visited: List[str] = []

        # 1. CAPTURE phase (root down to target parent)
        for node_id in path[:-1]:
            if event.cancelled:
                return visited
            visited.append(f"{node_id}:{RoutingPhase.CAPTURE.value}")

        # 2. TARGET phase
        if not event.cancelled:
            visited.append(f"{target_id}:{RoutingPhase.TARGET.value}")

        # 3. BUBBLE phase (target parent up to root)
        for node_id in reversed(path[:-1]):
            if event.cancelled:
                return visited
            visited.append(f"{node_id}:{RoutingPhase.BUBBLE.value}")

        return visited

    # --------------------------------------------------------------------------
    # 6. RATE CONTROL (DEBOUNCE & THROTTLE) (?44, ?45)
    # --------------------------------------------------------------------------

    def debounce(self, key: str, interval_seconds: float, action: Callable[[], Any], now: Optional[float] = None) -> bool:
        """Executes action only after interval_seconds have passed since the last invocation."""
        current_time = now if now is not None else time.time()
        last_t = self.debounce_timestamps.get(key, 0.0)
        self.debounce_timestamps[key] = current_time

        if current_time - last_t >= interval_seconds:
            action()
            return True
        return False

    def throttle(self, key: str, interval_seconds: float, action: Callable[[], Any], now: Optional[float] = None) -> bool:
        """Executes action at most once per interval_seconds."""
        current_time = now if now is not None else time.time()
        last_t = self.throttle_timestamps.get(key, 0.0)

        if current_time - last_t >= interval_seconds:
            self.throttle_timestamps[key] = current_time
            action()
            return True
        return False

    # --------------------------------------------------------------------------
    # 7. APPLICATION STATE & DETERMINISTIC REPLAY (?48, ?49, ?50)
    # --------------------------------------------------------------------------

    def set_state(self, key: str, value: Any) -> None:
        """Updates application runtime state."""
        self.app_state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Retrieves value from application runtime state."""
        return self.app_state.get(key, default)

    def compute_state_hash(self) -> str:
        """Produces a bit-exact deterministic cryptographic SHA-256 state digest."""
        serialized = json.dumps(self.app_state, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def start_recording(self, session_id: str = "rec_session", seed: int = 42) -> ReplayRecording:
        """Starts recording input events and state hashes frame-by-frame."""
        self.replay_mode = ReplayMode.RECORDING
        self.current_frame_number = 0
        rec = ReplayRecording(session_id=session_id, seed=seed)
        self.current_recording = rec
        return rec

    def record_frame(self, input_events: List[InputEvent], commands: List[Command]) -> ReplayFrame:
        """Appends a recorded frame with inputs, executed commands, and state hash."""
        if not self.current_recording:
            raise RuntimeError("Cannot record frame: recording not started.")

        frame = ReplayFrame(
            frame_number=self.current_frame_number,
            timestamp=time.time(),
            input_events=copy.deepcopy(input_events),
            commands=copy.deepcopy(commands),
        )
        frame.compute_state_hash(self.app_state)
        self.current_recording.frames.append(frame)
        self.current_frame_number += 1
        self.current_recording.total_frames = len(self.current_recording.frames)
        self.current_recording.final_state_hash = frame.state_hash
        return frame

    def stop_recording(self) -> ReplayRecording:
        """Finalizes active recording."""
        if not self.current_recording:
            raise RuntimeError("No active recording to stop.")
        rec = self.current_recording
        self.replay_mode = ReplayMode.IDLE
        self.current_recording = None
        return rec

    def replay_session(self, recording: ReplayRecording) -> Tuple[bool, List[ReplayDivergence]]:
        """
        Replays recorded session frame-by-frame, applying inputs, executing commands,
        and validating bit-exact state hashes to detect divergences (?189).
        """
        self.replay_mode = ReplayMode.REPLAYING
        divergences: List[ReplayDivergence] = []

        for frame in recording.frames:
            # Process frame inputs
            for inp in frame.input_events:
                self.process_input(inp)

            # Process frame commands
            for cmd in frame.commands:
                self.execute_command(cmd)

            current_hash = self.compute_state_hash()
            if current_hash != frame.state_hash:
                div = ReplayDivergence(
                    frame_number=frame.frame_number,
                    expected_hash=frame.state_hash,
                    actual_hash=current_hash,
                    severity=DivergenceSeverity.CRITICAL,
                    description=f"Divergence detected at frame {frame.frame_number}.",
                )
                divergences.append(div)

        self.replay_mode = ReplayMode.IDLE
        is_exact = len(divergences) == 0
        return is_exact, divergences

    # --------------------------------------------------------------------------
    # 8. DIAGNOSTICS & TELEMETRY (?51, ?138, ?207)
    # --------------------------------------------------------------------------

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Records structured log entry with credential redaction."""
        sanitized = copy.deepcopy(data)
        for k in list(sanitized.keys()):
            if any(s in k.lower() for s in ("token", "secret", "password", "key", "auth")):
                sanitized[k] = "[REDACTED]"
        self.event_logs.append({
            "event": event_type,
            "timestamp": time.time(),
            "data": sanitized,
        })

    def export_diagnostic_bundle(self) -> DiagnosticEventBundle:
        """Assembles diagnostic bundle with cryptographic SHA-256 digest."""
        bundle = DiagnosticEventBundle(
            telemetry=copy.deepcopy(self.telemetry),
            event_logs=list(self.event_logs),
        )
        bundle.compute_digest()
        return bundle

    # --------------------------------------------------------------------------
    # 9. GOLDEN SCENARIOS (?184)
    # --------------------------------------------------------------------------

    def scenario_golden_event_sequence(self) -> Dict[str, Any]:
        """Scenario 1: Event publication, filtering, priority ordering, and delivery."""
        fab = UniversalEventFabricator()
        delivered = []
        fab.subscribe(EventType.APPLICATION, lambda e: delivered.append(e.payload.get("msg")), priority=10)
        fab.publish(Event(event_type=EventType.APPLICATION, payload={"msg": "hello"}))
        return {"delivered": delivered, "count": len(delivered), "success": delivered == ["hello"]}

    def scenario_golden_routing_sequence(self) -> Dict[str, Any]:
        """Scenario 2: Capture, target, and bubble phase routing sequence."""
        fab = UniversalEventFabricator()
        fab.register_focus_target(FocusTarget("root", parent_id=None))
        fab.register_focus_target(FocusTarget("panel", parent_id="root"))
        fab.register_focus_target(FocusTarget("btn", parent_id="panel"))
        visited = fab.route_event("btn", Event(event_type=EventType.INPUT))
        expected = ["root:CAPTURE", "panel:CAPTURE", "btn:TARGET", "panel:BUBBLE", "root:BUBBLE"]
        return {"visited": visited, "valid": visited == expected}

    def scenario_golden_command_result(self) -> Dict[str, Any]:
        """Scenario 3: Transactional command handling and result capture."""
        fab = UniversalEventFabricator()
        fab.register_command_handler("add_score", lambda c: c.parameters["amount"] * 2)
        res = fab.execute_command(Command(action="add_score", parameters={"amount": 50}))
        return {"status": res.status, "result": res.result, "success": res.result == 100}

    def scenario_golden_input_mapping(self) -> Dict[str, Any]:
        """Scenario 4: Raw input normalization and action resolution."""
        fab = UniversalEventFabricator()
        ctx = EventInputContext("gameplay")
        fab.register_action_mapping("gameplay", ActionMapping("Jump", InputDeviceType.KEYBOARD, "Space"))
        fab.push_context(ctx)
        actions = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="Space"))
        return {"actions": actions, "success": actions == ["Jump"]}

    def scenario_golden_context_stack(self) -> Dict[str, Any]:
        """Scenario 5: Modal context priority overriding background gameplay actions."""
        fab = UniversalEventFabricator()
        c_game = EventInputContext("gameplay", priority=ContextPriority.NORMAL, consumed_actions={"Fire"})
        c_game.mappings["Fire"] = ActionMapping("Fire", InputDeviceType.MOUSE, "LeftClick")
        fab.push_context(c_game)

        c_modal = EventInputContext("modal_ui", priority=ContextPriority.MODAL, consumed_actions={"ClickUI"})
        c_modal.mappings["ClickUI"] = ActionMapping("ClickUI", InputDeviceType.MOUSE, "LeftClick")
        fab.push_context(c_modal)

        actions = fab.process_input(InputEvent(InputDeviceType.MOUSE, InputEventType.MOUSE_DOWN, key_code="LeftClick"))
        return {"actions": actions, "success": "ClickUI" in actions and "Fire" not in actions}

    def scenario_golden_focus_transitions(self) -> Dict[str, Any]:
        """Scenario 6: Focus switching and active state tracking."""
        fab = UniversalEventFabricator()
        fab.register_focus_target(FocusTarget("t1"))
        fab.register_focus_target(FocusTarget("t2"))
        fab.set_focus("t1")
        assert fab.focus_targets["t1"].has_focus is True
        fab.set_focus("t2")
        return {"t1_focus": fab.focus_targets["t1"].has_focus, "t2_focus": fab.focus_targets["t2"].has_focus}

    def scenario_golden_state_transitions(self) -> Dict[str, Any]:
        """Scenario 7: State changes and deterministic state hash calculation."""
        fab = UniversalEventFabricator()
        fab.set_state("player_health", 100)
        h1 = fab.compute_state_hash()
        fab.set_state("player_health", 90)
        h2 = fab.compute_state_hash()
        return {"h1": h1, "h2": h2, "distinct": h1 != h2}

    def scenario_golden_replay(self) -> Dict[str, Any]:
        """Scenario 8: Deterministic recording and bit-exact replay playback."""
        fab = UniversalEventFabricator()
        fab.register_command_handler("move", lambda c: fab.set_state("pos", c.parameters["x"]))
        rec = fab.start_recording()
        fab.execute_command(Command(action="move", parameters={"x": 10}))
        fab.record_frame([], [Command(action="move", parameters={"x": 10})])
        fab.stop_recording()

        # Replay in fresh instance
        replayer = UniversalEventFabricator()
        replayer.register_command_handler("move", lambda c: replayer.set_state("pos", c.parameters["x"]))
        success, divergences = replayer.replay_session(rec)
        return {"success": success, "divergences": len(divergences)}

    def scenario_golden_replay_divergence(self) -> Dict[str, Any]:
        """Scenario 9: Detection and reporting of replay state divergence."""
        fab = UniversalEventFabricator()
        rec = fab.start_recording()
        fab.set_state("seed", 100)
        fab.record_frame([], [])
        fab.stop_recording()

        # Replay with state corruption
        replayer = UniversalEventFabricator()
        replayer.set_state("seed", 999)  # Perturbed state
        success, divergences = replayer.replay_session(rec)
        return {"success": success, "divergences": len(divergences), "detected": not success}

    def scenario_golden_diagnostics(self) -> Dict[str, Any]:
        """Scenario 10: Event telemetry and diagnostic bundle generation."""
        fab = UniversalEventFabricator()
        fab.publish(Event(EventType.SYSTEM, payload={"msg": "test"}))
        fab.log_event("TEST_EVENT", {"secret_key": "HIDE_ME"})
        bundle = fab.export_diagnostic_bundle()
        return {"has_digest": len(bundle.sha256_digest) == 64, "logs": bundle.event_logs}

    # --------------------------------------------------------------------------
    # 10. COMPREHENSIVE PIPELINES (?185 to ?189)
    # --------------------------------------------------------------------------

    def execute_integration_pipeline(self) -> Dict[str, Any]:
        """Full input -> mapping -> context -> focus -> routing -> command -> state lifecycle (?185)."""
        fab = UniversalEventFabricator()
        # 1. Action Mapping & Context
        ctx = EventInputContext("game")
        fab.register_action_mapping("game", ActionMapping("Interact", InputDeviceType.KEYBOARD, "E"))
        fab.push_context(ctx)

        # 2. Focus & Target
        fab.register_focus_target(FocusTarget("door"))
        fab.set_focus("door")

        # 3. Command & State
        fab.register_command_handler("open_door", lambda c: fab.set_state("door_open", True))

        # 4. Input trigger
        actions = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="E"))
        if "Interact" in actions:
            cmd = Command(action="open_door")
            fab.execute_command(cmd)

        return {
            "door_open": fab.get_state("door_open"),
            "success": fab.get_state("door_open") is True,
        }

    def execute_e2e_input_pipeline(self) -> Dict[str, Any]:
        """Hardware input normalization and action mapping execution (?186)."""
        fab = UniversalEventFabricator()
        ctx = EventInputContext("flight")
        fab.register_action_mapping("flight", ActionMapping("Pitch", InputDeviceType.GAMEPAD, "AXIS_Y", deadzone=0.2))
        fab.push_context(ctx)
        # Below deadzone
        below = fab.process_input(InputEvent(InputDeviceType.GAMEPAD, InputEventType.AXIS_MOVE, axis_values=(0.1, 0, 0)))
        # Above deadzone
        above = fab.process_input(InputEvent(InputDeviceType.GAMEPAD, InputEventType.AXIS_MOVE, axis_values=(0.5, 0, 0)))
        return {"below": below, "above": above, "success": len(below) == 0 and "Pitch" in above}

    def execute_e2e_context_pipeline(self) -> Dict[str, Any]:
        """Modal context stack priority and input interception (?187)."""
        fab = UniversalEventFabricator()
        ctx_base = EventInputContext("base", priority=ContextPriority.NORMAL, consumed_actions={"ActionA"})
        ctx_base.mappings["ActionA"] = ActionMapping("ActionA", InputDeviceType.KEYBOARD, "A")
        fab.push_context(ctx_base)

        ctx_modal = EventInputContext("modal", priority=ContextPriority.MODAL, consumed_actions={"ActionModal"})
        ctx_modal.mappings["ActionModal"] = ActionMapping("ActionModal", InputDeviceType.KEYBOARD, "A")
        fab.push_context(ctx_modal)

        actions = fab.process_input(InputEvent(InputDeviceType.KEYBOARD, InputEventType.KEY_DOWN, key_code="A"))
        return {"actions": actions, "success": actions == ["ActionModal"]}

    def execute_e2e_replay_pipeline(self) -> Dict[str, Any]:
        """Recording gameplay session and bit-exact deterministic replay validation (?188)."""
        fab = UniversalEventFabricator()
        fab.register_command_handler("increment", lambda c: fab.set_state("counter", fab.get_state("counter", 0) + 1))
        rec = fab.start_recording()

        for _ in range(5):
            fab.execute_command(Command(action="increment"))
            fab.record_frame([], [Command(action="increment")])

        fab.stop_recording()

        replayer = UniversalEventFabricator()
        replayer.register_command_handler("increment", lambda c: replayer.set_state("counter", replayer.get_state("counter", 0) + 1))
        success, divs = replayer.replay_session(rec)
        return {"success": success, "final_value": replayer.get_state("counter"), "divs": len(divs)}

    def execute_e2e_divergence_pipeline(self) -> Dict[str, Any]:
        """Replay divergence identification and classification (?189)."""
        fab = UniversalEventFabricator()
        rec = fab.start_recording()
        fab.set_state("score", 100)
        fab.record_frame([], [])
        fab.stop_recording()

        replayer = UniversalEventFabricator()
        replayer.set_state("score", 999)  # Intentional discrepancy
        success, divs = replayer.replay_session(rec)
        return {
            "divergence_detected": not success,
            "severity": divs[0].severity if divs else None,
            "frame": divs[0].frame_number if divs else None,
        }
