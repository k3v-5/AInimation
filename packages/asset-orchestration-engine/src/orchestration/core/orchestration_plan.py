from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..tasks.task_graph import TaskGraph
from .agent_state import FailureAction

@dataclass
class OrchestrationPlan:
    orchestration_id: str
    objective: str
    asset_id: str
    semantic_id: str
    task_graph: TaskGraph = field(default_factory=TaskGraph)
    max_iterations: int = 50
    minimum_quality_score: float = 85.0
    failure_policy: FailureAction = FailureAction.RETRY
    metadata: Dict[str, Any] = field(default_factory=dict)
