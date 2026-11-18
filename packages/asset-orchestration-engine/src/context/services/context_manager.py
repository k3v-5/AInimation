from typing import Optional, Dict, Any, List
from .context_recovery_service import ContextRecoveryService
from .context_packager import ContextPackager
from .context_snapshot_service import ContextSnapshotService
from .context_conflict_detector import ContextConflictDetector
from ..core.context_models import ContextPackage, ContextSnapshot, ContextPriority
from ...memory.store.memory_store import MemoryStore

class ContextManager:
    """
    Central Context Manager coordinating recovery, packaging, snapshots and conflict detection.
    """
    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store
        self.recovery = ContextRecoveryService(memory_store)
        self.packager = ContextPackager()
        self.snapshots = ContextSnapshotService()
        self.conflicts = ContextConflictDetector()

    def build_context_package(
        self,
        task_id: str,
        agent_id: str,
        semantic_id: Optional[str] = None,
        task_objective: str = "",
        priority: ContextPriority = ContextPriority.NORMAL
    ) -> ContextPackage:
        memories = self.store.list_all()
        return self.packager.package_context(
            task_id=task_id,
            agent_id=agent_id,
            semantic_id=semantic_id,
            memories=memories,
            task_objective=task_objective,
            priority=priority
        )

    def create_snapshot(self, snapshot_id: str, context_data: Dict[str, Any]) -> ContextSnapshot:
        return self.snapshots.create_snapshot(snapshot_id, context_data)

    def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        return self.snapshots.restore_snapshot(snapshot_id)
