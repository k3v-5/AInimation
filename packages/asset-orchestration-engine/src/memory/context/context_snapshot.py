import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .context_builder import ExecutionContext

@dataclass
class ContextSnapshot:
    snapshot_id: str
    task_id: str
    semantic_id: Optional[str]
    created_at: float = field(default_factory=time.time)
    context_data: Dict[str, Any] = field(default_factory=dict)
    active_memory_ids: List[str] = field(default_factory=list)
    snapshot_hash: str = ""

    def __post_init__(self):
        if not self.snapshot_hash:
            self.snapshot_hash = self.compute_hash()

    def compute_hash(self) -> str:
        data = {
            "snapshot_id": self.snapshot_id,
            "task_id": self.task_id,
            "semantic_id": self.semantic_id,
            "memory_ids": sorted(self.active_memory_ids),
            "context_data": self.context_data
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class ContextSnapshotManager:
    """Manages context snapshots associated with F70 long-running job checkpoints."""
    def __init__(self):
        self._snapshots: Dict[str, ContextSnapshot] = {}

    def capture_snapshot(self, snapshot_id: str, execution_ctx: ExecutionContext) -> ContextSnapshot:
        mem_ids = [m["memory_id"] for m in execution_ctx.relevant_memories if "memory_id" in m]
        ctx_data = {
            "project_context": execution_ctx.project_context,
            "asset_context": execution_ctx.asset_context,
            "active_constraints": execution_ctx.active_constraints,
            "active_decisions": execution_ctx.active_decisions
        }
        snap = ContextSnapshot(
            snapshot_id=snapshot_id,
            task_id=execution_ctx.task_id,
            semantic_id=execution_ctx.semantic_id,
            context_data=ctx_data,
            active_memory_ids=mem_ids
        )
        self._snapshots[snapshot_id] = snap
        return snap

    def get_snapshot(self, snapshot_id: str) -> Optional[ContextSnapshot]:
        return self._snapshots.get(snapshot_id)
