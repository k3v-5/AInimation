import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

class EvaluationDimension(str, Enum):
    SEMANTIC = "SEMANTIC"
    SHAPE = "SHAPE"
    PROPORTION = "PROPORTION"
    SCALE = "SCALE"
    COMPOSITION = "COMPOSITION"
    STYLE = "STYLE"
    MATERIAL = "MATERIAL"
    DETAIL = "DETAIL"
    SPATIAL = "SPATIAL"
    TECHNICAL = "TECHNICAL"

class EvaluationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class RepairScope(str, Enum):
    PARAMETER = "PARAMETER"
    COMPONENT = "COMPONENT"
    ASSET = "ASSET"
    GROUP = "GROUP"
    REGION = "REGION"
    SCENE = "SCENE"

@dataclass
class EvaluationFailure:
    code: str # SCALE_MISMATCH, PROPORTION_MISMATCH, SPATIAL_RELATIONSHIP_FAILURE, MISSING_REQUIRED_ASSET
    severity: EvaluationSeverity
    entity_id: str
    dimension: EvaluationDimension
    expected: Any
    actual: Any
    confidence: float = 0.95
    component_id: Optional[str] = None
    parameter_name: Optional[str] = None
    suggested_scope: RepairScope = RepairScope.PARAMETER
    suggested_action: str = ""

@dataclass
class RepairCandidate:
    repair_id: str
    target_entity: str
    scope: RepairScope
    component_id: Optional[str]
    parameter_name: Optional[str]
    current_value: Any
    target_value: Any
    expected_improvement: float
    cost: float = 1.0
    risk: float = 0.10

@dataclass
class RepairPlan:
    plan_id: str
    target_entity: str
    candidates: List[RepairCandidate] = field(default_factory=list)
    estimated_rebuild_ratio: float = 0.10
    created_at: float = field(default_factory=time.time)

@dataclass
class EvaluationReport:
    evaluation_id: str
    target_id: str
    overall_score: float
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    failures: List[EvaluationFailure] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.95
    created_at: float = field(default_factory=time.time)

    @property
    def is_pass(self) -> bool:
        has_critical_or_error = any(f.severity in [EvaluationSeverity.CRITICAL, EvaluationSeverity.ERROR] for f in self.failures)
        return self.overall_score >= 0.85 and not has_critical_or_error

@dataclass
class ExpectedVisualProfile:
    profile_id: str
    target_dimensions: Dict[str, float] = field(default_factory=dict)
    expected_components: List[str] = field(default_factory=list)
    expected_spatial_relations: Dict[str, str] = field(default_factory=dict)
    target_polycount: int = 10000
    style: str = "STYLIZED"
