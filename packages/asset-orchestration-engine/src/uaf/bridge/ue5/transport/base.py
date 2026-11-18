"""Abstract base transport interface for the UAF ↔ UE5 bridge."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from uaf.bridge.ue5.protocol.messages import BridgeMessage


class BridgeTransport(ABC):
    """Decoupled transport abstraction supporting local IPC, network sockets, or in-memory queues."""

    def __init__(self) -> None:
        self.bytes_sent: int = 0
        self.bytes_received: int = 0
        self.messages_sent: int = 0
        self.messages_received: int = 0

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def send(self, message: BridgeMessage) -> bool:
        pass

    @abstractmethod
    def receive(self) -> Optional[BridgeMessage]:
        pass

    def poll(self, max_messages: int = 100) -> List[BridgeMessage]:
        messages: List[BridgeMessage] = []
        for _ in range(max_messages):
            msg = self.receive()
            if msg is None:
                break
            messages.append(msg)
        return messages
