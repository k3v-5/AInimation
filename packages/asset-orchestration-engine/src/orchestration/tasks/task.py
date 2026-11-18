import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.agent_state import TaskStatus, TaskPriority, FailureAction

@dataclass
class Task:
    task_id: str
    task_type: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    owner_agent_id: Optional[str] = None
    required_capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout_sec: float = 60.0
    failure_policy: FailureAction = FailureAction.RETRY
    parent_task_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def transition_to(self, new_status: TaskStatus):
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.BLOCKED],
            TaskStatus.READY: [TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.BLOCKED],
            TaskStatus.RUNNING: [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.RETRYING, TaskStatus.CANCELLED],
            TaskStatus.BLOCKED: [TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.CANCELLED],
            TaskStatus.RETRYING: [TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.FAILED, TaskStatus.CANCELLED],
            TaskStatus.COMPLETED: [],
            TaskStatus.FAILED: [TaskStatus.RETRYING, TaskStatus.RUNNING],
            TaskStatus.CANCELLED: [],
            TaskStatus.SKIPPED: []
        }
        allowed = valid_transitions.get(self.status, [])
        if new_status not in allowed and new_status != self.status:
            raise ValueError(f"Invalid task transition from {self.status} to {new_status}")
        
        self.status = new_status
        if new_status == TaskStatus.RUNNING and not self.started_at:
            self.started_at = time.time()
        elif new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.SKIPPED]:
            self.completed_at = time.time()
