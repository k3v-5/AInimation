from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from .vas_types import (
    RequirementClass, ValidationMethod, RequirementOrigin,
    ContradictionSeverity, AmbiguitySeverity, InformationState, EngineTarget
)

@dataclass
class VisualCompilationInput:
    prompt: str
    asset_class_hint: str = "PROP.GENERIC"
    reference_reports: List[Any] = field(default_factory=list) # DecomposedReferenceReports from F55
    semantic_context: Dict[str, Any] = field(default_factory=dict) # Semantic identities & relationships from F54
    project_constraints: Dict[str, Any] = field(default_factory=dict)
    previous_vas: Optional[Any] = None
    previous_generation_metadata: Dict[str, Any] = field(default_factory=dict)
    instructions: List[str] = field(default_factory=list)

@dataclass
class TraceabilityRecord:
    requirement_id: str
    source_type: RequirementOrigin
    source_id: str
    source_location: str = ""
    transformation: str = "DIRECT"
    confidence: float = 1.0
    timestamp: float = 0.0

@dataclass
class InvariantSpec:
    invariant_id: str
    description: str
    importance: float = 1.0 # 0.0 to 1.0
    source: str = "SYSTEM"
    confidence: float = 1.0
    tolerance: float = 0.0
    validation_method: ValidationMethod = ValidationMethod.SEMANTIC

@dataclass
class VariableSpec:
    variable_id: str
    property_path: str
    min_value: float
    max_value: float
    default_value: float
    unit: str = "unitless"
    priority: float = 0.5
    allowed_to_change: bool = True

@dataclass
class ToleranceSpec:
    property_name: str
    target_value: Any
    tolerance_value: Any
    tolerance_type: str = "ABSOLUTE" # ABSOLUTE, PERCENTAGE, PERCEPTUAL
    unit: str = "meters"

@dataclass
class AcceptanceCriterion:
    criterion_id: str
    target_property: str
    target_value: Any
    tolerance: Any
    priority: float # 0.0 to 1.0
    validation_method: ValidationMethod
    minimum_score: float = 0.90
    failure_severity: str = "BLOCKER"

@dataclass
class AmbiguityReport:
    ambiguity_id: str
    source_text: str
    description: str
    severity: AmbiguitySeverity
    affected_property: str
    possible_interpretations: List[str] = field(default_factory=list)
    resolution_required: bool = False

@dataclass
class ContradictionReport:
    contradiction_id: str
    conflicting_requirements: List[str]
    description: str
    severity: ContradictionSeverity
    recommended_resolution: str

@dataclass
class UnrealRequirementsSpec:
    target_engine: EngineTarget = EngineTarget.UNREAL_ENGINE_5
    target_version: str = "5.4"
    asset_scale: float = 1.0
    nanite_enabled: bool = True
    lod_count: int = 3
    collision_required: bool = True
    collision_type: str = "UCX_CONVEX"
    material_slot_budget: int = 4
    texture_resolution: int = 2048
    pivot_convention: str = "BOTTOM_CENTER_GROUNDED"
    naming_convention: str = "SM_{Asset}_{Descriptor}"
    folder_convention: str = "/Game/DarX/Meshes/Props/"

@dataclass
class ProductionBudgetSpec:
    poly_budget: int = 15000
    triangle_budget: int = 30000
    material_budget: int = 3
    texture_budget_mb: float = 64.0
    generation_time_budget_sec: float = 60.0

@dataclass
class VisualAssetSpecification:
    schema_version: str = "1.0.0"
    specification_id: str = "VAS_DEFAULT"
    specification_hash: str = ""
    specification_version: str = "1.0.0"
    semantic_identity: Dict[str, Any] = field(default_factory=lambda: {"semantic_id": "asset.root", "asset_id": "asset_001", "asset_type": "PROP.GENERIC"})
    source: Dict[str, Any] = field(default_factory=dict)
    intent: Dict[str, Any] = field(default_factory=dict)
    asset_classification: str = "PROP.GENERIC"
    visual_identity: Dict[str, Any] = field(default_factory=dict)
    silhouette: Dict[str, Any] = field(default_factory=dict)
    proportions: Dict[str, Any] = field(default_factory=dict)
    dimensions: Dict[str, Any] = field(default_factory=dict)
    components: List[Dict[str, Any]] = field(default_factory=list)
    geometry_requirements: Dict[str, Any] = field(default_factory=dict)
    detail_requirements: Dict[str, Any] = field(default_factory=dict)
    material_requirements: Dict[str, Any] = field(default_factory=dict)
    surface_requirements: Dict[str, Any] = field(default_factory=dict)
    color_requirements: Dict[str, Any] = field(default_factory=dict)
    style_requirements: Dict[str, Any] = field(default_factory=dict)
    camera_requirements: Dict[str, Any] = field(default_factory=dict)
    lighting_requirements: Dict[str, Any] = field(default_factory=dict)
    presentation_requirements: Dict[str, Any] = field(default_factory=dict)
    technical_requirements: Dict[str, Any] = field(default_factory=dict)
    unreal_requirements: UnrealRequirementsSpec = field(default_factory=UnrealRequirementsSpec)
    production_budget: ProductionBudgetSpec = field(default_factory=ProductionBudgetSpec)
    invariants: List[InvariantSpec] = field(default_factory=list)
    variables: List[VariableSpec] = field(default_factory=list)
    tolerances: List[ToleranceSpec] = field(default_factory=list)
    priorities: Dict[str, float] = field(default_factory=dict)
    requirement_classes: Dict[str, RequirementClass] = field(default_factory=dict)
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    ambiguity_report: List[AmbiguityReport] = field(default_factory=list)
    contradiction_report: List[ContradictionReport] = field(default_factory=list)
    overall_confidence: float = 1.0
    traceability: List[TraceabilityRecord] = field(default_factory=list)
    compilation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
