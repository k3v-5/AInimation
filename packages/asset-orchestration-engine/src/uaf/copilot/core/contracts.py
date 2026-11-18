"""
UAF-81.95: Core Contracts, Enums & Models for Real-Time In-Engine Co-Piloting & Live Synchronization.
Strict dataclasses, 3D vectors/transforms with UE5 coordinate conversions,
actor replication states, terrain delta patches, and session metrics.
"""

from __future__ import annotations

import math
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CopilotSessionState(str, Enum):
    """Lifecycle state of the live co-piloting session."""
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    CONNECTED = "CONNECTED"
    SYNCING = "SYNCING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    DISCONNECTED = "DISCONNECTED"


class SyncDirection(str, Enum):
    """Direction of the live synchronization channel."""
    AOE_TO_UE5 = "AOE_TO_UE5"
    UE5_TO_AOE = "UE5_TO_AOE"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class CoPilotCommandType(str, Enum):
    """Types of co-pilot synchronization messages."""
    HANDSHAKE = "HANDSHAKE"
    PING = "PING"
    PONG = "PONG"
    SYNC_TERRAIN_REGION = "SYNC_TERRAIN_REGION"
    SYNC_WFC_ROOMS = "SYNC_WFC_ROOMS"
    SYNC_SPAWNER_AI = "SYNC_SPAWNER_AI"
    SYNC_AUDIO_ACOUSTICS = "SYNC_AUDIO_ACOUSTICS"
    FEEDBACK_TRANSFORM_CHANGED = "FEEDBACK_TRANSFORM_CHANGED"
    FEEDBACK_DESIGNER_LOCK = "FEEDBACK_DESIGNER_LOCK"
    ACK = "ACK"
    NACK = "NACK"
    ERROR = "ERROR"


class ConflictResolutionPolicy(str, Enum):
    """Policy for resolving concurrent edits between procedural generator and designer."""
    DESIGNER_LOCK_WINS = "DESIGNER_LOCK_WINS"  # Human designer edits override procedural updates
    PROCEDURAL_OVERRIDE = "PROCEDURAL_OVERRIDE"  # Force overwrite with new procedural seed
    LATEST_TIMESTAMP = "LATEST_TIMESTAMP"      # Wall-clock timestamp arbitration


# ---------------------------------------------------------------------------
# 3D Math Models with Unit Conversion (Meters <-> Unreal Centimeters)
# ---------------------------------------------------------------------------

class Vector3D(BaseModel):
    """3D point or offset in meters."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_ue5_cm(self) -> Tuple[float, float, float]:
        """Converts position from meters to Unreal Engine centimeters (1m = 100cm)."""
        return round(self.x * 100.0, 2), round(self.y * 100.0, 2), round(self.z * 100.0, 2)

    @classmethod
    def from_ue5_cm(cls, x_cm: float, y_cm: float, z_cm: float) -> Vector3D:
        """Converts position from Unreal Engine centimeters to meters."""
        return cls(x=round(x_cm / 100.0, 4), y=round(y_cm / 100.0, 4), z=round(z_cm / 100.0, 4))

    def distance_to(self, other: Vector3D) -> float:
        """Euclidean distance in meters."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)


class Rotator3D(BaseModel):
    """Euler rotation angles in degrees (Pitch, Yaw, Roll)."""
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0


class Transform3D(BaseModel):
    """Complete 3D coordinate frame."""
    position: Vector3D = Field(default_factory=Vector3D)
    rotation: Rotator3D = Field(default_factory=Rotator3D)
    scale: Vector3D = Field(default_factory=lambda: Vector3D(x=1.0, y=1.0, z=1.0))


# ---------------------------------------------------------------------------
# Live Synchronization Entities
# ---------------------------------------------------------------------------

class LiveActorSync(BaseModel):
    """Live state of an actor synchronized between AOE and UE5."""
    actor_id: str
    actor_class: str
    transform: Transform3D = Field(default_factory=Transform3D)
    properties: Dict[str, Any] = Field(default_factory=dict)
    is_locked_by_designer: bool = False
    revision: int = 1
    last_updated_timestamp: float = 0.0


class TerrainRegionPatch(BaseModel):
    """Sub-region heightmap delta patch for instant viewport terrain updates."""
    patch_id: str
    start_x: int = Field(ge=0)
    start_y: int = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    height_samples_m: List[float] = Field(default_factory=list)
    weightmap_layer: Optional[str] = None


class CoPilotMessage(BaseModel):
    """Standardized JSON-RPC live synchronization message."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    command_type: CoPilotCommandType
    sender: str = "AOE_CORE"  # or "UE5_EDITOR"
    timestamp: float = 0.0
    payload: Dict[str, Any] = Field(default_factory=dict)


class CoPilotSessionMetrics(BaseModel):
    """Telemetry and performance metrics for the co-pilot connection."""
    messages_sent: int = 0
    messages_received: int = 0
    average_latency_ms: float = 0.0
    sync_events_count: int = 0
    conflicts_resolved: int = 0
    designer_locks_active: int = 0
