import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .control_types import (
    TaskState, AgentRole, ToolEffect, LockType, DecisionAction, ApprovalStatus
)

@dataclass
class Task:
    task_id: str
    intent: str
    parent_task_id: Optional[str] = None
    assigned_agent: Optional[AgentRole] = None
    status: TaskState = TaskState.CREATED
    budget_mcp_calls: int = 30
    priority: int = 1
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class AgentDefinition:
    agent_id: str
    role: AgentRole
    capabilities: List[str] = field(default_factory=list)
    allowed_effects: List[ToolEffect] = field(default_factory=lambda: [ToolEffect.READ_ONLY])
    concurrency_limit: int = 1

@dataclass
class ToolDefinition:
    tool_id: str
    provider: str
    effect: ToolEffect = ToolEffect.READ_ONLY
    required_preconditions: List[str] = field(default_factory=list)
    timeout_sec: float = 30.0

@dataclass
class AgentResult:
    task_id: str
    agent_id: str
    status: TaskState
    outputs: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    error_message: Optional[str] = None
    mcp_calls_used: int = 1

@dataclass
class ResourceLock:
    lock_id: str
    lock_type: LockType
    resource_id: str
    owner_task_id: str
    acquired_at: float = field(default_factory=time.time)
    timeout_sec: float = 60.0

@dataclass
class ExecutionTrace:
    trace_id: str
    task_id: str
    agent_id: str
    tool_id: str
    duration: float = 0.0
    status: str = "SUCCESS"

@dataclass
class ControlPlan:
    plan_id: str
    intent: str
    agent_pipeline: List[AgentRole] = field(default_factory=list)
    subtasks: List[Task] = field(default_factory=list)
    estimated_mcp_calls: int = 10
