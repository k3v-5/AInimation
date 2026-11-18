from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .loop_types import (
    LoopState, DecisionOutcome, StopReason, LoopEventType,
    RegressionPolicyType
)

@dataclass
class IterationTargets:
    minimum_visual_score: float = 0.90
    minimum_geometry_score: float = 0.90
    minimum_topology_score: float = 0.95
    minimum_unreal_readiness: bool = True
    overall_target_score: float = 0.92

@dataclass
class IterationContext:
    loop_id: str
    iteration_id: str
    iteration_number: int
    parent_iteration_id: Optional[str] = None
    asset_id: str = "asset.root"
    semantic_id: str = "asset.root"
    state_hash: str = ""
    baseline_hash: str = ""
    status: LoopState = LoopState.CREATED
    started_at: float = 0.0
    completed_at: float = 0.0

@dataclass
class IterationRecord:
    iteration_number: int
    state_hash: str
    visual_score: float
    geometry_score: float
    overall_score: float
    accepted: bool
    corrections_applied: List[str] = field(default_factory=list)
    decision: DecisionOutcome = DecisionOutcome.CONTINUE

@dataclass
class IterationLoopConfiguration:
    max_iterations: int = 5
    max_runtime: float = 120.0
    max_actions: int = 15
    max_corrections: int = 10
    stagnation_window: int = 3
    minimum_improvement: float = 0.015
    quality_epsilon: float = 0.005
    cycle_detection_enabled: bool = True
    oscillation_detection_enabled: bool = True
    targets: IterationTargets = field(default_factory=IterationTargets)
    dry_run: bool = False

@dataclass
class IterativeGenerationRequest:
    job_id: str
    asset_id: str
    semantic_id: str
    reference_report: Any
    vas: Any
    configuration: IterationLoopConfiguration = field(default_factory=IterationLoopConfiguration)

@dataclass
class IterativeGenerationResult:
    loop_id: str = "LOOP_DEFAULT"
    asset_id: str = "asset.root"
    semantic_id: str = "asset.root"
    status: LoopState = LoopState.COMPLETED
    iterations_executed: int = 1
    accepted_iteration: int = 0
    final_state_hash: str = ""
    final_quality: float = 1.0
    initial_quality: float = 1.0
    quality_delta: float = 0.0
    best_iteration: int = 0
    stop_reason: StopReason = StopReason.CONVERGENCE_REACHED
    iteration_history: List[IterationRecord] = field(default_factory=list)
    loop_hash: str = ""
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoopValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
