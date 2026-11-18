import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .intent_types import (
    RequirementType, RequirementPriority, RequirementSource,
    AmbiguitySeverity, AmbiguityCategory, ReferenceScopeType,
    TaskCriticality, MilestoneType, PreflightStatus
)

@dataclass
class UserRequest:
    request_id: str
    raw_text: str
    references: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    project_id: str = "DARX_MAIN"
    asset_id: Optional[str] = None

@dataclass
class Requirement:
    req_id: str
    type: RequirementType
    priority: RequirementPriority
    source: RequirementSource
    description: str
    key: str
    value: Any
    confidence: float = 1.0

@dataclass
class ExclusionItem:
    exclusion_id: str
    description: str
    prohibited_terms: List[str] = field(default_factory=list)

@dataclass
class AmbiguityItem:
    ambiguity_id: str
    term: str
    category: AmbiguityCategory
    severity: AmbiguitySeverity
    impact: str

@dataclass
class ClarificationRequest:
    question_id: str
    ambiguity: AmbiguityItem
    options: List[str]
    recommended_option: str
    blocking: bool = True

@dataclass
class ReferenceTargetMask:
    target: List[str] = field(default_factory=lambda: ["building", "house", "structure"])
    context: List[str] = field(default_factory=lambda: ["trees", "vegetation", "ground"])
    ignore: List[str] = field(default_factory=lambda: ["sky", "clouds", "lighting"])
    scope: ReferenceScopeType = ReferenceScopeType.COPY_STRUCTURE

@dataclass
class CompiledIntent:
    intent_id: str
    objective: str
    requirements: List[Requirement] = field(default_factory=list)
    exclusions: List[ExclusionItem] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)
    ambiguities: List[AmbiguityItem] = field(default_factory=list)
    target_mask: ReferenceTargetMask = field(default_factory=ReferenceTargetMask)
    preflight_status: PreflightStatus = PreflightStatus.READY
    confidence: float = 0.95
    clarification_request: Optional[ClarificationRequest] = None

@dataclass
class TaskGraphNode:
    node_id: str
    name: str
    requires: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    consumes: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    criticality: TaskCriticality = TaskCriticality.REQUIRED
    cost: int = 1
    milestone: Optional[MilestoneType] = None

@dataclass
class TaskGraphDAG:
    graph_id: str
    nodes: Dict[str, TaskGraphNode] = field(default_factory=dict)
    milestones: List[MilestoneType] = field(default_factory=list)

@dataclass
class ExecutionPlanStep:
    step_id: str
    target: str
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    preconditions: Dict[str, Any] = field(default_factory=dict)
    postconditions: Dict[str, Any] = field(default_factory=dict)
    validation: str = "pass_milestone"

@dataclass
class IntentDelta:
    delta_id: str
    target: str
    property_name: str
    old_value: Any
    new_value: Any
    affected_subgraph: List[str] = field(default_factory=list)
