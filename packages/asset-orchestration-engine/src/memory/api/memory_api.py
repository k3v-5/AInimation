import time
from typing import Dict, Any, List, Optional
from ..core.memory_types import (
    MemoryRecord, MemoryType, MemoryScope, MemoryStatus, MemorySource
)
from ..store.memory_store import MemoryStore
from ..core.memory_provenance import MemoryProvenanceService
from ..core.memory_versioning import MemoryVersionManager
from ..query.memory_query_engine import MemoryQueryEngine
from ..context.context_relevance import ContextRelevanceEngine
from ..context.conflict_detector import ContextConflictDetector
from ..context.context_builder import ContextBuilder, ExecutionContext
from ..context.context_snapshot import ContextSnapshot, ContextSnapshotManager
from ..core.memory_consolidator import MemoryConsolidator
from ..governance.memory_governance import MemoryGovernanceGuard
from ...context.services.context_manager import ContextManager
from ...context.core.context_models import ContextPackage, ContextPriority

class ContextMemoryAPI:
    """
    Context & Memory Management API (F73).
    Unified public facade conforming to Section 26 specifications.
    """
    def __init__(self, persistence_path: Optional[str] = None):
        self.store = MemoryStore(persistence_path)
        self.provenance = MemoryProvenanceService()
        self.version_manager = MemoryVersionManager()
        self.query_engine = MemoryQueryEngine(lambda: self.store.list_all(status=None))
        self.relevance = ContextRelevanceEngine()
        self.conflicts = ContextConflictDetector()
        self.builder = ContextBuilder(self.store, self.relevance, self.conflicts)
        self.snapshots = ContextSnapshotManager()
        self.consolidator = MemoryConsolidator(self.store)
        self.governance = MemoryGovernanceGuard()
        self.context_manager = ContextManager(self.store)
        self._init_project_default_memories()

    def _init_project_default_memories(self):
        if len(self.store.list_by_scope(MemoryScope.PROJECT)) == 0:
            self.record_project_constraint(
                constraint_id="darx_fps_standard",
                constraint_data={"category": "FPS_WEAPON", "max_length_mm": 950, "pbr_roughness_min": 0.2, "metallic_default": 0.8},
                importance=1.0, confidence=1.0
            )
            self.store_memory(MemoryRecord(
                memory_id="darx_visual_style_master",
                memory_type=MemoryType.PROJECT_MEMORY,
                scope=MemoryScope.PROJECT,
                project_id="DarX",
                content={
                    "shape_language": "Angular, tactical sci-fi, beveled hard surfaces",
                    "palette": ["Dark Anodized Titanium", "Matte Carbon Black", "Amber Emissive"],
                    "convention": "No duplicate parts, zero self-collision, distinct silhouette"
                },
                source=MemorySource.USER,
                importance=0.95,
                confidence=1.0,
                tags=["style", "art_bible"]
            ))

    # --- Section 26 API Methods ---

    def store_memory(self, record: MemoryRecord, derived_from: Optional[List[str]] = None) -> MemoryRecord:
        saved = self.store.create(record)
        self.provenance.register_provenance(saved, derived_from)
        root_key = record.semantic_id or record.project_id
        self.version_manager.register_version(root_key, saved.memory_id)
        return saved

    def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        return self.store.get(memory_id)

    def query_memory(
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
        return self.query_engine.query(
            semantic_id=semantic_id,
            memory_type=memory_type,
            scope=scope,
            job_id=job_id,
            agent_id=agent_id,
            status=status,
            min_confidence=min_confidence,
            min_importance=min_importance,
            tag=tag
        )

    def update_memory(self, record: MemoryRecord) -> MemoryRecord:
        return self.store.update(record)

    def supersede_memory(self, old_id: str, new_record: MemoryRecord) -> MemoryRecord:
        old = self.store.get(old_id)
        if old:
            new_record = self.version_manager.create_superseded_version(old, new_record)
            self.store.update(old)
        return self.store_memory(new_record, derived_from=[old_id] if old else None)

    def create_snapshot(self, snapshot_id: str, context_data: Dict[str, Any]) -> Any:
        return self.context_manager.create_snapshot(snapshot_id, context_data)

    def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        return self.context_manager.restore_snapshot(snapshot_id)

    def build_context(
        self,
        project_id: str,
        task_id: str,
        agent_id: str,
        semantic_id: Optional[str] = None,
        max_memories: int = 40
    ) -> ExecutionContext:
        return self.builder.build_context(
            project_id=project_id,
            task_id=task_id,
            agent_id=agent_id,
            semantic_id=semantic_id,
            max_memories=max_memories
        )

    def recover_context(self, scope_type: str, target_id: str) -> Any:
        scope_upper = scope_type.upper()
        if scope_upper == "PROJECT":
            return self.context_manager.recovery.recover_project_context(target_id)
        elif scope_upper == "ASSET":
            return self.context_manager.recovery.recover_asset_context(target_id)
        elif scope_upper == "JOB":
            return self.context_manager.recovery.recover_job_context(target_id)
        elif scope_upper == "AGENT":
            return self.context_manager.recovery.recover_agent_context(target_id)
        elif scope_upper == "TASK":
            return self.context_manager.recovery.recover_task_context(target_id)
        raise ValueError(f"Unknown scope_type: {scope_type}")

    def detect_conflicts(self) -> List[Any]:
        active_recs = self.store.list_all(status=MemoryStatus.ACTIVE)
        return self.context_manager.conflicts.detect_conflicts(active_recs)

    # --- Helper & Domain Specific Methods ---

    def record_project_constraint(
        self,
        constraint_id: str,
        constraint_data: Dict[str, Any],
        importance: float = 1.0,
        confidence: float = 1.0
    ) -> MemoryRecord:
        rec = MemoryRecord(
            memory_id=f"CONST_{constraint_id}",
            memory_type=MemoryType.REQUIREMENT_MEMORY,
            scope=MemoryScope.PROJECT,
            content=constraint_data,
            source=MemorySource.USER,
            importance=importance,
            confidence=confidence,
            tags=["constraint", "project_rule"]
        )
        return self.store_memory(rec)

    def record_asset_decision(
        self,
        semantic_id: str,
        decision_data: Dict[str, Any],
        agent_id: str = "agent.strategy",
        source: MemorySource = MemorySource.AOE,
        importance: float = 0.8,
        confidence: float = 0.9
    ) -> MemoryRecord:
        self.governance.validate_write_access(agent_id, MemoryScope.ASSET)
        rec = MemoryRecord(
            memory_id=f"DEC_{int(time.time()*1000)%100000}",
            memory_type=MemoryType.DECISION_MEMORY,
            scope=MemoryScope.ASSET,
            semantic_id=semantic_id,
            agent_id=agent_id,
            content=decision_data,
            source=source,
            importance=importance,
            confidence=confidence,
            tags=["decision"]
        )
        return self.store_memory(rec)

    def record_critic_findings(
        self,
        semantic_id: str,
        findings: Dict[str, Any],
        task_id: str,
        agent_id: str = "agent.visual.critic"
    ) -> MemoryRecord:
        rec = MemoryRecord(
            memory_id=f"CRIT_{int(time.time()*1000)%100000}",
            memory_type=MemoryType.FAILURE_MEMORY,
            scope=MemoryScope.ASSET,
            semantic_id=semantic_id,
            task_id=task_id,
            agent_id=agent_id,
            content=findings,
            source=MemorySource.VALIDATION,
            importance=0.9,
            confidence=0.95,
            tags=["criticism", "defects"]
        )
        return self.store_memory(rec)

    def record_asset_result(
        self,
        semantic_id: str,
        result_data: Dict[str, Any],
        task_id: str,
        agent_id: str
    ) -> MemoryRecord:
        rec = MemoryRecord(
            memory_id=f"RES_{int(time.time()*1000)%100000}",
            memory_type=MemoryType.OPERATION_MEMORY,
            scope=MemoryScope.ASSET,
            semantic_id=semantic_id,
            task_id=task_id,
            agent_id=agent_id,
            content=result_data,
            source=MemorySource.BLENDER,
            importance=0.85,
            confidence=1.0,
            tags=["result", "asset_state"]
        )
        return self.store_memory(rec)

    def build_execution_context(
        self,
        project_id: str,
        task_id: str,
        agent_id: str,
        semantic_id: Optional[str] = None,
        max_memories: int = 40
    ) -> ExecutionContext:
        return self.build_context(
            project_id=project_id,
            task_id=task_id,
            agent_id=agent_id,
            semantic_id=semantic_id,
            max_memories=max_memories
        )

    def capture_context_snapshot(self, snapshot_id: str, ctx: ExecutionContext) -> ContextSnapshot:
        return self.snapshots.capture_snapshot(snapshot_id, ctx)
