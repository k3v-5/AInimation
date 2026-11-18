import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .memory_types import MemoryRecord, MemorySource

@dataclass
class ProvenanceNode:
    memory_id: str
    source_type: MemorySource
    source_id: str
    created_by: str
    created_at: float
    derived_from: List[str] = field(default_factory=list)

class MemoryProvenanceService:
    """Tracks and reconstructs the lineage/provenance chain of all memory records."""
    def __init__(self):
        self._provenance: Dict[str, ProvenanceNode] = {}

    def register_provenance(self, record: MemoryRecord, derived_from: Optional[List[str]] = None):
        node = ProvenanceNode(
            memory_id=record.memory_id,
            source_type=record.source,
            source_id=record.source_id,
            created_by=record.agent_id or "SYSTEM",
            created_at=record.created_at,
            derived_from=derived_from or ([record.parent_memory_id] if record.parent_memory_id else [])
        )
        self._provenance[record.memory_id] = node

    def get_lineage(self, memory_id: str) -> List[ProvenanceNode]:
        chain = []
        curr = memory_id
        visited = set()
        while curr and curr not in visited:
            visited.add(curr)
            node = self._provenance.get(curr)
            if not node:
                break
            chain.append(node)
            curr = node.derived_from[0] if node.derived_from else None
        return chain
