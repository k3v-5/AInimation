"""
UAF-81.95: Real-Time In-Engine Co-Piloting & Live Synchronization.
Headless WebSocket/TCP daemon, live bidirectional synchronization between AOE
and Unreal Engine 5, Designer Lock conflict resolution, and sub-500ms delta updates.
"""

from uaf.copilot.core import (
    CopilotSessionState,
    SyncDirection,
    CoPilotCommandType,
    ConflictResolutionPolicy,
    Vector3D,
    Rotator3D,
    Transform3D,
    LiveActorSync,
    TerrainRegionPatch,
    CoPilotMessage,
    CoPilotSessionMetrics,
)
from uaf.copilot.protocol import (
    serialize_message,
    deserialize_message,
    MessageBuilder,
)
from uaf.copilot.sync import (
    CoPilotReconciler,
)
from uaf.copilot.daemon import (
    CoPilotDaemonServer,
)
from uaf.copilot.ue5 import (
    UE5CoPilotListener,
)

__all__ = [
    # Core
    "CopilotSessionState",
    "SyncDirection",
    "CoPilotCommandType",
    "ConflictResolutionPolicy",
    "Vector3D",
    "Rotator3D",
    "Transform3D",
    "LiveActorSync",
    "TerrainRegionPatch",
    "CoPilotMessage",
    "CoPilotSessionMetrics",
    # Protocol
    "serialize_message",
    "deserialize_message",
    "MessageBuilder",
    # Sync & Reconcile
    "CoPilotReconciler",
    # Daemon
    "CoPilotDaemonServer",
    # UE5 Listener
    "UE5CoPilotListener",
]
