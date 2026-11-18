from typing import Dict, Any, Optional
from ..core.agent_state import TaskStatus, TaskPriority, FailureAction, AgentPermission
from ..core.agent_registry import AgentRegistry
from ..core.orchestration_plan import OrchestrationPlan
from ..core.orchestration_policy import OrchestrationPolicy
from ..tasks.task import Task
from ..tasks.task_graph import TaskGraph
from ..engine.orchestration_engine import OrchestrationEngine

class MultiAgentOrchestrationAPI:
    """
    Multi-Agent Orchestration API (F71).
    Public facade for constructing, planning, executing and recovering multi-agent asset orchestration workflows.
    """
    def __init__(self, registry: Optional[AgentRegistry] = None, policy: Optional[OrchestrationPolicy] = None):
        self._engine = OrchestrationEngine(registry=registry, policy=policy)

    @property
    def registry(self) -> AgentRegistry:
        return self._engine.registry

    @property
    def event_log(self):
        return self._engine.event_log

    def create_plan(self, asset_id: str, semantic_id: str, prompt: str = "Tactical weapon") -> OrchestrationPlan:
        return self._engine.build_standard_weapon_pipeline_plan(asset_id, semantic_id, prompt)

    def execute_plan(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        return self._engine.execute_plan(plan)
