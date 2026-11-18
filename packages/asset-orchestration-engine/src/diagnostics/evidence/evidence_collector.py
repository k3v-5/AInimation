from typing import Dict, List, Optional
from .provenance import EvidenceItem

class EvidenceCollector:
    """Manages collection, hashing, and retrieval of evidence items."""
    def __init__(self):
        self._evidence: Dict[str, EvidenceItem] = {}

    def add_evidence(self, evidence_id: str, evidence_type: str, source: str, content: dict, relevance: float = 1.0) -> EvidenceItem:
        item = EvidenceItem(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            source=source,
            content=content,
            relevance=relevance
        )
        self._evidence[evidence_id] = item
        return item

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceItem]:
        item = self._evidence.get(evidence_id)
        if item and not item.verify_integrity():
            raise RuntimeError(f"Evidence '{evidence_id}' has been tampered with.")
        return item

    def list_evidence(self) -> List[EvidenceItem]:
        return list(self._evidence.values())
