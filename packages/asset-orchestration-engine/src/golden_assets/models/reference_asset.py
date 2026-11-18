import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from ..core.golden_types import ReferenceStatus

@dataclass
class ReferenceAsset:
    reference_id: str
    semantic_id: str
    asset_family: str
    category: str
    status: ReferenceStatus = ReferenceStatus.DRAFT
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_file: Optional[str] = None
    content_hash: str = ""
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self.compute_hash()

    def compute_hash(self) -> str:
        data = {
            "reference_id": self.reference_id,
            "semantic_id": self.semantic_id,
            "asset_family": self.asset_family,
            "category": self.category,
            "metadata": self.metadata,
            "source_file": self.source_file
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "semantic_id": self.semantic_id,
            "asset_family": self.asset_family,
            "category": self.category,
            "status": self.status.value,
            "metadata": self.metadata,
            "source_file": self.source_file,
            "content_hash": self.content_hash,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferenceAsset":
        return cls(
            reference_id=data["reference_id"],
            semantic_id=data.get("semantic_id", ""),
            asset_family=data.get("asset_family", "general"),
            category=data.get("category", "prop"),
            status=ReferenceStatus(data.get("status", "DRAFT")),
            metadata=data.get("metadata", {}),
            source_file=data.get("source_file"),
            content_hash=data.get("content_hash", ""),
            created_at=data.get("created_at", time.time())
        )
