from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .msp_types import (
    AssetCategoryTag, ComponentConstructionMethod, BasePrimitiveType,
    GeometricOperationType, SymmetryType, DetailLevel, CollisionStrategyType,
    PivotStrategyType, StrategyRiskLevel, ReuseStrategyType
)

@dataclass
class ParametricSpec:
    parameter_id: str
    type_name: str = "float"
    unit: str = "meters"
    default_value: float = 1.0
    minimum: float = 0.001
    maximum: float = 100.0
    source_requirement: str = "VAS"
    expression: Optional[str] = None # e.g. "blade_length * 0.12"
    modifiable: bool = True
    importance: float = 0.8

@dataclass
class GeometricOperation:
    operation_id: str
    operation_type: GeometricOperationType
    target_component: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list) # List of operation_ids that must complete first
    validation_gate: str = "PASS"

@dataclass
class ModifierStrategySpec:
    modifier_id: str
    modifier_type: str
    order: int
    parameters: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    is_destructive: bool = False
    is_required: bool = True

@dataclass
class GeometryNodesStrategySpec:
    node_system_id: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""

@dataclass
class ComponentStrategy:
    component_id: str
    parent_component_id: Optional[str] = None
    semantic_role: str = "BODY"
    method: ComponentConstructionMethod = ComponentConstructionMethod.PARAMETRIC
    base_geometry: BasePrimitiveType = BasePrimitiveType.CUBE
    dimensions: Dict[str, float] = field(default_factory=dict)
    proportions: Dict[str, float] = field(default_factory=dict)
    operations: List[GeometricOperation] = field(default_factory=list)
    parameters: List[ParametricSpec] = field(default_factory=list)
    modifiers: List[ModifierStrategySpec] = field(default_factory=list)
    geometry_nodes: Optional[GeometryNodesStrategySpec] = None
    triangle_budget: int = 5000
    importance: float = 1.0
    visual_weight: float = 1.0
    symmetry: SymmetryType = SymmetryType.NONE
    fallback_method: ComponentConstructionMethod = ComponentConstructionMethod.PRIMITIVE

@dataclass
class GlobalStrategySpec:
    construction_method: str = "HYBRID"
    parametric_level: str = "HIGH"
    procedural_level: str = "HIGH"
    reuse_level: str = "MEDIUM"
    detail_level: str = "HIGH"
    symmetry: SymmetryType = SymmetryType.NONE
    non_destructive_policy: bool = True

@dataclass
class GeometryBudgetDistribution:
    total_triangle_budget: int = 30000
    total_vertex_budget: int = 15000
    component_budgets: Dict[str, int] = field(default_factory=dict)

@dataclass
class CostEstimate:
    estimated_triangles: int = 5000
    estimated_objects: int = 3
    estimated_modifiers: int = 2
    complexity_score: float = 0.45
    risk_level: StrategyRiskLevel = StrategyRiskLevel.LOW
    strategy_score: float = 0.92

@dataclass
class ModelingStrategyPlan:
    schema_version: str = "1.0.0"
    strategy_id: str = "MSP_DEFAULT"
    strategy_hash: str = ""
    strategy_version: str = "1.0.0"
    semantic_id: str = "asset.root"
    specification_id: str = "VAS_DEFAULT"
    asset_classification: List[AssetCategoryTag] = field(default_factory=lambda: [AssetCategoryTag.PROP])
    global_strategy: GlobalStrategySpec = field(default_factory=GlobalStrategySpec)
    component_strategies: List[ComponentStrategy] = field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict) # component_id -> [dependent_ids]
    execution_graph: List[GeometricOperation] = field(default_factory=list) # Ordered DAG of operations
    parameters: List[ParametricSpec] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    geometry_budget: GeometryBudgetDistribution = field(default_factory=GeometryBudgetDistribution)
    topology_strategy: Dict[str, Any] = field(default_factory=lambda: {"quad_preference": True, "manifold_required": True})
    symmetry_strategy: SymmetryType = SymmetryType.NONE
    modifier_strategy: List[ModifierStrategySpec] = field(default_factory=list)
    geometry_nodes_strategy: Optional[GeometryNodesStrategySpec] = None
    detail_strategy: Dict[str, Any] = field(default_factory=dict)
    reuse_strategy: ReuseStrategyType = ReuseStrategyType.CREATE_NEW
    lod_strategy: Dict[str, Any] = field(default_factory=lambda: {"LOD0": 1.0, "LOD1": 0.5, "LOD2": 0.25, "LOD3": 0.10})
    collision_strategy: CollisionStrategyType = CollisionStrategyType.CUSTOM_UCX
    pivot_strategy: PivotStrategyType = PivotStrategyType.BASE_CENTER_GROUNDED
    material_interface: Dict[str, Any] = field(default_factory=dict)
    unreal_interface: Dict[str, Any] = field(default_factory=dict)
    validation_strategy: Dict[str, Any] = field(default_factory=dict)
    fallback_strategies: List[Dict[str, Any]] = field(default_factory=list)
    cost_estimate: CostEstimate = field(default_factory=CostEstimate)
    warnings: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    confidence: float = 0.95
    traceability: List[Dict[str, Any]] = field(default_factory=list)
    compilation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
