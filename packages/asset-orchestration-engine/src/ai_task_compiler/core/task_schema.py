import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .task_types import (
    TaskSource, TaskAction, SemanticOperation, TaskScope, TaskPriority,
    TaskRiskLevel, TaskStatusEnum, AmbiguityType, TaskPermissionType, ConstraintTypeEnum
)

@dataclass
class TargetSpec:
    semantic_id: str
    asset_id: str
    component_id: Optional[str] = None
    level_id: Optional[str] = None
    target_type: str = "ASSET" # ASSET, COMPONENT, LEVEL, MULTI
    confidence: float = 1.0

@dataclass
class IntentModel:
    action: TaskAction
    objective: str
    target: TargetSpec
    desired_state: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

@dataclass
class TaskConstraint:
    constraint_id: str
    constraint_type: ConstraintTypeEnum
    target_property: str
    value: Any = None
    is_hard: bool = True

@dataclass
class TaskPreference:
    preference_id: str
    description: str
    weight: float = 0.5

@dataclass
class TaskEnvelope:
    task_id: str
    source: TaskSource = TaskSource.USER
    source_id: str = "user_default"
    timestamp: float = field(default_factory=time.time)
    raw_instruction: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    requested_operation: SemanticOperation = SemanticOperation.CHANGE_DIMENSIONS
    target: TargetSpec = field(default_factory=lambda: TargetSpec("HOUSE_001", "HOUSE_001"))
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[TaskConstraint] = field(default_factory=list)
    preferences: List[TaskPreference] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    risk: TaskRiskLevel = TaskRiskLevel.LOW
    permissions: List[TaskPermissionType] = field(default_factory=lambda: [TaskPermissionType.MODIFY_ASSET])
    status: TaskStatusEnum = TaskStatusEnum.COMPILED
    requires_approval: bool = False
    idempotency_key: str = ""

    def compute_envelope_hash(self) -> str:
        payload = {
            "source": self.source.value,
            "raw": self.raw_instruction.strip(),
            "target": self.target.semantic_id,
            "op": self.requested_operation.value,
            "params": self.parameters,
            "constraints": [
                {"type": c.constraint_type.value, "prop": c.target_property, "val": str(c.value)}
                for c in self.constraints
            ]
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

@dataclass
class TaskPreview:
    task_id: str
    target: str
    operation: str
    parameters: Dict[str, Any]
    constraints: List[str]
    expected_affected: List[str]
    expected_unaffected: List[str]
    risk: str
    estimated_cost_ms: float
    explanation: str

@dataclass
class ClarificationRequest:
    request_id: str
    question: str
    options: List[str]
    ambiguity_type: AmbiguityType

@dataclass
class TaskDecomposition:
    parent_task_id: str
    subtasks: List[TaskEnvelope]
    dependency_graph: Dict[str, List[str]] # subtask_id -> [depends_on_ids]

@dataclass
class TaskResult:
    status: TaskStatusEnum
    task_id: str
    interpretation: str
    warnings: List[str] = field(default_factory=list)
    ambiguities: List[str] = field(default_factory=list)
    preview: Optional[TaskPreview] = None
    next_action: str = "EXECUTE_PLAN"
