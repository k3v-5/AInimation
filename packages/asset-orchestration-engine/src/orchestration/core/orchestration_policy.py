from dataclasses import dataclass, field
from .agent_state import FailureAction

@dataclass
class OrchestrationPolicy:
    max_iterations: int = 3
    min_quality_score: float = 85.0
    failure_action: FailureAction = FailureAction.RETRY
    retry_limit: int = 3
    concurrency_limit: int = 4
    enforce_tool_guard: bool = True
    enforce_resource_locks: bool = True
    persist_checkpoints: bool = True
