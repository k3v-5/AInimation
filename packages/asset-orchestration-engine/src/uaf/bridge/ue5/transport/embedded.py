"""In-memory paired loopback transport with failure injection capabilities."""

from __future__ import annotations
import copy
from queue import Empty, Queue
from typing import Any, Optional, Tuple, Union
from uaf.bridge.ue5.protocol.messages import BridgeMessage
from uaf.bridge.ue5.transport.base import BridgeTransport


class EmbeddedTransport(BridgeTransport):
    """Zero-overhead in-memory transport connecting UAF and UE5 simulated endpoints."""

    def __init__(
        self,
        inbound_queue: Queue[Any],
        outbound_queue: Queue[Any],
        name: str = "EmbeddedTransport",
    ) -> None:
        super().__init__()
        self.inbound = inbound_queue
        self.outbound = outbound_queue
        self.name = name
        self._connected = False

        # Failure injection flags
        self.drop_next_n: int = 0
        self.duplicate_next: bool = False
        self.reorder_buffer: Optional[Any] = None

    @property
    def transport_type(self) -> str:
        return "Embedded"

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def has_pending_messages(self) -> bool:
        return not self.inbound.empty()

    def send(self, message: Union[BridgeMessage, bytes, str]) -> bool:
        if not self._connected:
            return False

        # Failure injection: packet drop
        if self.drop_next_n > 0:
            self.drop_next_n -= 1
            return True

        # Deep copy message to avoid cross-endpoint state mutation
        cloned = copy.deepcopy(message)

        self.outbound.put(cloned)
        self.messages_sent += 1
        payload_size = len(cloned) if isinstance(cloned, (bytes, str)) else len(str(getattr(cloned, 'payload', '')))
        self.bytes_sent += payload_size

        # Failure injection: duplication
        if self.duplicate_next:
            self.duplicate_next = False
            self.outbound.put(copy.deepcopy(cloned))

        return True

    def receive(self) -> Optional[Union[BridgeMessage, bytes, str]]:
        if not self._connected:
            return None
        try:
            msg = self.inbound.get_nowait()
            self.messages_received += 1
            payload_size = len(msg) if isinstance(msg, (bytes, str)) else len(str(getattr(msg, 'payload', '')))
            self.bytes_received += payload_size
            return msg
        except Empty:
            return None

    @classmethod
    def create_pair(cls) -> Tuple[EmbeddedTransport, EmbeddedTransport]:
        """Creates a paired bidirectional channel: (UAF endpoint, UE5 endpoint)."""
        q_uaf_to_ue = Queue[Any]()
        q_ue_to_uaf = Queue[Any]()

        uaf_side = cls(inbound_queue=q_ue_to_uaf, outbound_queue=q_uaf_to_ue, name="UAF_Endpoint")
        ue_side = cls(inbound_queue=q_uaf_to_ue, outbound_queue=q_ue_to_uaf, name="UE5_Endpoint")
        return uaf_side, ue_side
