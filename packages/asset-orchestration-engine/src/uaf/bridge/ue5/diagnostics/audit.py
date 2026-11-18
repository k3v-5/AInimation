"""Tamper-evident LiveLink audit trail with SHA-256 cryptographic chaining.

Every state mutation, transaction lifecycle event, conflict resolution, and
reconnection event is committed to this append-only hash-chained ledger.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AuditEntry:
    """An immutable entry in the LiveLink audit trail."""
    sequence: int
    timestamp_us: int
    event_type: str
    object_id: Optional[str]
    revision: Optional[int]
    payload_hash: str
    prev_hash: str
    entry_hash: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LiveLinkAuditTrail:
    """Append-only, SHA-256 hash-chained audit log for bridge events."""

    GENESIS_HASH: str = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self) -> None:
        self._entries: List[AuditEntry] = []

    @property
    def entries(self) -> List[AuditEntry]:
        return list(self._entries)

    @property
    def count(self) -> int:
        return len(self._entries)

    @property
    def latest_hash(self) -> str:
        if not self._entries:
            return self.GENESIS_HASH
        return self._entries[-1].entry_hash

    def record(
        self,
        event_type: str,
        object_id: Optional[str] = None,
        revision: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """Records a new immutable audit entry, chained to the previous entry's hash."""
        seq = len(self._entries)
        now_us = int(time.perf_counter() * 1_000_000)
        prev_hash = self.latest_hash
        details_dict = details or {}

        serialized_details = json.dumps(details_dict, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(serialized_details.encode("utf-8")).hexdigest()

        # Compute chain hash: SHA-256(seq || timestamp || event_type || object_id || rev || payload_hash || prev_hash)
        entry_raw = f"{seq}:{now_us}:{event_type}:{object_id or ''}:{revision or 0}:{payload_hash}:{prev_hash}"
        entry_hash = hashlib.sha256(entry_raw.encode("utf-8")).hexdigest()

        entry = AuditEntry(
            sequence=seq,
            timestamp_us=now_us,
            event_type=event_type,
            object_id=object_id,
            revision=revision,
            payload_hash=payload_hash,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            details=details_dict,
        )
        self._entries.append(entry)
        return entry

    def verify_chain(self) -> bool:
        """Verifies the integrity of the cryptographic hash chain."""
        expected_prev = self.GENESIS_HASH
        for entry in self._entries:
            if entry.prev_hash != expected_prev:
                return False

            serialized_details = json.dumps(entry.details, sort_keys=True, default=str)
            computed_payload_hash = hashlib.sha256(serialized_details.encode("utf-8")).hexdigest()
            if computed_payload_hash != entry.payload_hash:
                return False

            entry_raw = f"{entry.sequence}:{entry.timestamp_us}:{entry.event_type}:{entry.object_id or ''}:{entry.revision or 0}:{entry.payload_hash}:{entry.prev_hash}"
            computed_entry_hash = hashlib.sha256(entry_raw.encode("utf-8")).hexdigest()
            if computed_entry_hash != entry.entry_hash:
                return False

            expected_prev = entry.entry_hash
        return True

    def find_by_object(self, object_id: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.object_id == object_id]

    def find_by_event(self, event_type: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.event_type == event_type]
