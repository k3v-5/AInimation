import time
from typing import List, Dict, Any, Optional
from .memory_types import MemoryRecord, MemoryType, MemoryScope, MemoryStatus, MemorySource
from ..store.memory_store import MemoryStore

class MemoryConsolidator:
    """
    Consolidates multiple raw agent observations into synthesized style rules or decisions.
    """
    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store

    def consolidate_critiques_to_decision(
        self,
        semantic_id: str,
        critique_memory_ids: List[str],
        consolidated_action: Dict[str, Any],
        author_agent_id: str = "agent.strategy"
    ) -> MemoryRecord:
        critiques = [self.store.get(cid) for cid in critique_memory_ids if self.store.get(cid)]
        combined_findings = []
        for c in critiques:
            combined_findings.append(c.content)

        decision_content = {
            "action_plan": consolidated_action,
            "source_findings": combined_findings,
            "synthesized_reason": "Consolidated resolution of previous critic findings."
        }

        rec = MemoryRecord(
            memory_id=f"DEC_CONS_{int(time.time()*1000)%100000}",
            memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET,
            semantic_id=semantic_id,
            agent_id=author_agent_id,
            source=MemorySource.STRATEGY_ENGINE,
            content=decision_content,
            importance=0.9,
            confidence=0.95,
            tags=["consolidated", "critic_resolution"]
        )
        return self.store.create(rec)
