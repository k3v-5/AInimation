import hashlib
import json
import time
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class EvidenceItem:
    evidence_id: str
    evidence_type: str
    source: str
    data: Dict[str, Any]
    content_hash: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.content_hash:
            raw = json.dumps(self.data, sort_keys=True, default=str)
            self.content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "source": self.source,
            "data": self.data,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp
        }

class EvidenceAnalyzer:
    """Evaluates integrity and relevance of collected evidence items."""

    @staticmethod
    def verify_evidence(item: EvidenceItem) -> bool:
        raw = json.dumps(item.data, sort_keys=True, default=str)
        expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return item.content_hash == expected
