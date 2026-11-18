from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .scoring_types import (
    AcceptanceStatus, QualityLevel, MetricCategory,
    ConstraintSeverity, QualityTrend, DirectionType, MetricStatus
)

@dataclass
class QualityMetric:
    metric_id: str
    name: str
    category: MetricCategory
    raw_value: Any
    normalized_value: float = 1.0 # 0.0 to 1.0
    weight: float = 1.0
    direction: DirectionType = DirectionType.HIGHER_IS_BETTER
    required: bool = True
    status: MetricStatus = MetricStatus.VALID
    source: str = "F61_OR_F62"

@dataclass
class QualityConstraint:
    constraint_id: str
    name: str
    category: MetricCategory
    severity: ConstraintSeverity = ConstraintSeverity.HIGH
    blocking: bool = True
    threshold: float = 0.0
    description: str = ""

@dataclass
class QualityDefect:
    defect_id: str
    category: MetricCategory
    severity: ConstraintSeverity
    description: str
    location: str = "root"
    blocking: bool = False

@dataclass
class QualityProfile:
    profile_id: str = "DEFAULT_GAME_PROP"
    version: str = "1.0.0"
    weights: Dict[MetricCategory, float] = field(default_factory=lambda: {
        MetricCategory.VISUAL: 0.30,
        MetricCategory.GEOMETRY: 0.20,
        MetricCategory.TOPOLOGY: 0.15,
        MetricCategory.MATERIAL: 0.10,
        MetricCategory.UNREAL_READINESS: 0.15,
        MetricCategory.SEMANTIC: 0.10
    })
    acceptance_threshold: float = 85.0
    conditional_threshold: float = 70.0
    rejection_threshold: float = 50.0
    category_minimums: Dict[MetricCategory, float] = field(default_factory=lambda: {
        MetricCategory.VISUAL: 0.80,
        MetricCategory.GEOMETRY: 0.80,
        MetricCategory.TOPOLOGY: 0.90,
        MetricCategory.UNREAL_READINESS: 0.85
    })

@dataclass
class AcceptanceExplanation:
    decision: AcceptanceStatus
    summary: str
    passed_requirements: List[str] = field(default_factory=list)
    failed_requirements: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)
    strongest_metrics: List[str] = field(default_factory=list)
    weakest_metrics: List[str] = field(default_factory=list)

@dataclass
class QualityResult:
    asset_id: str = "asset.root"
    semantic_id: str = "asset.root"
    evaluation_id: str = "EVAL_001"
    overall_score: float = 100.0 # 0.0 to 100.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    quality_level: QualityLevel = QualityLevel.EXCEPTIONAL
    acceptance_status: AcceptanceStatus = AcceptanceStatus.ACCEPTED
    blocking_reasons: List[str] = field(default_factory=list)
    quality_hash: str = ""
    evaluated_at: float = 0.0
    scoring_version: str = "1.0.0"

@dataclass
class QualityReport:
    report_id: str
    asset_id: str
    semantic_id: str
    quality_result: QualityResult
    explanation: AcceptanceExplanation
    metrics: List[QualityMetric] = field(default_factory=list)
    defects: List[QualityDefect] = field(default_factory=list)
    profile_id: str = "DEFAULT_GAME_PROP"
    human_readable: str = ""

@dataclass
class ScoringValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
