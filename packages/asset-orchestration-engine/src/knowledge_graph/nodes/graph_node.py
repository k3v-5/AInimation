import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .node_types import NodeType

@dataclass
class GraphNode:
    node_id: str
    node_type: NodeType
    semantic_id: Optional[str] = None
    project_id: str = "DarX"
    version: int = 1
    status: str = "ACTIVE"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    source: str = "SYSTEM"
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    integrity_hash: str = ""

    def __post_init__(self):
        if isinstance(self.node_type, str):
            try:
                self.node_type = NodeType(self.node_type)
            except Exception:
                pass
        if not self.integrity_hash:
            self.integrity_hash = self.compute_hash()

    def compute_hash(self) -> str:
        type_val = self.node_type.value if hasattr(self.node_type, "value") else str(self.node_type)
        data = {
            "node_id": self.node_id,
            "node_type": type_val,
            "semantic_id": self.semantic_id,
            "project_id": self.project_id,
            "version": self.version,
            "source": self.source,
            "metadata": self.metadata
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.integrity_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "semantic_id": self.semantic_id,
            "project_id": self.project_id,
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source": self.source,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "integrity_hash": self.integrity_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphNode":
        return cls(
            node_id=data["node_id"],
            node_type=NodeType(data["node_type"]),
            semantic_id=data.get("semantic_id"),
            project_id=data.get("project_id", "DarX"),
            version=data.get("version", 1),
            status=data.get("status", "ACTIVE"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            source=data.get("source", "SYSTEM"),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
            integrity_hash=data.get("integrity_hash", "")
        )
