from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .correction_types import (
    CorrectionStatus, ActionAuthorization, RollbackStatus,
    CorrectionStrategyType, RegressionSeverity, OperationType
)

@dataclass
class ParameterChange:
    parameter_id: str
    old_value: Any
    new_value: Any
    delta: float = 0.0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None

@dataclass
class AssetSnapshot:
    snapshot_id: str
    asset_id: str
    iteration_id: int
    timestamp: float
    state_hash: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    transforms: Dict[str, Any] = field(default_factory=dict)
    geometry_state: Dict[str, Any] = field(default_factory=dict)
    material_state: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QualityDeltaReport:
    visual_delta: float = 0.0 # e.g. +0.15
    geometry_delta: float = 0.0 # e.g. +0.10
    topology_delta: float = 0.0
    semantic_integrity: bool = True
    overall_gain: float = 0.0

@dataclass
class CorrectionConfiguration:
    enabled_strategies: List[CorrectionStrategyType] = field(default_factory=lambda: [
        CorrectionStrategyType.DIRECT, CorrectionStrategyType.GRADUAL, CorrectionStrategyType.LOCAL
    ])
    max_actions: int = 5
    max_delta: float = 0.50
    confidence_threshold: float = 0.80
    allow_risky_actions: bool = False
    dry_run: bool = False
    timeout: float = 30.0

@dataclass
class CorrectionResult:
    correction_run_id: str = "CORR_DEFAULT"
    asset_id: str = "asset.root"
    semantic_id: str = "asset.root"
    status: CorrectionStatus = CorrectionStatus.PENDING
    actions_attempted: List[str] = field(default_factory=list)
    actions_applied: List[str] = field(default_factory=list)
    actions_rejected: List[str] = field(default_factory=list)
    actions_rolled_back: List[str] = field(default_factory=list)
    before_state: Optional[AssetSnapshot] = None
    after_state: Optional[AssetSnapshot] = None
    parameter_changes: List[ParameterChange] = field(default_factory=list)
    quality_delta: QualityDeltaReport = field(default_factory=QualityDeltaReport)
    regressions: List[str] = field(default_factory=list)
    rollback_status: RollbackStatus = RollbackStatus.NONE
    iteration_recommendation: str = "CONTINUE"
    correction_hash: str = ""
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CorrectionValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
