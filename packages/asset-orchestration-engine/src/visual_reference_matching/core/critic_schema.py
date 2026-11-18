import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .critic_types import (
    EvaluationMode, VisualDiagnosisType, CriticDecisionType,
    ReferenceRole, EvaluationStage, ColorSpaceType
)

@dataclass
class ReferenceImageSpec:
    image_id: str
    role: ReferenceRole = ReferenceRole.SILHOUETTE
    expected_aspect_ratio: float = 1.52 # width / height
    expected_roof_ratio: float = 0.31   # roof / body
    expected_components: Dict[str, Any] = field(default_factory=dict)
    expected_colors: Dict[str, List[float]] = field(default_factory=dict) # e.g. {"walls": [50.0, 0.0, 0.0]} (Lab)
    confidence: float = 0.95

@dataclass
class SilhouetteMetrics:
    iou: float = 1.0
    hausdorff_distance: float = 0.0
    aspect_ratio_error: float = 0.0
    score: float = 1.0

@dataclass
class ProportionMetrics:
    roof_to_body_error: float = 0.0
    width_to_height_error: float = 0.0
    score: float = 1.0

@dataclass
class MaterialMetrics:
    delta_e: float = 0.0
    score: float = 1.0

@dataclass
class VisualDiagnosis:
    diag_type: VisualDiagnosisType
    location: str
    severity: str
    deviation_amount: float
    description: str
    confidence: float = 0.95

@dataclass
class ParameterCorrection:
    parameter_name: str
    current_value: float
    suggested_value: float
    delta: float
    relative_change_pct: float
    affected_components: List[str] = field(default_factory=list)
    risk: str = "LOW"
    confidence: float = 0.90
    replan_required: bool = False

@dataclass
class ScoringWeights:
    silhouette: float = 0.35
    proportions: float = 0.25
    components: float = 0.20
    spatial: float = 0.10
    material: float = 0.05
    style: float = 0.05

@dataclass
class VisualScoreReport:
    report_id: str
    asset_id: str
    overall_score: float
    sub_scores: Dict[str, float] = field(default_factory=dict)
    diagnoses: List[VisualDiagnosis] = field(default_factory=list)
    suggested_corrections: List[ParameterCorrection] = field(default_factory=list)
    decision: CriticDecisionType = CriticDecisionType.ACCEPT
    explainability: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
