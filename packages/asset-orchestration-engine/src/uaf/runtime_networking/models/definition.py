"""
UAF-81.83: Domain Models, Identifiers, Enums, and Exception Contracts
for Universal Runtime Networking, Replication, State Synchronization & Multiplayer Engine.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
import enum
import hashlib
import json
import math
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

Vec3 = Tuple[float, float, float]


# ==============================================================================
# 1. NUMERIC SANITY AND ANTI-CHEAT CHECKS
# ==============================================================================

def ensure_finite_float(val: float, context: str = "") -> float:
    """Validate that a float value is finite (not NaN, not +Inf, not -Inf)."""
    if math.isnan(val) or math.isinf(val):
        raise NumericSecurityError(f"Non-finite float detected in {context}: {val}")
    return float(val)


def ensure_finite_vec3(v: Sequence[float], context: str = "") -> Vec3:
    """Validate that a 3D vector contains only finite floats."""
    if len(v) != 3:
        raise NumericSecurityError(f"Vec3 must have exactly 3 coordinates in {context}, got {len(v)}")
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    if math.isnan(x) or math.isinf(x) or math.isnan(y) or math.isinf(y) or math.isnan(z) or math.isinf(z):
        raise NumericSecurityError(f"Non-finite coordinate in Vec3 ({x}, {y}, {z}) in {context}")
    return (x, y, z)


# ==============================================================================
# 2. ENUMS
# ==============================================================================

class NetworkMode(str, enum.Enum):
    DEDICATED_SERVER = "DEDICATED_SERVER"
    LISTEN_SERVER = "LISTEN_SERVER"
    CLIENT = "CLIENT"
    HEADLESS_SERVER = "HEADLESS_SERVER"
    REPLAY = "REPLAY"
    OFFLINE = "OFFLINE"


class AuthorityType(str, enum.Enum):
    SERVER_AUTHORITY = "SERVER_AUTHORITY"
    CLIENT_PREDICTED = "CLIENT_PREDICTED"
    SHARED = "SHARED"
    NONE = "NONE"


class OwnershipType(str, enum.Enum):
    CLIENT_OWNED = "CLIENT_OWNED"
    SERVER_OWNED = "SERVER_OWNED"
    UNOWNED = "UNOWNED"


class ReplicationPolicy(str, enum.Enum):
    ALWAYS = "ALWAYS"
    OWNER_ONLY = "OWNER_ONLY"
    RELEVANT = "RELEVANT"
    INITIAL_ONLY = "INITIAL_ONLY"
    DORMANT = "DORMANT"
    MANUAL = "MANUAL"


class ChannelType(str, enum.Enum):
    RELIABLE_ORDERED = "RELIABLE_ORDERED"
    UNRELIABLE_SEQUENCED = "UNRELIABLE_SEQUENCED"


class ConnectionState(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    AUTHENTICATING = "AUTHENTICATING"
    CONNECTED = "CONNECTED"
    SYNCING = "SYNCING"
    ACTIVE = "ACTIVE"
    MIGRATING = "MIGRATING"
    DISCONNECTING = "DISCONNECTING"


class RPCType(str, enum.Enum):
    RELIABLE_SERVER = "RELIABLE_SERVER"
    RELIABLE_CLIENT = "RELIABLE_CLIENT"
    UNRELIABLE_SERVER = "UNRELIABLE_SERVER"
    UNRELIABLE_CLIENT = "UNRELIABLE_CLIENT"


class NetworkPriority(int, enum.Enum):
    CRITICAL = 4
    HIGH = 3
    NORMAL = 2
    LOW = 1
    BACKGROUND = 0


class DormancyState(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DORMANT = "DORMANT"


class DisconnectReason(str, enum.Enum):
    CLIENT_REQUEST = "CLIENT_REQUEST"
    SERVER_SHUTDOWN = "SERVER_SHUTDOWN"
    TIMEOUT = "TIMEOUT"
    DESYNC = "DESYNC"
    RATE_LIMIT = "RATE_LIMIT"
    PROTOCOL_MISMATCH = "PROTOCOL_MISMATCH"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"


# ==============================================================================
# 3. EXCEPTIONS
# ==============================================================================

class NetworkError(Exception):
    """Base exception for networking runtime errors."""
    pass


class PacketValidationError(NetworkError):
    """Raised when a packet header, checksum, or structure is invalid."""
    pass


class DesyncError(NetworkError):
    """Raised when client prediction and server authoritative state cannot be reconciled."""
    pass


class RateLimitExceededError(NetworkError):
    """Raised when a connection exceeds permitted bandwidth, packet, or RPC quotas."""
    pass


class InvalidAuthorityError(NetworkError):
    """Raised when an unprivileged client attempts to mutate server-authoritative state."""
    pass


class SchemaVersionMismatchError(NetworkError):
    """Raised when packet or world protocol version does not match."""
    pass


class BaselineInvalidatedError(NetworkError):
    """Raised when delta compression attempts to compute against an unacknowledged baseline."""
    pass


class ConnectionStateError(NetworkError):
    """Raised when an illegal connection state transition is attempted."""
    pass


class NumericSecurityError(NetworkError):
    """Raised when a NaN or Infinity is detected in incoming client inputs or packets."""
    pass


class RollbackError(NetworkError):
    """Raised when server-side rollback or resimulation fails."""
    pass


# ==============================================================================
# 4. IDENTIFIERS & DATACLASSES
# ==============================================================================

@dataclass(frozen=True, order=True)
class NetworkEntityId:
    namespace: int
    value: int

    def __str__(self) -> str:
        return f"NetId({self.namespace}:{self.value})"


@dataclass(frozen=True)
class ConnectionId:
    value: str


@dataclass(frozen=True)
class ClientId:
    value: str


@dataclass(frozen=True)
class NetworkSession:
    session_id: str
    protocol_version: int = 1
    world_revision: int = 1
    tick_rate: int = 60
    server_id: str = "srv_dedicated_01"


@dataclass(frozen=True)
class ReplicatedProperty:
    property_id: str
    type_id: str
    authority: AuthorityType = AuthorityType.SERVER_AUTHORITY
    quantization: str = "none"
    condition: str = "always"


@dataclass(frozen=True)
class ReplicatedComponent:
    component_id: str
    replication_policy: ReplicationPolicy = ReplicationPolicy.RELEVANT
    authority: AuthorityType = AuthorityType.SERVER_AUTHORITY
    priority: int = 100


@dataclass(frozen=True)
class EntitySnapshot:
    net_id: NetworkEntityId
    owner_id: Optional[str]
    properties: Dict[str, Any]
    revision: int = 0


@dataclass(frozen=True)
class WorldSnapshot:
    server_tick: int
    snapshot_id: int
    world_revision: int
    entities: Tuple[EntitySnapshot, ...]


@dataclass(frozen=True)
class PacketHeader:
    protocol_version: int
    session_id: str
    connection_id: str
    channel: ChannelType
    sequence: int
    ack: int
    ack_bits: int
    server_tick: int
    payload_size: int
    flags: int = 0


@dataclass(frozen=True)
class Packet:
    header: PacketHeader
    payload: bytes


@dataclass(frozen=True)
class InputCommand:
    client_tick: int
    sequence: int
    buttons: int = 0
    axes: Tuple[float, ...] = (0.0, 0.0)
    actions: Tuple[str, ...] = ()

    def __post_init__(self):
        for ax in self.axes:
            ensure_finite_float(ax, f"InputCommand(seq={self.sequence}).axis")


@dataclass(frozen=True)
class RPCMessage:
    operation_id: str
    target_net_id: NetworkEntityId
    rpc_name: str
    rpc_type: RPCType
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InterestProfile:
    position: Vec3 = (0.0, 0.0, 0.0)
    radius: float = 100.0
    priority: int = 0

    def __post_init__(self):
        ensure_finite_vec3(self.position, "InterestProfile.position")
        ensure_finite_float(self.radius, "InterestProfile.radius")


@dataclass(frozen=True)
class BandwidthBudget:
    bytes_per_tick: int = 65536
    max_packets_per_tick: int = 16
    reliable_bytes_per_tick: int = 32768
    unreliable_bytes_per_tick: int = 32768


@dataclass
class NetworkMetrics:
    connected_clients: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    reliable_sent: int = 0
    reliable_retransmits: int = 0
    unreliable_dropped: int = 0
    packet_loss_count: int = 0
    duplicates_detected: int = 0
    out_of_order_count: int = 0
    avg_rtt_ms: float = 0.0
    snapshots_sent: int = 0
    prediction_ticks: int = 0
    reconciliation_count: int = 0
    rollback_count: int = 0
    desync_count: int = 0
    full_resync_count: int = 0


@dataclass(frozen=True)
class NetworkSnapshot:
    server_tick: int
    world_revision: int
    active_connections: Tuple[str, ...]
    entity_count: int
    state_hash: str

    @classmethod
    def create(
        cls,
        server_tick: int,
        world_revision: int,
        active_connections: Sequence[str],
        entities: Sequence[EntitySnapshot],
    ) -> NetworkSnapshot:
        """Construct a deterministic network state snapshot with canonical SHA-256."""
        sorted_entities = []
        for e in sorted(entities, key=lambda ent: (ent.net_id.namespace, ent.net_id.value)):
            # Sort properties for determinism
            sorted_props = {k: str(v) for k, v in sorted(e.properties.items())}
            sorted_entities.append({
                "ns": e.net_id.namespace,
                "val": e.net_id.value,
                "owner": e.owner_id or "",
                "rev": e.revision,
                "props": sorted_props,
            })

        payload = {
            "server_tick": server_tick,
            "world_revision": world_revision,
            "connections": sorted(active_connections),
            "entities": sorted_entities,
        }
        raw_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        canonical_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

        return cls(
            server_tick=server_tick,
            world_revision=world_revision,
            active_connections=tuple(sorted(active_connections)),
            entity_count=len(entities),
            state_hash=canonical_hash,
        )
