import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set
from .orchestrator_types import AgentType, TaskState, LockType, RiskLevel, ExecutionMode, MessageType, ScopeType

@dataclass
class AgentDefinition:
    agent_id: str
    agent_type: AgentType
    capabilities: List[str] = field(default_factory=list)
    allowed_tools: List[str] = field(default_factory=list)
    max_iterations: int = 5
    timeout_sec: float = 30.0
    is_busy: bool = False

@dataclass
class Task:
    task_id: str
    task_type: str # CREATE_WALLS, CREATE_ROOF, CREATE_DOOR, CREATE_STAIRS, VALIDATE_GAMEPLAY
    target_asset_id: str
    parent_task_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    state: TaskState = TaskState.CREATED
    assigned_agent: Optional[str] = None
    attempt: int = 1
    max_attempts: int = 3
    scope: ScopeType = ScopeType.COMPONENT_SCOPE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class Checkpoint:
    checkpoint_id: str
    asset_id: str
    parameters: Dict[str, Any]
    task_states: Dict[str, TaskState]
    timestamp: float = field(default_factory=time.time)

@dataclass
class ChangeSet:
    task_id: str
    agent_id: str
    modified_parameters: Dict[str, Any]
    tools_used: List[str]
    timestamp: float = field(default_factory=time.time)

@dataclass
class OrchestrationCorrectionPlan:
    problem: str
    parameter_to_change: str
    old_value: Any
    new_value: Any
    affected_subtrees: List[str] = field(default_factory=list) # ["door", "collision", "navigation"]
    rebuild_scope: str = "SUBTREE" # SUBTREE vs FULL_ASSET

@dataclass
class ExecutionReport:
    execution_id: str
    status: str # APPROVED, REJECTED, ESCALATED, ROLLED_BACK
    tasks_executed: int
    total_attempts: int
    rollbacks_count: int
    final_parameters: Dict[str, Any]
    execution_logs: List[str] = field(default_factory=list)
    is_approved: bool = True

@dataclass
class OrchestratorConfig:
    max_iterations: int = 5
    max_attempts_per_task: int = 3
    safe_mode: bool = False
    execution_mode: ExecutionMode = ExecutionMode.AUTOMATIC
    quality_threshold: float = 0.85
