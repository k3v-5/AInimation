"""WebSocket transport for remote tooling, web dashboards, and inspection panels."""

from __future__ import annotations
from typing import Optional
from uaf.bridge.ue5.protocol.messages import BridgeMessage
from uaf.bridge.ue5.protocol.schema import BridgeMessageCodec
from uaf.bridge.ue5.transport.base import BridgeTransport


class WebSocketTransport(BridgeTransport):
    """WebSocket transport for browser inspectors and remote web tooling."""

    def __init__(self, uri: str = "ws://127.0.0.1:8891/livelink") -> None:
        super().__init__()
        self.uri = uri
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
