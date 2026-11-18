"""Quarantine isolation for corrupted assets and malformed actors."""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class QuarantinedItem:
    item_id: str
    item_type: str  # "Asset" or "Actor"
    reason: str
    timestamp_ns: int = field(default_factory=time.perf_counter_ns)
    metadata: Dict[str, Any] = field(default_factory=dict)


class QuarantineManager:
    """Isolates failing entities without terminating the LiveLink session."""

    def __init__(self) -> None:
        self._quarantined: Dict[str, QuarantinedItem] = {}

    @property
    def count(self) -> int:
        return len(self._quarantined)

    def quarantine(
        self,
        item_id: str,
        reason: str,
        item_type: str = "Asset",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuarantinedItem:
        item = QuarantinedItem(
            item_id=item_id,
            item_type=item_type,
            reason=reason,
            metadata=metadata or {},
        )
        self._quarantined[item_id] = item
        return item

    def is_quarantined(self, item_id: str) -> bool:
        return item_id in self._quarantined

    def get(self, item_id: str) -> Optional[QuarantinedItem]:
        return self._quarantined.get(item_id)

    def release(self, item_id: str) -> Optional[QuarantinedItem]:
        return self._quarantined.pop(item_id, None)

    def get_all(self) -> List[QuarantinedItem]:
        return list(self._quarantined.values())

    def clear(self) -> None:
        self._quarantined.clear()
