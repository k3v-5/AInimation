"""
Universal Application State, Event Bus, Message Dispatch, Command System,
Input Abstraction, Action Mapping, Context Stack, Focus, Priority,
Routing, Replay & Deterministic Event Processing Models (UAF-81.65).
"""

from __future__ import annotations
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class EventType(str, Enum):
    """Authoritative event classifications (?26)."""
    APPLICATION = "APPLICATION"
    INPUT = "INPUT"
    SYSTEM = "SYSTEM"
    COMMAND = "COMMAND"
    TELEMETRY = "TELEMETRY"
    CUSTOM = "CUSTOM"


class EventPriority(int, Enum):
    """Event dispatch priority tiers (?39). Higher number = higher priority."""
    BACKGROUND = 0
    LOW = 10
    NORMAL = 20
    HIGH = 30
    IMMEDIATE = 40


class InputDeviceType(str, Enum):
    """Physical input device categories (?34)."""
    KEYBOARD = "KEYBOARD"
    MOUSE = "MOUSE"
    GAMEPAD = "GAMEPAD"
    TOUCH = "TOUCH"
    VR = "VR"


class InputEventType(str, Enum):
    """Hardware input event actions (?35)."""
    KEY_DOWN = "KEY_DOWN"
    KEY_UP = "KEY_UP"
    MOUSE_MOVE = "MOUSE_MOVE"
    MOUSE_DOWN = "MOUSE_DOWN"
    MOUSE_UP = "MOUSE_UP"
    AXIS_MOVE = "AXIS_MOVE"
    TOUCH_START = "TOUCH_START"
    TOUCH_MOVE = "TOUCH_MOVE"
    TOUCH_END = "TOUCH_END"


class DispatchMode(str, Enum):
    """Event delivery dispatch modes (?27)."""
    SYNC = "SYNC"
    ASYNC = "ASYNC"
    QUEUED = "QUEUED"
    IMMEDIATE = "IMMEDIATE"


class OverflowPolicy(str, Enum):
    """Queue backpressure and overflow handling policies (?47, ?191)."""
    DROP_OLDEST = "DROP_OLDEST"
    DROP_NEWEST = "DROP_NEWEST"
    BLOCK = "BLOCK"
    ERROR = "ERROR"


class RoutingPhase(str, Enum):
    """Hierarchical event propagation phases (?40, ?41, ?42)."""
    CAPTURE = "CAPTURE"
    TARGET = "TARGET"
    BUBBLE = "BUBBLE"


class ReplayMode(str, Enum):
    """Deterministic replay recording and execution states (?48, ?49)."""
    IDLE = "IDLE"
    RECORDING = "RECORDING"
    REPLAYING = "REPLAYING"
    VERIFYING = "VERIFYING"


class DivergenceSeverity(str, Enum):
    """Divergence severity classifications during replay verification (?189)."""
    NONE = "NONE"
    MINOR = "MINOR"
    CRITICAL = "CRITICAL"


class CommandStatus(str, Enum):
    """Transactional command execution lifecycle states (?31, ?32)."""
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ContextPriority(int, Enum):
    """Input context layer priorities (?37)."""
    LOW = 10
    NORMAL = 20
    HIGH = 30
    MODAL = 40


class RateControlStrategy(str, Enum):
    """Rate control throttling and debouncing strategies (?44, ?45)."""
    NONE = "NONE"
    DEBOUNCE = "DEBOUNCE"
    THROTTLE = "THROTTLE"


# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class Event:
    """Authoritative event envelope (?25)."""
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    source: str = "system"
    handled: bool = False
    cancelled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "handled": self.handled,
            "cancelled": self.cancelled,
            "payload": self.payload,
        }


@dataclass
class Message:
    """Channel-based message packet (?29, ?30)."""
    channel: str
    payload: Any
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = "anonymous"
    recipient: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "channel": self.channel,
            "sender": self.sender,
            "recipient": self.recipient,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


@dataclass
class Command:
    """Transactional intent descriptor (?31)."""
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = "client"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "action": self.action,
            "parameters": self.parameters,
            "sender": self.sender,
            "timestamp": self.timestamp,
        }


@dataclass
class EventCommandResult:
    """Execution result of a command (?32)."""
    command_id: str
    status: CommandStatus
    result: Any = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "status": self.status.value,
            "result": self.result,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
        }

# Internal alias
CommandResult = EventCommandResult


