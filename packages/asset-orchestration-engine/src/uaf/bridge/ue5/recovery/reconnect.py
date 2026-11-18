"""Resilient connection recovery, outbound freezing, and delta queue replay."""

from __future__ import annotations
import time
from typing import Callable, List, Optional
from uaf.bridge.ue5.protocol.messages import BridgeMessage, BridgeMessageType
from uaf.bridge.ue5.sync.session import BridgeSession, ConnectionState
from uaf.bridge.ue5.transport.base import BridgeTransport


class ReconnectionManager:
    """Manages reconnection workflows, outbound mutation freezing, and delta replay."""

    def __init__(
        self,
        transport: Optional[BridgeTransport] = None,
        session: Optional[BridgeSession] = None,
        max_reconnect_attempts: int = 5,
        backoff_base_s: float = 0.5,
    ) -> None:
        self.transport = transport
        self.session = session
        self.max_reconnect_attempts = max_reconnect_attempts
        self.backoff_base_s = backoff_base_s
        self.frozen_delta_queue: List[BridgeMessage] = []
        self.is_frozen: bool = False
        self.reconnect_count: int = 0

    def record_reconnect(self) -> None:
        self.reconnect_count += 1

    def on_connection_lost(self) -> None:
        """Freezes outbound mutations to prevent state drift during disconnect."""
        self.is_frozen = True
        if self.session:
            self.session.transition_to(ConnectionState.DISCONNECTED)

    def enqueue_mutation(self, message: BridgeMessage) -> bool:
        """If frozen, queues mutation for later delta replay. Otherwise returns False."""
        if self.is_frozen:
            self.frozen_delta_queue.append(message)
            return True
        return False

    def attempt_reconnect(self, handshake_callback: Optional[Callable[[], bool]] = None) -> bool:
        """Executes reconnection sequence: connect -> handshake -> replay -> resume."""
        if self.session:
            self.session.transition_to(ConnectionState.RECONNECTING)

        if not self.transport:
            return False

        for attempt in range(1, self.max_reconnect_attempts + 1):
            connected = self.transport.connect()
            if connected:
                # Perform handshake
                if handshake_callback:
                    try:
                        ok = handshake_callback()
                        if not ok:
                            continue
                    except Exception:
                        continue

                # Reconnect successful
                if self.session:
                    self.session.transition_to(ConnectionState.CONNECTED)
                self.replay_deltas()
                self.is_frozen = False
                self.record_reconnect()
                return True

            # Exponential backoff
            time.sleep(self.backoff_base_s * (2 ** (attempt - 1)))

        if self.session:
            self.session.transition_to(ConnectionState.FAILED)
        return False

    def replay_deltas(self) -> int:
        """Flushes and transmits queued mutations in strict sequence."""
        replayed_count = 0
        while self.frozen_delta_queue:
            msg = self.frozen_delta_queue.pop(0)
            if self.transport:
                self.transport.send(msg)
            replayed_count += 1
        return replayed_count

    def clear(self) -> None:
        self.frozen_delta_queue.clear()
        self.is_frozen = False
