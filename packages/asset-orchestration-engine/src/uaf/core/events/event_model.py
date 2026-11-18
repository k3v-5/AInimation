"""
Base event model for Universal Asset Factory.
UAF-81.0 Sections 36, 37, 38.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class UAFEvent:
    """
    Immutable domain event with correlation tracking.
    """
    event_type: str
    production_id: str
    operation_id: Optional[str] = None
    asset_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "production_id": self.production_id,
            "operation_id": self.operation_id,
            "asset_id": self.asset_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UAFEvent":
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            production_id=data["production_id"],
            operation_id=data.get("operation_id"),
            asset_id=data.get("asset_id"),
            timestamp=float(data.get("timestamp", time.time())),
            payload=data.get("payload", {}),
        )
