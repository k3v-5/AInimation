from typing import Optional, Dict, Any, List
from ..core.context_models import (
    GlobalContext, AssetContext, TaskContext, AgentContext, JobContext
)
from ...memory.store.memory_store import MemoryStore
from ...memory.core.memory_types import MemoryScope, MemoryType, MemoryStatus

class ContextRecoveryService:
    """
    Recovers structured contextual states purely from persistent MemoryStore
    across restarts, crashes and worker handoffs.
    """
    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store

    def recover_project_context(self, project_id: str = "DarX") -> GlobalContext:
        recs = self.store.query(scope=MemoryScope.PROJECT, status=MemoryStatus.ACTIVE)
        rules = []
        standards = {}
        for r in recs:
            if "rule" in r.content:
                rules.append(r.content["rule"])
            standards.update(r.content)
        return GlobalContext(
            project_id=project_id,
            project_rules=rules,
            asset_standards=standards
        )

    def recover_asset_context(self, semantic_id: str) -> AssetContext:
        recs = self.store.list_by_asset(semantic_id, status=MemoryStatus.ACTIVE)
        geom = {}
        mats = []
        col = {}
        for r in recs:
            if r.memory_type == MemoryType.OPERATION_MEMORY:
                if "objects" in r.content:
                    geom.update(r.content)
                if "materials" in r.content:
                    mats.append(r.content["materials"])
            elif r.memory_type == MemoryType.DECISION_MEMORY:
                geom.update(r.content)
        return AssetContext(
            semantic_id=semantic_id,
            geometry=geom,
            materials=mats,
            collision=col
        )

    def recover_job_context(self, job_id: str) -> JobContext:
        recs = self.store.query(job_id=job_id, status=MemoryStatus.ACTIVE)
        completed = []
        failed = []
        for r in recs:
            if r.memory_type == MemoryType.OPERATION_MEMORY:
                completed.append(r.memory_id)
            elif r.memory_type == MemoryType.FAILURE_MEMORY:
                failed.append(r.memory_id)
        return JobContext(
            job_id=job_id,
            completed_operations=completed,
            failed_operations=failed
        )

    def recover_agent_context(self, agent_id: str) -> AgentContext:
        recs = self.store.query(agent_id=agent_id, status=MemoryStatus.ACTIVE)
        facts = [r.content for r in recs]
        return AgentContext(
            agent_id=agent_id,
            role="WORKER",
            known_facts=facts
        )

    def recover_task_context(self, task_id: str) -> TaskContext:
        recs = self.store.list_by_task(task_id)
        completed = []
        reqs = []
        for r in recs:
            if r.memory_type == MemoryType.OPERATION_MEMORY:
                completed.append(r.memory_id)
            elif r.memory_type == MemoryType.REQUIREMENT_MEMORY:
                reqs.append(str(r.content))
        return TaskContext(
            task_id=task_id,
            objective=f"Task {task_id}",
            requirements=reqs,
            completed_steps=completed,
            current_state="IN_PROGRESS" if completed else "PENDING"
        )
