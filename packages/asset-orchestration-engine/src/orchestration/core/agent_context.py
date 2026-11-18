from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .agent_state import AgentPermission

@dataclass
class AgentContext:
    orchestration_id: str
    job_id: str
    task_id: str
    asset_id: str
    semantic_id: str
    project_id: str = "DEFAULT_PROJECT"
    permissions: List[AgentPermission] = field(default_factory=list)
    available_capabilities: List[str] = field(default_factory=list)
    previous_results: Dict[str, Any] = field(default_factory=dict)
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    budget: Dict[str, float] = field(default_factory=dict)
    execution_metadata: Dict[str, Any] = field(default_factory=dict)

    def get_result(self, task_id: str) -> Optional[Any]:
        return self.previous_results.get(task_id)
