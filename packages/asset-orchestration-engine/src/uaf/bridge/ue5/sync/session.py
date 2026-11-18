"""LiveLink bridge session state machine and heartbeat management."""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uaf.bridge.ue5.protocol.versioning import BridgeProtocolVersion


class ConnectionState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    RECONNECTING = "RECONNECTING"
    FAILED = "FAILED"


@dataclass
class BridgeSession:
    """Manages active connection lifecycle, heartbeats, and timeouts."""
    session_id: str = field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:12]}")
    state: ConnectionState = ConnectionState.DISCONNECTED
    heartbeat_interval_s: float = 1.0
    timeout_s: float = 5.0
    last_heartbeat_s: float = field(default_factory=time.perf_counter)
    last_ack_s: float = field(default_factory=time.perf_counter)
    retry_count: int = 0
    max_retries: int = 5
    capabilities: Any = None
    protocol_version: BridgeProtocolVersion = field(default_factory=BridgeProtocolVersion)
    metadata: Dict[str, Any] = field(default_factory=dict)
    change_events: List[Any] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        return self.state == ConnectionState.CONNECTED

    def connect(self) -> None:
        self.transition_to(ConnectionState.CONNECTED)

    def disconnect(self) -> None:
        self.transition_to(ConnectionState.DISCONNECTED)

    def mark_handshake_complete(self, capabilities: Any) -> None:
        self.capabilities = capabilities

    def record_change(self, change_event: Any) -> None:
        self.change_events.append(change_event)

    def transition_to(self, new_state: ConnectionState) -> None:
        self.state = new_state
        if new_state == ConnectionState.CONNECTED:
            self.retry_count = 0
            self.last_ack_s = time.perf_counter()

    def record_pulse(self) -> None:
        self.last_heartbeat_s = time.perf_counter()

    def record_ack(self) -> None:
        now = time.perf_counter()
        self.last_ack_s = now
        self.last_heartbeat_s = now
        if self.state in (ConnectionState.CONNECTING, ConnectionState.DEGRADED, ConnectionState.RECONNECTING):
            self.transition_to(ConnectionState.CONNECTED)

    def check_health(self, current_time_s: Optional[float] = None) -> ConnectionState:
        now = current_time_s if current_time_s is not None else time.perf_counter()
        elapsed = now - self.last_ack_s

        if self.state == ConnectionState.CONNECTED:
            if elapsed > self.timeout_s:
                self.transition_to(ConnectionState.DEGRADED)
        elif self.state == ConnectionState.DEGRADED:
            if elapsed > (self.timeout_s * 2.0):
                self.transition_to(ConnectionState.RECONNECTING)
        return self.state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "is_active": self.is_active,
            "last_heartbeat_s": self.last_heartbeat_s,
            "last_ack_s": self.last_ack_s,
            "retry_count": self.retry_count,
            "metadata": self.metadata,
        }
