from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .evaluation_types import (
    EvaluationCategory, DefectType, DefectSeverity,
    DefectCauseCategory, AcceptanceStatus, EvaluationLevel,
    RegressionStatus
)

@dataclass
class CorrectionHint:
    target: str
    parameter: str
    direction: str # "INCREASE", "DECREASE", "MODIFY", "ALIGN"
    magnitude: float = 0.05
    priority: float = 0.85
    confidence: float = 0.90
    expected_score_gain: float = 0.08

@dataclass
class VisualDefect:
    defect_id: str
    defect_type: DefectType
    severity: DefectSeverity = DefectSeverity.MODERATE
    region: str = "asset.root"
    semantic_id: str = "asset.root"
    component_id: Optional[str] = None
    bbox: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0) # min_x, min_y, max_x, max_y
    score: float = 0.70
    confidence: float = 0.90
    expected: Any = None
    actual: Any = None
    error_pct: float = 0.0
    probable_causes: Dict[str, float] = field(default_factory=lambda: {DefectCauseCategory.GEOMETRY.value: 0.90})
    correction_hint: Optional[CorrectionHint] = None

@dataclass
class CategoryEvaluation:
    category: EvaluationCategory
    score: float = 1.0
    weight: float = 1.0
    confidence: float = 0.95
    status: str = "EVALUATED"
    metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class RegionEvaluation:
    region_id: str
    semantic_id: str
    component_id: str
    score: float = 1.0
    defects: List[VisualDefect] = field(default_factory=list)

@dataclass
class RequirementEvaluationResult:
    requirement_id: str
    score: float = 1.0
    status: AcceptanceStatus = AcceptanceStatus.PASS
    evidence: Dict[str, Any] = field(default_factory=dict)
    defects: List[VisualDefect] = field(default_factory=list)
    confidence: float = 0.95

@dataclass
class EvaluationDelta:
    previous_eval_id: str
    current_eval_id: str
    score_delta: float = 0.0
    fixed_defects: List[str] = field(default_factory=list)
    new_defects: List[str] = field(default_factory=list)
    regression_status: RegressionStatus = RegressionStatus.NONE

@dataclass
class EvaluationConfiguration:
    weights: Dict[str, float] = field(default_factory=lambda: {
        EvaluationCategory.SILHOUETTE.value: 1.0,
        EvaluationCategory.PROPORTION.value: 0.9,
        EvaluationCategory.GEOMETRY.value: 0.9,
        EvaluationCategory.MATERIAL.value: 0.8,
        EvaluationCategory.COLOR.value: 0.7,
        EvaluationCategory.ROUGHNESS.value: 0.6,
        EvaluationCategory.LIGHTING.value: 0.5,
        EvaluationCategory.CAMERA.value: 0.5
    })
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        "pass_global": 0.85,
        "warn_global": 0.70,
        "silhouette_iou_min": 0.88,
        "aspect_ratio_error_max": 0.10
    })
    minimum_confidence: float = 0.50
    enabled_categories: List[EvaluationCategory] = field(default_factory=lambda: list(EvaluationCategory))

@dataclass
class VisualEvaluationResult:
    evaluation_id: str = "EVAL_DEFAULT"
    semantic_id: str = "asset.root"
    reference_id: str = "REF_DEFAULT"
    geometry_generation_id: str = "GEN_DEFAULT"
    surface_generation_id: str = "SURF_DEFAULT"
    presentation_id: str = "VPC_DEFAULT"
    global_score: float = 0.95
    category_scores: Dict[str, CategoryEvaluation] = field(default_factory=dict)
    region_scores: Dict[str, RegionEvaluation] = field(default_factory=dict)
    defects: List[VisualDefect] = field(default_factory=list)
    difference_maps: Dict[str, str] = field(default_factory=dict)
    confidence: float = 0.95
    requirement_results: List[RequirementEvaluationResult] = field(default_factory=list)
    correction_hints: List[CorrectionHint] = field(default_factory=list)
    acceptance_status: AcceptanceStatus = AcceptanceStatus.PASS
    evaluation_hash: str = ""
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
