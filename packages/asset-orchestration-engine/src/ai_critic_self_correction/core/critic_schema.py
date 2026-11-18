import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .critic_types import (
    CriticStatus, ModificationLevel, CorrectionOperationType,
    RootCauseSeverity, CriticRiskLevel, BudgetStatus, StrategyResult
)

@dataclass
class RootCause:
    cause_id: str
    description: str
    affected_properties: List[str] = field(default_factory=list)
    evidence: str = ""
    confidence: float = 0.95
    severity: RootCauseSeverity = RootCauseSeverity.HIGH
    dependencies: List[str] = field(default_factory=list)

@dataclass
class PreservationContract:
    preserve_properties: List[str] = field(default_factory=list)
    target_modification: str = ""

@dataclass
class CorrectionOp:
    operation_id: str
    operation_type: CorrectionOperationType
    target: str
    level: ModificationLevel
    parameters: Dict[str, Any] = field(default_factory=dict)
    cost: int = 1
    blast_radius: str = "LOW"

@dataclass
class CorrectionPlan:
    plan_id: str
    target_asset: str
    operations: List[CorrectionOp] = field(default_factory=list)
    preservation_contract: PreservationContract = field(default_factory=PreservationContract)
    preconditions: Dict[str, Any] = field(default_factory=dict)
    postconditions: Dict[str, Any] = field(default_factory=dict)
    estimated_cost: int = 5
    risk: CriticRiskLevel = CriticRiskLevel.LOW

@dataclass
class CriticDecision:
    decision_id: str
    asset_id: str
    status: CriticStatus
    score: float
    diagnosis: List[RootCause] = field(default_factory=list)
    plan: Optional[CorrectionPlan] = None
    confidence: float = 0.95
    next_action: str = "EXECUTE"
    stop_reason: Optional[str] = None

@dataclass
class CriticPolicy:
    max_iterations: int = 5
    max_cost: int = 50
    minimum_improvement: float = 0.02
    human_review_threshold: float = 0.60

@dataclass
class CheckpointSnapshot:
    checkpoint_id: str
    score: float
    asset_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class CandidateBranch:
    branch_id: str
    plan: CorrectionPlan
    predicted_score: float = 0.90
