import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .runtime_types import (
    RuntimeTaskStatus, RuntimeTaskType, RuntimePriority,
    RuntimeLockType, AgentState, ExecutionState, RuntimeEventType,
    ConcurrencyMode
)

@dataclass
class Task:
    task_id: str
    asset_id: str
    type: RuntimeTaskType
    parent_task_id: Optional[str] = None
    project_id: str = "DARX_MAIN"
    priority: RuntimePriority = RuntimePriority.NORMAL
    status: RuntimeTaskStatus = RuntimeTaskStatus.CREATED
    dependencies: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class EventEnvelope:
    event_id: str
    event_type: RuntimeEventType
    timestamp: float
    source: str
    task_id: str
    asset_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""

@dataclass
class LockLease:
    lock_id: str
    resource_id: str
    task_id: str
    lock_type: RuntimeLockType
    acquired_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 30.0)

@dataclass
class AgentProfile:
    agent_id: str
    capabilities: List[str]
    permissions: List[str] = field(default_factory=lambda: ["READ", "PLAN", "EXECUTE"])
    state: AgentState = AgentState.IDLE
    last_heartbeat: float = field(default_factory=time.time)

@dataclass
class ExecutionUnit:
    execution_id: str
    task_id: str
    operation: str
    agent_id: str
    idempotency_key: str
    status: ExecutionState = ExecutionState.CREATED
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class WorkflowStep:
    step_id: str
    task_type: RuntimeTaskType
    required_capabilities: List[str]
    is_critical: bool = True

@dataclass
class Workflow:
    workflow_id: str
    asset_id: str
    steps: List[WorkflowStep] = field(default_factory=list)
    current_step_index: int = 0
    status: str = "IN_PROGRESS"

@dataclass
class AssetManifest:
    asset_id: str
    specification_id: str
    asset_hash: str
    version: str
    artifacts: List[str] = field(default_factory=list)
    validation_passed: bool = True
    similarity_score: float = 0.95
    final_status: str = "APPROVED"
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
