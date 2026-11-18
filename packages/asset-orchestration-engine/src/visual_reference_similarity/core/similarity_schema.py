import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .similarity_types import (
    ReferenceType, ReferencePriority, ReferenceCategory, EvaluationStatus,
    DifferenceType, DifferenceSeverity, CorrectionPriority, ViewDirection
)

@dataclass
class ReferenceProfile:
    reference_id: str
    source_type: ReferenceType = ReferenceType.IMAGE
    subject: str = "house"
    priority: ReferencePriority = ReferencePriority.HIGH
    applies_to: List[str] = field(default_factory=lambda: ["silhouette", "proportions", "components", "materials"])
    expected_features: Dict[str, Any] = field(default_factory=dict)
    proportions: Dict[str, float] = field(default_factory=dict)
    silhouette_aspect_ratio: float = 1.3
    confidence: float = 1.0

@dataclass
class AssetObservation:
    asset_id: str
    detected_features: Dict[str, Any] = field(default_factory=dict)
    detected_proportions: Dict[str, float] = field(default_factory=dict)
    silhouette_aspect_ratio: float = 1.3
    bounds: Dict[str, float] = field(default_factory=dict)

@dataclass
class DifferenceRecord:
    target: str
    diff_type: DifferenceType
    severity: DifferenceSeverity
    expected: Any
    actual: Any
    metric: str

@dataclass
class CorrectionRequest:
    correction_id: str
    target: str
    issue: str
    severity: CorrectionPriority
    expected_state: Any
    actual_state: Any
    suggested_action: str
    confidence: float = 0.95

@dataclass
class SimilarityWeights:
    silhouette: float = 0.25
    proportions: float = 0.20
    components: float = 0.20
    spatial: float = 0.15
    materials: float = 0.10
    style: float = 0.10

@dataclass
class SimilarityReport:
    report_id: str
    asset_id: str
    overall_score: float
    category_scores: Dict[str, float] = field(default_factory=dict)
    critical_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    differences: List[DifferenceRecord] = field(default_factory=list)
    corrections: List[CorrectionRequest] = field(default_factory=list)
    evaluation_status: EvaluationStatus = EvaluationStatus.PASS
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

@dataclass
class CandidateAsset:
    candidate_id: str
    score: float
    critical_failures_count: int
    asset_data: Dict[str, Any] = field(default_factory=dict)
