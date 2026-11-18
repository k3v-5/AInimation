"""
UAF-81.83: Network Connection State Machine and Endpoint Management.
"""

from __future__ import annotations

from typing import Dict, Optional, Set

from ..models.definition import (
    BandwidthBudget,
    ConnectionId,
    ConnectionState,
    ConnectionStateError,
    DisconnectReason,
    InterestProfile,
)
from ..protocol.channel import ReliableOrderedChannel, UnreliableSequencedChannel
from ..replication.baseline import ClientBaselineTracker


# Valid state transitions
VALID_TRANSITIONS: Dict[ConnectionState, Set[ConnectionState]] = {
    ConnectionState.DISCONNECTED: {ConnectionState.CONNECTING},
    ConnectionState.CONNECTING: {ConnectionState.AUTHENTICATING, ConnectionState.DISCONNECTED, ConnectionState.DISCONNECTING},
    ConnectionState.AUTHENTICATING: {ConnectionState.CONNECTED, ConnectionState.DISCONNECTED, ConnectionState.DISCONNECTING},
    ConnectionState.CONNECTED: {ConnectionState.SYNCING, ConnectionState.ACTIVE, ConnectionState.DISCONNECTING, ConnectionState.DISCONNECTED},
    ConnectionState.SYNCING: {ConnectionState.ACTIVE, ConnectionState.DISCONNECTING, ConnectionState.DISCONNECTED},
    ConnectionState.ACTIVE: {ConnectionState.MIGRATING, ConnectionState.DISCONNECTING, ConnectionState.DISCONNECTED},
    ConnectionState.MIGRATING: {ConnectionState.ACTIVE, ConnectionState.DISCONNECTING, ConnectionState.DISCONNECTED},
    ConnectionState.DISCONNECTING: {ConnectionState.DISCONNECTED},
}


class NetworkConnection:
    """
    Encapsulates connection state, reliable/unreliable channels, baseline tracking,
    and bandwidth accounting for a network endpoint.
    """

    def __init__(
        self,
        connection_id: str,
        client_id: str,
        rto_ticks: int = 5,
        max_history_ticks: int = 120,
    ):
        self.connection_id = connection_id
        self.client_id = client_id
        self.state: ConnectionState = ConnectionState.DISCONNECTED
        self.disconnect_reason: Optional[DisconnectReason] = None

        # Channels
        self.reliable_channel = ReliableOrderedChannel(rto_ticks=rto_ticks)
        self.unreliable_channel = UnreliableSequencedChannel()

        # Replication Baseline
        self.baseline_tracker = ClientBaselineTracker(
            connection_id=connection_id,
            max_history_ticks=max_history_ticks,
        )

        # Interest Profile
        self.interest_profile = InterestProfile()

        # Telemetry & Diagnostics
        self.rtt_ms: float = 20.0
        self.last_activity_tick: int = 0
        self.bytes_sent: int = 0
        self.bytes_received: int = 0
        self.packets_sent: int = 0
        self.packets_received: int = 0

    def transition_to(self, new_state: ConnectionState) -> None:
        """
        Transition connection state machine.
        Raises ConnectionStateError if the transition is illegal.
        """
        allowed = VALID_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            raise ConnectionStateError(
                f"Illegal connection state transition from {self.state.value} to {new_state.value}"
            )
        self.state = new_state

    def disconnect(self, reason: DisconnectReason = DisconnectReason.CLIENT_REQUEST) -> None:
        """Disconnect this connection with a stated reason."""
        self.disconnect_reason = reason
        self.state = ConnectionState.DISCONNECTED

    def is_active(self) -> bool:
        """Check if connection is active and ready for data transfer."""
        return self.state in (ConnectionState.CONNECTED, ConnectionState.SYNCING, ConnectionState.ACTIVE)
