from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .critic_types import (
    DefectCategory, DefectSeverity, CriticRecommendation,
    QualityProfile, CriticCameraView, RequirementType
)

@dataclass
class ExpectedState:
    asset_class: str = "HOUSE"
    style: str = "STYLIZED_LOW_POLY"
    required_components: List[str] = field(default_factory=lambda: ["roof", "walls", "entrance"])
    forbidden_components: List[str] = field(default_factory=lambda: ["satellite_dish", "modern_antenna", "gun"])
    expected_proportions: Dict[str, float] = field(default_factory=lambda: {"roof_ratio": 0.30})
    expected_materials: Dict[str, str] = field(default_factory=lambda: {"walls": "STONE", "roof": "WOOD"})
    hardness_map: Dict[str, RequirementType] = field(default_factory=dict)

@dataclass
class ActualState:
    detected_class: str = "HOUSE"
    detected_components: List[str] = field(default_factory=list)
    measured_proportions: Dict[str, float] = field(default_factory=dict)
    detected_materials: Dict[str, str] = field(default_factory=dict)
    is_photorealistic: bool = False
    detail_density: float = 0.50
    multi_view_aspect_ratios: Dict[CriticCameraView, float] = field(default_factory=dict)
    component_spatial_status: Dict[str, str] = field(default_factory=dict) # e.g. "window_02": "BEHIND_WALL"
    detection_confidences: Dict[str, float] = field(default_factory=dict)

@dataclass
class VisualDefect:
    defect_id: str
    category: DefectCategory
    severity: DefectSeverity
    confidence: float
    affected_component: str
    expected: Any
    actual: Any
    evidence: str
    recommended_action: str
    scope: str = "LOCAL"

@dataclass
class CorrectionPlanItem:
    item_id: str
    defect_id: str
    action: str
    target_component: str
    parameter: Optional[str] = None
    delta: Optional[float] = None
    tool: str = "BlenderAgent"
    expected_effect: str = ""
    risk: str = "LOW"

@dataclass
class CriticResult:
    overall_score: float
    technical_score: float
    visual_score: float
    hard_failures: List[str] = field(default_factory=list)
    defects: List[VisualDefect] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendation: CriticRecommendation = CriticRecommendation.ACCEPT
    correction_plan: List[CorrectionPlanItem] = field(default_factory=list)
    explanation_human: str = ""
    explanation_agent: str = ""
