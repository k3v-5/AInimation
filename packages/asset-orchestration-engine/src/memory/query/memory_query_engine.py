from typing import List, Optional, Dict, Any
from ..core.memory_types import MemoryRecord, MemoryType, MemoryScope, MemoryStatus

class MemoryQueryEngine:
    """Advanced querying and filtering engine for MemoryStore."""
    def __init__(self, records_getter):
        self._get_all = records_getter

    def query(
        self,
        semantic_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        job_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[MemoryStatus] = MemoryStatus.ACTIVE,
        min_confidence: float = 0.0,
        min_importance: float = 0.0,
        tag: Optional[str] = None
    ) -> List[MemoryRecord]:
        results = self._get_all()
        if status is not None:
            results = [r for r in results if r.status == status]
        if semantic_id:
            results = [r for r in results if r.semantic_id == semantic_id or r.scope in (MemoryScope.PROJECT, MemoryScope.GLOBAL)]
        if memory_type:
            results = [r for r in results if r.memory_type == memory_type]
        if scope:
            results = [r for r in results if r.scope == scope]
        if job_id:
            results = [r for r in results if r.job_id == job_id]
        if agent_id:
            results = [r for r in results if r.agent_id == agent_id]
        if min_confidence > 0.0:
            results = [r for r in results if r.confidence >= min_confidence]
        if min_importance > 0.0:
            results = [r for r in results if r.importance >= min_importance]
        if tag:
            results = [r for r in results if tag in r.tags]
        return results
