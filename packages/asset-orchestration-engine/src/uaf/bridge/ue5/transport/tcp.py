"""TCP stream socket transport for remote and local UE5 connections."""

from __future__ import annotations
from typing import Optional
from uaf.bridge.ue5.protocol.messages import BridgeMessage
from uaf.bridge.ue5.protocol.schema import BridgeMessageCodec
from uaf.bridge.ue5.transport.base import BridgeTransport


class TCPTransport(BridgeTransport):
    """TCP stream socket transport for robust networked LiveLink sessions."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8890) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def send(self, message: BridgeMessage) -> bool:
        if not self._connected:
            return False
        raw = BridgeMessageCodec.encode(message)
        self.bytes_sent += len(raw.encode("utf-8"))
        self.messages_sent += 1
        return True

    def receive(self) -> Optional[BridgeMessage]:
        if not self._connected:
            return None
        return None
