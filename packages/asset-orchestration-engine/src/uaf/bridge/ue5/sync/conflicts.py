"""Conflict detection and resolution policies for concurrent bidirectional edits."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from uaf.bridge.ue5.sync.revisions import RevisionVector


class ConflictPolicy(str, Enum):
    UAF_WINS = "UAF_WINS"
    UE_WINS = "UE_WINS"
    LATEST_TIMESTAMP = "LATEST_TIMESTAMP"
    REJECT = "REJECT"
    MANUAL_RESOLUTION = "MANUAL_RESOLUTION"
    MERGE = "MERGE"


class ConflictResolutionError(Exception):
    """Raised when a conflict cannot be automatically resolved under the active policy."""
    pass


@dataclass
class SyncConflict:
    """Represents concurrent divergent modifications to the same property."""
    object_id: str
    property: str
    uaf_value: Any
    ue5_value: Any
    uaf_revision: int
    ue5_revision: int
    uaf_timestamp_ns: int
    ue5_timestamp_ns: int
    conflict_id: str = field(default_factory=lambda: f"cnf_{uuid.uuid4().hex[:10]}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "object_id": self.object_id,
            "property": self.property,
            "uaf_value": self.uaf_value,
            "ue5_value": self.ue5_value,
            "uaf_revision": self.uaf_revision,
            "ue5_revision": self.ue5_revision,
            "uaf_timestamp_ns": self.uaf_timestamp_ns,
            "ue5_timestamp_ns": self.ue5_timestamp_ns,
        }


class ConflictDetector:
    """Detects and resolves concurrent edit conflicts between UAF and UE5."""

    def __init__(
        self,
        policy: ConflictPolicy = ConflictPolicy.UAF_WINS,
        default_policy: Optional[ConflictPolicy] = None,
    ) -> None:
        self.policy = default_policy or policy
        self.conflict_history: list[SyncConflict] = []

    def check_conflict(
        self,
        object_id: str,
        property_path: str,
        uaf_value: Any,
        ue5_value: Any,
        uaf_rev: RevisionVector,
        ue5_rev: RevisionVector,
        uaf_ts_ns: int = 0,
        ue5_ts_ns: int = 0,
    ) -> Optional[SyncConflict]:
        """Detects if changes are concurrent and values differ."""
        if uaf_value == ue5_value:
            return None

        if uaf_rev.is_concurrent_with(ue5_rev) or (uaf_rev.logical_revision == ue5_rev.logical_revision):
            conflict = SyncConflict(
                object_id=object_id,
                property=property_path,
                uaf_value=uaf_value,
                ue5_value=ue5_value,
                uaf_revision=uaf_rev.uaf_revision,
                ue5_revision=ue5_rev.ue5_revision,
                uaf_timestamp_ns=uaf_ts_ns,
                ue5_timestamp_ns=ue5_ts_ns,
            )
            self.conflict_history.append(conflict)
            return conflict
        return None

    def detect(
        self,
        object_id: str,
        base_rev: Optional[RevisionVector] = None,
        uaf_rev: Optional[RevisionVector] = None,
        ue5_rev: Optional[RevisionVector] = None,
        uaf_patch: Any = None,
        ue5_patch: Any = None,
        property_path: str = "state",
        uaf_value: Any = None,
        ue5_value: Any = None,
    ) -> Optional[SyncConflict]:
        """Convenience overload for detecting conflicts between revision vectors."""
        u_rev = uaf_rev or RevisionVector()
        e_rev = ue5_rev or RevisionVector()
        # If values not given, use patches or dummy placeholders
        val_u = uaf_value if uaf_value is not None else (uaf_patch or "uaf")
        val_e = ue5_value if ue5_value is not None else (ue5_patch or "ue5")
        return self.check_conflict(
            object_id=object_id,
            property_path=property_path,
            uaf_value=val_u,
            ue5_value=val_e,
            uaf_rev=u_rev,
            ue5_rev=e_rev,
        )

    def resolve(
        self,
        conflict: SyncConflict,
        uaf_val: Any = None,
        ue5_val: Any = None,
    ) -> Any:
        """Applies configured policy to determine the winning value."""
        val_u = uaf_val if uaf_val is not None else conflict.uaf_value
        val_e = ue5_val if ue5_val is not None else conflict.ue5_value

        if self.policy == ConflictPolicy.UAF_WINS:
            return val_u
        elif self.policy == ConflictPolicy.UE_WINS:
            return val_e
        elif self.policy == ConflictPolicy.LATEST_TIMESTAMP:
            return val_u if conflict.uaf_timestamp_ns >= conflict.ue5_timestamp_ns else val_e
        elif self.policy == ConflictPolicy.REJECT:
            raise ConflictResolutionError(
                f"Sync conflict rejected on {conflict.object_id}.{conflict.property}"
            )
        elif self.policy == ConflictPolicy.MERGE:
            if isinstance(val_u, dict) and isinstance(val_e, dict):
                merged = dict(val_e)
                merged.update(val_u)
                return merged
            return val_u
        return val_u
