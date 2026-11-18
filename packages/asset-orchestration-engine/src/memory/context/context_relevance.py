import time
from typing import List, Dict, Any, Optional, Tuple
from ..core.memory_types import MemoryRecord, MemoryScope, MemoryType, MemoryStatus

class ContextRelevanceEngine:
    """
    Ranks and budgets memories based on semantic relevance, scope,
    recency, importance, confidence and priority.
    """
    def __init__(
        self,
        weight_semantic: float = 0.35,
        weight_scope: float = 0.20,
        weight_importance: float = 0.20,
        weight_confidence: float = 0.15,
        weight_recency: float = 0.10
    ):
        self.w_sem = weight_semantic
        self.w_scope = weight_scope
        self.w_imp = weight_importance
        self.w_conf = weight_confidence
        self.w_rec = weight_recency

    def compute_relevance(
        self,
        record: MemoryRecord,
        target_semantic_id: Optional[str] = None,
        target_task_id: Optional[str] = None,
        target_agent_id: Optional[str] = None
    ) -> float:
        # Strict cross-asset isolation: If target_semantic_id is set and record belongs to a DIFFERENT asset scope, score = 0.0
        if target_semantic_id and record.scope == MemoryScope.ASSET and record.semantic_id and record.semantic_id != target_semantic_id:
            return 0.0

        # 1. Scope Match
        scope_score = 0.5
        if record.scope == MemoryScope.ASSET and record.semantic_id == target_semantic_id:
            scope_score = 1.0
        elif record.scope == MemoryScope.TASK and record.task_id == target_task_id:
            scope_score = 0.9
        elif record.scope == MemoryScope.PROJECT:
            scope_score = 0.7
        elif record.scope == MemoryScope.GLOBAL:
            scope_score = 0.6
        elif record.scope == MemoryScope.AGENT and record.agent_id == target_agent_id:
            scope_score = 0.8

        # 2. Semantic Match
        sem_score = 0.2
        if record.semantic_id == target_semantic_id:
            sem_score = 1.0
        elif record.scope in (MemoryScope.PROJECT, MemoryScope.GLOBAL):
            sem_score = 0.6

        # 3. Recency (decay over time)
        age_hours = (time.time() - record.updated_at) / 3600.0
        recency_score = max(0.1, 1.0 / (1.0 + 0.05 * age_hours))

        # 4. Importance & Confidence
        imp_score = max(0.0, min(1.0, record.importance))
        conf_score = max(0.0, min(1.0, record.confidence))

        # Weighted combination
        total = (
            self.w_sem * sem_score +
            self.w_scope * scope_score +
            self.w_imp * imp_score +
            self.w_conf * conf_score +
            self.w_rec * recency_score
        )
        return round(min(1.0, max(0.0, total)), 4)

    def rank_and_filter(
        self,
        records: List[MemoryRecord],
        target_semantic_id: Optional[str] = None,
        target_task_id: Optional[str] = None,
        target_agent_id: Optional[str] = None,
        max_memories: int = 50,
        min_relevance_threshold: float = 0.25
    ) -> List[Tuple[MemoryRecord, float]]:
        scored = []
        for r in records:
            if r.status != MemoryStatus.ACTIVE:
                continue
            score = self.compute_relevance(r, target_semantic_id, target_task_id, target_agent_id)
            if score >= min_relevance_threshold:
                scored.append((r, score))
        
        # Sort descending by relevance score
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:max_memories]
