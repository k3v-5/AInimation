"""Full-scene snapshot capture and canonical SHA-256 state hashing."""

from __future__ import annotations
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class BridgeSnapshot:
    """Immutable full-scene snapshot representing the synchronized world."""
    snapshot_id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    frame: int = 0
    timestamp_ns: int = field(default_factory=time.perf_counter_ns)
    actors: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    assets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    world_data: Dict[str, Any] = field(default_factory=dict)
    state_hash: str = ""
    # Aliases
    objects: Optional[Dict[str, Dict[str, Any]]] = None
    timestamp_us: Optional[int] = None

    def __post_init__(self) -> None:
        if self.timestamp_us is not None:
            self.timestamp_ns = self.timestamp_us * 1000
        if self.objects is not None:
            self.actors = self.objects
        else:
            self.objects = self.actors

        if not self.state_hash:
            self.state_hash = self.compute_canonical_hash()

    def compute_canonical_hash(self) -> str:
        """Computes a deterministic SHA-256 checksum across actors, assets, and world settings."""
        canonical_dict = {
            "actors": {k: self.actors[k] for k in sorted(self.actors.keys())},
            "assets": {k: self.assets[k] for k in sorted(self.assets.keys())},
            "world_data": {k: self.world_data[k] for k in sorted(self.world_data.keys())},
        }
        encoded = json.dumps(canonical_dict, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "frame": self.frame,
            "timestamp_ns": self.timestamp_ns,
            "actors": self.actors,
            "assets": self.assets,
            "world_data": self.world_data,
            "state_hash": self.state_hash,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
