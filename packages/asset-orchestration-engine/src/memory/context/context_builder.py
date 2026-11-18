from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.memory_types import MemoryRecord, MemoryScope, MemoryType, MemoryStatus
from ..store.memory_store import MemoryStore
from .context_relevance import ContextRelevanceEngine
from .conflict_detector import ContextConflictDetector

@dataclass
class ExecutionContext:
    project_id: str
    semantic_id: Optional[str]
    task_id: str
    agent_id: str
    project_context: Dict[str, Any] = field(default_factory=dict)
    asset_context: Dict[str, Any] = field(default_factory=dict)
    task_context: Dict[str, Any] = field(default_factory=dict)
    relevant_memories: List[Dict[str, Any]] = field(default_factory=list)
    active_constraints: List[str] = field(default_factory=list)
    active_decisions: List[Dict[str, Any]] = field(default_factory=list)
    relevant_references: List[Dict[str, Any]] = field(default_factory=list)
    previous_results: List[Dict[str, Any]] = field(default_factory=list)
    known_errors: List[str] = field(default_factory=list)
    current_asset_state: Dict[str, Any] = field(default_factory=dict)
    allowed_operations: List[str] = field(default_factory=lambda: ["*"])
    relevance_audit: List[Dict[str, Any]] = field(default_factory=list)

class ContextBuilder:
    """
    Constructs bounded, conflict-resolved, prioritized ExecutionContext for agents (F73).
    """
    def __init__(
        self,
        memory_store: MemoryStore,
        relevance_engine: Optional[ContextRelevanceEngine] = None,
        conflict_detector: Optional[ContextConflictDetector] = None
    ):
        self.store = memory_store
        self.relevance = relevance_engine or ContextRelevanceEngine()
        self.conflicts = conflict_detector or ContextConflictDetector()

    def build_context(
        self,
        project_id: str,
        task_id: str,
        agent_id: str,
        semantic_id: Optional[str] = None,
        current_operation: Optional[str] = None,
        max_memories: int = 40
    ) -> ExecutionContext:
        ctx = ExecutionContext(
            project_id=project_id,
            semantic_id=semantic_id,
            task_id=task_id,
            agent_id=agent_id
        )

        all_active = self.store.list_all(status=MemoryStatus.ACTIVE)
        
        # Rank and budget
        ranked = self.relevance.rank_and_filter(
            all_active,
            target_semantic_id=semantic_id,
            target_task_id=task_id,
            target_agent_id=agent_id,
            max_memories=max_memories
        )

        for rec, score in ranked:
            # Audit trace
            ctx.relevance_audit.append({
                "memory_id": rec.memory_id,
                "type": rec.memory_type.value,
                "relevance_score": score,
                "scope": rec.scope.value,
                "importance": rec.importance,
                "source": rec.source.value
            })

            # Categorize into ExecutionContext fields
            if rec.memory_type == MemoryType.CONSTRAINT_MEMORY:
                for k, v in rec.content.items():
                    ctx.active_constraints.append(f"{k}: {v}")
            elif rec.memory_type == MemoryType.DECISION_MEMORY:
                ctx.active_decisions.append({"id": rec.memory_id, "content": rec.content, "version": rec.version})
            elif rec.memory_type == MemoryType.REFERENCE_MEMORY:
                ctx.relevant_references.append(rec.content)
            elif rec.memory_type == MemoryType.RESULT_MEMORY:
                ctx.previous_results.append(rec.content)
            elif rec.memory_type == MemoryType.ERROR_MEMORY:
                ctx.known_errors.append(str(rec.content))
            elif rec.memory_type == MemoryType.STYLE_MEMORY:
                ctx.project_context.update(rec.content)
            elif rec.memory_type == MemoryType.PROJECT_MEMORY or rec.scope == MemoryScope.PROJECT:
                ctx.project_context.update(rec.content)
            elif rec.memory_type == MemoryType.ASSET_MEMORY:
                ctx.asset_context.update(rec.content)

            ctx.relevant_memories.append({
                "memory_id": rec.memory_id,
                "type": rec.memory_type.value,
                "content": rec.content,
                "confidence": rec.confidence,
                "score": score
            })

        return ctx
