from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .reference_types import (
    ReferenceType, ReferenceRole, GeometricPrimitiveType,
    SpatialRelationType, UncertaintyType, SpecificationPriority,
    TargetProfileType, DetailTreatmentType
)

@dataclass
class ReferenceItem:
    reference_id: str
    uri: str
    ref_type: ReferenceType = ReferenceType.IMAGE
    role: ReferenceRole = ReferenceRole.PRIMARY
    priority: float = 1.0
    quality_score: float = 0.95
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VisualLandmark:
    landmark_id: str
    name: str
    normalized_pos: Tuple[float, float] # (x, y) in [0, 1]
    semantic_role: str = ""
    confidence: float = 0.95

@dataclass
class ComponentDetectionRecord:
    component_name: str
    count: int = 1
    bounding_box: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0) # (x, y, w, h)
    normalized_pos: Tuple[float, float, float] = (0.5, 0.5, 0.0)
    primitive_type: GeometricPrimitiveType = GeometricPrimitiveType.BOX
    is_inferred: bool = False
    confidence: float = 0.90
    spatial_relations: List[Dict[str, Any]] = field(default_factory=list) # [{"relation": ABOVE, "target": "walls"}]

@dataclass
class ProportionConstraint:
    name: str
    target_value: float
    tolerance: float = 0.03 # e.g. 0.31 +/- 0.03
    confidence: float = 0.95
    priority: SpecificationPriority = SpecificationPriority.REFERENCE_OBSERVED
    reference_weight: float = 1.0

@dataclass
class UncertaintyItem:
    uncertainty_type: UncertaintyType
    description: str
    impact: str = "HIGH" # HIGH, MEDIUM, LOW
    suggested_question: Optional[str] = None

@dataclass
class FeatureParameterAttribution:
    feature_name: str
    candidate_parameters: List[str] = field(default_factory=list)
    sensitivity_rating: str = "HIGH" # HIGH, MEDIUM, LOW
    confidence: float = 0.92

@dataclass
class VisualSpecification:
    spec_id: str
    archetype_id: str = "MEDIEVAL_HOUSE"
    aspect_ratio: float = 1.52
    roof_ratio: float = 0.31
    detected_components: Dict[str, ComponentDetectionRecord] = field(default_factory=dict)
    landmarks: List[VisualLandmark] = field(default_factory=list)
    materials: Dict[str, str] = field(default_factory=dict)
    dominant_colors: List[str] = field(default_factory=list)
    detail_treatments: Dict[str, DetailTreatmentType] = field(default_factory=dict)
    uncertainties: List[UncertaintyItem] = field(default_factory=list)
    overall_confidence: float = 0.92

@dataclass
class StructuralSpecification:
    spec_id: str
    visual_spec_id: str
    archetype_id: str
    target_parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[ProportionConstraint] = field(default_factory=list)
    gameplay_constraints: Dict[str, Any] = field(default_factory=dict)
    feature_parameter_map: Dict[str, FeatureParameterAttribution] = field(default_factory=dict)

@dataclass
class VisualTargetProfile:
    profile_type: TargetProfileType = TargetProfileType.GAMEPLAY
    similarity_weights: Dict[str, float] = field(default_factory=lambda: {
        "silhouette": 0.30,
        "proportions": 0.25,
        "components": 0.20,
        "materials": 0.15,
        "style": 0.10
    })
    polygon_budget: int = 25000
    tolerance_mode: str = "NORMAL" # STRICT, NORMAL, LOOSE
