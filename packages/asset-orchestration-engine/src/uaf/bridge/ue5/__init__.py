"""Universal Deep Unreal Engine 5 LiveLink & Interoperability Bridge package."""

from uaf.bridge.ue5.bridge import UE5Bridge
from uaf.bridge.ue5.protocol.messages import (
    AuthorityModel,
    BridgeMessage,
    BridgeMessageType,
    ChangeEvent,
    SyncState,
    UpdatePriority,
)
from uaf.bridge.ue5.protocol.capabilities import UE5Capabilities, UE5Feature
from uaf.bridge.ue5.protocol.versioning import BridgeProtocolVersion, HandshakeResult
from uaf.bridge.ue5.transport.base import BridgeTransport
from uaf.bridge.ue5.transport.embedded import EmbeddedTransport
from uaf.bridge.ue5.transport.ipc import IPCTransport
from uaf.bridge.ue5.transport.tcp import TCPTransport
from uaf.bridge.ue5.transport.websocket import WebSocketTransport
from uaf.bridge.ue5.sync.session import BridgeSession, ConnectionState
from uaf.bridge.ue5.sync.revisions import RevisionVector
from uaf.bridge.ue5.sync.patches import PatchOperation, StatePatch, apply_patch, diff_dict
from uaf.bridge.ue5.sync.snapshots import BridgeSnapshot
from uaf.bridge.ue5.sync.conflicts import ConflictDetector, ConflictPolicy, SyncConflict
from uaf.bridge.ue5.sync.transactions import BridgeTransaction, TransactionManager
from uaf.bridge.ue5.registry.objects import UE5ObjectEntry, UE5ObjectRegistry
from uaf.bridge.ue5.registry.assets import UE5AssetEntry, UE5AssetRegistry
from uaf.bridge.ue5.recovery.reconnect import ReconnectionManager
from uaf.bridge.ue5.recovery.repair import BridgeRepairEngine, OrphanPolicy, OrphanReport
from uaf.bridge.ue5.recovery.quarantine import QuarantinedItem, QuarantineManager
from uaf.bridge.ue5.diagnostics.errors import UE5ErrorCode, UE5ErrorContext, UE5BridgeError
from uaf.bridge.ue5.diagnostics.traces import BridgeSpan, BridgeTelemetryCollector
from uaf.bridge.ue5.diagnostics.audit import AuditEntry, LiveLinkAuditTrail
from uaf.bridge.ue5.validation.compatibility import EngineCompatibilityValidator, CompatibilityReport
from uaf.bridge.ue5.validation.determinism import DeterminismChecker, StateDivergenceReport
from uaf.bridge.ue5.validation.certification import LiveLinkCertificationSuite, CertificationReport

__all__ = [
    "UE5Bridge",
    "AuthorityModel",
    "BridgeMessage",
    "BridgeMessageType",
    "ChangeEvent",
    "SyncState",
    "UpdatePriority",
    "UE5Capabilities",
    "UE5Feature",
    "BridgeProtocolVersion",
    "HandshakeResult",
    "BridgeTransport",
    "EmbeddedTransport",
    "IPCTransport",
    "TCPTransport",
    "WebSocketTransport",
    "BridgeSession",
    "ConnectionState",
    "RevisionVector",
    "PatchOperation",
    "StatePatch",
    "apply_patch",
    "diff_dict",
    "BridgeSnapshot",
    "ConflictDetector",
    "ConflictPolicy",
    "SyncConflict",
    "BridgeTransaction",
    "TransactionManager",
    "UE5ObjectEntry",
    "UE5ObjectRegistry",
    "UE5AssetEntry",
    "UE5AssetRegistry",
    "ReconnectionManager",
    "BridgeRepairEngine",
    "OrphanPolicy",
    "OrphanReport",
    "QuarantinedItem",
    "QuarantineManager",
    "UE5ErrorCode",
    "UE5ErrorContext",
    "UE5BridgeError",
    "BridgeSpan",
    "BridgeTelemetryCollector",
    "AuditEntry",
    "LiveLinkAuditTrail",
    "EngineCompatibilityValidator",
    "CompatibilityReport",
    "DeterminismChecker",
    "StateDivergenceReport",
    "LiveLinkCertificationSuite",
    "CertificationReport",
]
