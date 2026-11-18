import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .edge_types import RelationshipType

@dataclass
class GraphEdge:
    edge_id: str
    source_node: str
    target_node: str
    relationship_type: RelationshipType
    created_at: float = field(default_factory=time.time)
    created_by: str = "SYSTEM"
    job_id: Optional[str] = None
    agent_id: Optional[str] = None
    version: int = 1
    confidence: float = 1.0
    source: str = "AOE"
    metadata: Dict[str, Any] = field(default_factory=dict)
    integrity_hash: str = ""

    def __post_init__(self):
        if not self.integrity_hash:
            self.integrity_hash = self.compute_hash()

    def compute_hash(self) -> str:
        data = {
            "edge_id": self.edge_id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "relationship_type": self.relationship_type.value,
            "version": self.version,
            "job_id": self.job_id,
            "agent_id": self.agent_id,
            "metadata": self.metadata
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.integrity_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "relationship_type": self.relationship_type.value,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "job_id": self.job_id,
            "agent_id": self.agent_id,
            "version": self.version,
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata,
            "integrity_hash": self.integrity_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEdge":
        return cls(
            edge_id=data["edge_id"],
            source_node=data["source_node"],
            target_node=data["target_node"],
            relationship_type=RelationshipType(data["relationship_type"]),
            created_at=data.get("created_at", time.time()),
            created_by=data.get("created_by", "SYSTEM"),
            job_id=data.get("job_id"),
            agent_id=data.get("agent_id"),
            version=data.get("version", 1),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "AOE"),
            metadata=data.get("metadata", {}),
            integrity_hash=data.get("integrity_hash", "")
        )
