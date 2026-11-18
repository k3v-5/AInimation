import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class LandmarkFeature:
    name: str # roof_peak, foundation_base, window_center, wall_top
    normalized_pos: Tuple[float, float, float] # (x, y, z) in [0, 1] bounding box
    confidence: float = 0.95

@dataclass
class ProportionFeature:
    feature_name: str # roof_to_wall_ratio, width_to_height_ratio, window_to_wall_ratio
    value: float
    tolerance: float = 0.05

@dataclass
class GeometricDiscrepancy:
    component: str # roof, windows, walls
    parameter_hint: str # roof_height, window_scale, width
    expected_value: float
    actual_value: float
    delta_percent: float # e.g. +18.0%, -20.0%
    severity: str = "ERROR" # WARNING, ERROR, CRITICAL
    description: str = ""

@dataclass
class ReferenceProfile:
    reference_id: str
    source_uri: str
    silhouette_complexity: float = 0.85
    proportions: Dict[str, ProportionFeature] = field(default_factory=dict)
    landmarks: List[LandmarkFeature] = field(default_factory=list)
    detected_components: List[str] = field(default_factory=list) # ["roof", "walls", "windows", "foundation"]
    style_attributes: Dict[str, str] = field(default_factory=dict) # {"style": "medieval_stylized", "wear": "medium"}

@dataclass
class ErrorMap:
    reference_id: str
    target_asset_id: str
    silhouette_similarity: float # 0.0 to 1.0
    overall_geometric_score: float # 0.0 to 1.0
    discrepancies: List[GeometricDiscrepancy] = field(default_factory=list)
    missing_components: List[str] = field(default_factory=list)
    unexpected_components: List[str] = field(default_factory=list)
    recommended_patches: Dict[str, float] = field(default_factory=dict) # param_name -> new_value
    created_at: float = field(default_factory=time.time)

    @property
    def is_match(self) -> bool:
        return self.overall_geometric_score >= 0.90 and not self.missing_components and len(self.discrepancies) == 0
