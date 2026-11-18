import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class LoopStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAILED_MAX_ITERATIONS = "FAILED_MAX_ITERATIONS"
    STAGNATED = "STAGNATED"

@dataclass
class CorrectionStep:
    target_component: str
    parameter_name: str
    current_value: float
    recommended_value: float
    operation: str = "SET"
    reason: str = ""

@dataclass
class CorrectionPlan:
    plan_id: str
    steps: List[CorrectionStep] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    rebuild_scope: str = "SUBTREE" # PARAMETER, COMPONENT, SUBTREE, ASSET
    estimated_improvement: float = 0.20

@dataclass
class LoopIterationRecord:
    iteration_index: int
    score_before: float
    score_after: float
    applied_patches: Dict[str, float] = field(default_factory=dict)
    affected_components: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

@dataclass
class AutonomousLoopResult:
    status: LoopStatus
    iterations_run: int
    final_score: float
    target_asset_id: str
    history: List[LoopIterationRecord] = field(default_factory=list)
    unresolved_problems: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    message: str = ""
