"""Typed message definitions, authority models, sync states, and change events for UAF-81.87."""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class BridgeMessageType(str, Enum):
    # Handshake & Heartbeat
    HELLO = "HELLO"
    WELCOME = "WELCOME"
    PING = "PING"
    PONG = "PONG"
    HEARTBEAT = "HEARTBEAT"
    CAPABILITIES = "CAPABILITIES"
    SESSION_CONFIG = "SESSION_CONFIG"
    READY = "READY"

    # CRUD & Delta Sync
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    PATCH = "PATCH"
    SNAPSHOT = "SNAPSHOT"

    # Assets
    ASSET_CREATE = "ASSET_CREATE"
    ASSET_UPDATE = "ASSET_UPDATE"
    ASSET_DELETE = "ASSET_DELETE"
    ASSET_RELOAD = "ASSET_RELOAD"

    # Scene & Actors
    SCENE_LOAD = "SCENE_LOAD"
    SCENE_UNLOAD = "SCENE_UNLOAD"
    ACTOR_SPAWN = "ACTOR_SPAWN"
    ACTOR_UPDATE = "ACTOR_UPDATE"
    ACTOR_DESTROY = "ACTOR_DESTROY"

    # Subsystems
    CAMERA_UPDATE = "CAMERA_UPDATE"
    TRANSFORM_UPDATE = "TRANSFORM_UPDATE"
    ANIMATION_UPDATE = "ANIMATION_UPDATE"
    VFX_UPDATE = "VFX_UPDATE"
    LIGHT_UPDATE = "LIGHT_UPDATE"
    AUDIO_UPDATE = "AUDIO_UPDATE"

    # Diagnostics & Control
    ERROR = "ERROR"
    WARNING = "WARNING"
    ACK = "ACK"
    NACK = "NACK"


class AuthorityModel(str, Enum):
    UAF_AUTHORITATIVE = "UAF_AUTHORITATIVE"
    UE_AUTHORITATIVE = "UE_AUTHORITATIVE"
    SHARED = "SHARED"


class SyncState(str, Enum):
    SYNCED = "SYNCED"
    PENDING = "PENDING"
    DIRTY = "DIRTY"
    CONFLICT = "CONFLICT"
    ERROR = "ERROR"
    ORPHANED = "ORPHANED"
    MISSING = "MISSING"


class UpdatePriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    PREVIEW = "PREVIEW"


@dataclass
class ChangeEvent:
    """Explicit, auditable mutation record between UAF and UE5."""
    object_id: str
    property: str = ""
    old_value: Any = None
    new_value: Any = None
    source: Any = "UAF"  # str or AuthorityModel
    revision: int = 1
    timestamp_ns: int = field(default_factory=time.perf_counter_ns)
    frame: int = 0
    event_id: Optional[str] = None
    priority: UpdatePriority = UpdatePriority.NORMAL
    patch: Any = None
    state_hash: Optional[str] = None

    def __post_init__(self) -> None:
        if self.event_id is None:
            self.event_id = f"evt_{int(time.perf_counter() * 1_000_000)}"

    def to_dict(self) -> Dict[str, Any]:
        src_val = self.source.value if hasattr(self.source, "value") else str(self.source)
        return {
            "event_id": self.event_id,
            "object_id": self.object_id,
            "property": self.property,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "source": src_val,
            "revision": self.revision,
            "timestamp_ns": self.timestamp_ns,
            "frame": self.frame,
            "priority": self.priority.value if hasattr(self.priority, "value") else str(self.priority),
            "state_hash": self.state_hash,
        }


@dataclass
class BridgeMessage:
    """Universal envelope for all LiveLink / interoperability bridge traffic."""
    message_type: BridgeMessageType
    payload: Dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    sequence: int = 0
    session_id: str = ""
    source: str = "UAF"
    timestamp_ns: int = field(default_factory=time.perf_counter_ns)
    priority: UpdatePriority = UpdatePriority.NORMAL
    sender_id: Optional[str] = None
    requires_ack: bool = False
    ack_message_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.sender_id is not None:
            self.source = self.sender_id
        else:
            self.sender_id = self.source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sequence": self.sequence,
            "session_id": self.session_id,
            "source": self.source,
            "sender_id": self.sender_id,
            "timestamp_ns": self.timestamp_ns,
            "priority": self.priority.value,
            "payload": self.payload,
            "requires_ack": self.requires_ack,
            "ack_message_id": self.ack_message_id,
        }
