"""Local Inter-Process Communication (IPC) transport for UE5 editor process."""

from __future__ import annotations
from typing import Optional
from uaf.bridge.ue5.protocol.messages import BridgeMessage
from uaf.bridge.ue5.protocol.schema import BridgeMessageCodec
from uaf.bridge.ue5.transport.base import BridgeTransport


class IPCTransport(BridgeTransport):
    """IPC transport abstraction utilizing local pipes or shared memory."""

    def __init__(self, pipe_name: str = "UAF_UE5_LiveLink_Pipe") -> None:
        super().__init__()
        self.pipe_name = pipe_name
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