@dataclass
class InputEvent:
    """Hardware-normalized raw user input event (?33, ?34, ?35)."""
    device: InputDeviceType
    event_type: InputEventType
    key_code: str = ""
    axis_values: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    normalized_value: float = 1.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device": self.device.value,
            "event_type": self.event_type.value,
            "key_code": self.key_code,
            "axis_values": list(self.axis_values),
            "normalized_value": self.normalized_value,
            "timestamp": self.timestamp,
        }


@dataclass
class ActionMapping:
    """High-level gameplay or UI action mapped from hardware input (?36)."""
    action_name: str
    device: InputDeviceType
    input_trigger: str
    deadzone: float = 0.1
    sensitivity: float = 1.0
    modifier_keys: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_name": self.action_name,
            "device": self.device.value,
            "input_trigger": self.input_trigger,
            "deadzone": self.deadzone,
            "sensitivity": self.sensitivity,
            "modifier_keys": self.modifier_keys,
        }


@dataclass
class EventInputContext:
    """Layer in the active context stack (?37)."""
    context_id: str
    priority: ContextPriority = ContextPriority.NORMAL
    active: bool = True
    consumed_actions: Set[str] = field(default_factory=set)
    mappings: Dict[str, ActionMapping] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "priority": self.priority.value,
            "active": self.active,
            "consumed_actions": list(self.consumed_actions),
            "mapping_count": len(self.mappings),
        }

# Internal alias
InputContext = EventInputContext


@dataclass
class FocusTarget:
    """UI or gameplay focusable target in the hierarchy (?38, ?40)."""
    target_id: str
    focusable: bool = True
    priority: int = 0
    parent_id: Optional[str] = None
    has_focus: bool = False


@dataclass
class ReplayFrame:
    """Deterministic tick recording frame (?48, ?50)."""
    frame_number: int
    timestamp: float
    input_events: List[InputEvent] = field(default_factory=list)
    commands: List[Command] = field(default_factory=list)
    state_hash: str = ""

    def compute_state_hash(self, state_dict: Dict[str, Any]) -> str:
        serialized = json.dumps(state_dict, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.state_hash = h
        return h

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "input_count": len(self.input_events),
            "command_count": len(self.commands),
            "state_hash": self.state_hash,
        }


@dataclass
class ReplayRecording:
    """Full deterministic gameplay or session recording (?49)."""
    recording_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    seed: int = 42
    total_frames: int = 0
    frames: List[ReplayFrame] = field(default_factory=list)
    final_state_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recording_id": self.recording_id,
            "session_id": self.session_id,
            "seed": self.seed,
            "total_frames": self.total_frames,
            "final_state_hash": self.final_state_hash,
        }


@dataclass
class ReplayDivergence:
    """Divergence report during replay verification (?189)."""
    frame_number: int
    expected_hash: str
    actual_hash: str
    severity: DivergenceSeverity
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_number": self.frame_number,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "severity": self.severity.value,
            "description": self.description,
        }


@dataclass
class EventTelemetry:
    """Performance, throughput, and error metrics for event processing (?51)."""
    total_dispatched: int = 0
    queue_depth: int = 0
    dropped_events: int = 0
    avg_latency_ms: float = 0.0
    handler_errors: int = 0
    commands_executed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_dispatched": self.total_dispatched,
            "queue_depth": self.queue_depth,
            "dropped_events": self.dropped_events,
            "avg_latency_ms": self.avg_latency_ms,
            "handler_errors": self.handler_errors,
            "commands_executed": self.commands_executed,
        }


@dataclass
class DiagnosticEventBundle:
    """Complete diagnostic bundle for event and command subsystems."""
    bundle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    telemetry: EventTelemetry = field(default_factory=EventTelemetry)
    recordings: List[ReplayRecording] = field(default_factory=list)
    event_logs: List[Dict[str, Any]] = field(default_factory=list)
    sha256_digest: str = ""

    def compute_digest(self) -> str:
        data = {
            "bundle_id": self.bundle_id,
            "timestamp": self.timestamp,
            "total_dispatched": self.telemetry.total_dispatched,
            "log_count": len(self.event_logs),
        }
        serialized = json.dumps(data, sort_keys=True)
        self.sha256_digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return self.sha256_digest


@dataclass
class EventDiagnosticReport:
    """Validation report for events, commands, and routing configurations."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
