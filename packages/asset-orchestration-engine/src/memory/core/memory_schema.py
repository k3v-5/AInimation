import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class FailureRecord:
    failure_id: str
    asset_id: str
    asset_type: str
    component_type: str
    failure_type: str # e.g. BLADE_TOO_SHORT, MATERIAL_METALLIC_MISMATCH
    metric: str
    actual_value: float
    expected_value: float
    severity: str = "WARNING" # WARNING, ERROR, CRITICAL
    fingerprint: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class CorrectionRecord:
    correction_id: str
    failure_id: str
    strategy_id: str
    operation_type: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    before_score: float = 0.0
    after_score: float = 0.0
    result: str = "SUCCESS" # SUCCESS, PARTIAL_SUCCESS, FAILURE, ROLLBACK, NO_EFFECT, REGRESSION
    is_rollback: bool = False
    timestamp: float = field(default_factory=time.time)

@dataclass
class StrategyRecord:
    strategy_id: str
    failure_type: str
    asset_type: str
    component_type: str
    preferred_operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    sample_count: int = 1
    success_count: int = 1
    failure_count: int = 0
    success_rate: float = 1.0
    confidence: float = 0.50
    average_improvement: float = 0.15
    engine_version: str = "1.0"
