import time
from typing import Dict, Any, List, Optional
from ..core.context_models import ContextPackage, ContextPriority
from ...memory.core.memory_types import MemoryRecord, MemoryType, MemoryScope, MemoryStatus

class ContextPackager:
    """
    Packages relevant context into bounded packages (required, optional, historical)
    according to task objective and priority limits.
    """
    def package_context(
        self,
        task_id: str,
        agent_id: str,
        semantic_id: Optional[str],
        memories: List[MemoryRecord],
        task_objective: str = "",
        priority: ContextPriority = ContextPriority.NORMAL
    ) -> ContextPackage:
        required: Dict[str, Any] = {
            "task_id": task_id,
            "agent_id": agent_id,
            "semantic_id": semantic_id,
            "task_objective": task_objective
        }
        optional: Dict[str, Any] = {}
        historical: List[Dict[str, Any]] = []

        for m in memories:
            if m.status != MemoryStatus.ACTIVE:
                continue

            # Strict cross-asset filter
            if semantic_id and m.scope == MemoryScope.ASSET and m.semantic_id and m.semantic_id != semantic_id:
                continue

            # Categorize based on priority and type
            if m.memory_type in (MemoryType.REQUIREMENT_MEMORY, MemoryType.DECISION_MEMORY) or m.importance >= 0.8:
                required[f"req_{m.memory_id}"] = m.content
            elif m.memory_type in (MemoryType.REFERENCE_MEMORY, MemoryType.OPERATION_MEMORY):
                optional[f"opt_{m.memory_id}"] = m.content
            else:
                historical.append({
                    "memory_id": m.memory_id,
                    "type": m.memory_type.value,
                    "content": m.content,
                    "confidence": m.confidence
                })

        return ContextPackage(
            package_id=f"PKG_CTX_{int(time.time()*1000)%100000}",
            task_id=task_id,
            agent_id=agent_id,
            required_context=required,
            optional_context=optional,
            historical_context=historical,
            priority=priority
        )
