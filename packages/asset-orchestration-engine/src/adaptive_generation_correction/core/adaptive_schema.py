import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .adaptive_types import (
    SessionState, CorrectionOp, ScopeLevel, TerminationReason,
    AdaptiveRiskLevel, ErrorCategory
)

@dataclass
class GenerationAttempt:
    attempt_id: str
    parent_attempt_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    seed: int = 42
    total_score: float = 0.50
    category_scores: Dict[str, float] = field(default_factory=dict)
    is_hard_constraint_pass: bool = True
    timestamp: float = field(default_factory=time.time)

@dataclass
class ErrorDiagnosis:
    error_id: str
    category: ErrorCategory
    severity: str = "HIGH"
    affected_features: List[str] = field(default_factory=list)
    probable_causes: List[str] = field(default_factory=list)
    measured_value: Any = None
    target_value: Any = None
    confidence: float = 0.95

@dataclass
class CorrectionCandidate:
    candidate_id: str
    parameter: str
    operation: CorrectionOp
    old_value: Any
    new_value: Any
    delta: float = 0.0
    expected_effect: str = ""
    confidence: float = 0.92
    cost: float = 1.0
    scope: ScopeLevel = ScopeLevel.PARAMETER
    affected_components: List[str] = field(default_factory=list)
    risk: AdaptiveRiskLevel = AdaptiveRiskLevel.LOW

@dataclass
class CorrectionTransactionRecord:
    tx_id: str
    attempt_id: str
    state: str = "OPEN"
    checkpoint_parameters: Dict[str, Any] = field(default_factory=dict)
    dirty_components: List[str] = field(default_factory=list)
    rollback_available: bool = True

@dataclass
class LeaderboardEntry:
    attempt_id: str
    total_score: float
    visual_score: float
    hard_constraint_pass: bool
    cost: float

@dataclass
class SessionReport:
    session_id: str
    asset_id: str
    status: SessionState
    termination_reason: TerminationReason
    total_attempts: int
    score_history: List[float] = field(default_factory=list)
    best_attempt: Optional[GenerationAttempt] = None
    duration: float = 0.0
    rework_efficiency: float = 1.0
