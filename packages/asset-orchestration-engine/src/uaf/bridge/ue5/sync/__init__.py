"""Synchronization primitives, revisions, patches, snapshots, conflicts, and transactions."""

from uaf.bridge.ue5.sync.session import (
    ConnectionState,
    BridgeSession,
)
from uaf.bridge.ue5.sync.revisions import RevisionVector
from uaf.bridge.ue5.sync.patches import (
    PatchOperation,
    StatePatch,
    apply_patch,
    diff_dict,
)
from uaf.bridge.ue5.sync.snapshots import BridgeSnapshot
from uaf.bridge.ue5.sync.conflicts import (
    ConflictPolicy,
    ConflictResolutionError,
    SyncConflict,
    ConflictDetector,
)
from uaf.bridge.ue5.sync.transactions import (
    TransactionStatus,
    TransactionError,
    BridgeTransaction,
    TransactionManager,
)

__all__ = [
    "ConnectionState",
    "BridgeSession",
    "RevisionVector",
    "PatchOperation",
    "StatePatch",
    "apply_patch",
    "diff_dict",
    "BridgeSnapshot",
    "ConflictPolicy",
    "ConflictResolutionError",
    "SyncConflict",
    "ConflictDetector",
    "TransactionStatus",
    "TransactionError",
    "BridgeTransaction",
    "TransactionManager",
]
