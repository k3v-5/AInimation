import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class EvidenceItem:
    evidence_id: str
    evidence_type: str
    source: str
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    relevance: float = 1.0
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            raw = json.dumps(self.content, sort_keys=True, default=str)
            self.content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        raw = json.dumps(self.content, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest() == self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "source": self.source,
            "content": self.content,
            "timestamp": self.timestamp,
            "relevance": self.relevance,
            "content_hash": self.content_hash
        }
