"""UE5 Bridge Protocol definitions, schemas, versioning, and capabilities."""

from uaf.bridge.ue5.protocol.messages import (
    BridgeMessageType,
    AuthorityModel,
    SyncState,
    UpdatePriority,
    ChangeEvent,
    BridgeMessage,
)
from uaf.bridge.ue5.protocol.capabilities import (
    UE5Feature,
    UE5Capabilities,
)
from uaf.bridge.ue5.protocol.versioning import (
    BridgeProtocolVersion,
    VersionMismatchError,
    HandshakeResult,
    CURRENT_BRIDGE_PROTOCOL_VERSION,
)
from uaf.bridge.ue5.protocol.schema import (
    BridgeSchemaValidationError,
    BridgeMessageCodec,
)

__all__ = [
    "BridgeMessageType",
    "AuthorityModel",
    "SyncState",
    "UpdatePriority",
    "ChangeEvent",
    "BridgeMessage",
    "UE5Feature",
    "UE5Capabilities",
    "BridgeProtocolVersion",
    "VersionMismatchError",
    "HandshakeResult",
    "CURRENT_BRIDGE_PROTOCOL_VERSION",
    "BridgeSchemaValidationError",
    "BridgeMessageCodec",
]
