from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .optimization_types import (
    TargetPlatform, TargetEngine, OptimizationObjective,
    NanitePolicy, CollisionPolicy, SessionStatus, StrategyType,
    RiskLevel, BudgetStatus
)

@dataclass
class AssetCost:
    triangle_count: int = 80
    vertex_count: int = 48
    mesh_count: int = 1
    material_count: int = 1
    texture_count: int = 1
    texture_memory_mb: float = 16.0
    estimated_draw_calls: int = 1
    total_cost_index: float = 100.0

@dataclass
class OptimizationProfile:
    profile_id: str = "DEFAULT_OPTIMIZATION_PC"
    version: str = "1.0.0"
    target_platform: TargetPlatform = TargetPlatform.PC
    target_engine: TargetEngine = TargetEngine.UNREAL_ENGINE
    objective: OptimizationObjective = OptimizationObjective.BALANCED
    polygon_budget: int = 10000
    vertex_budget: int = 6000
    material_budget: int = 4
    texture_memory_budget_mb: float = 64.0
    visual_degradation_limit: float = 0.05 # max 5% loss
    semantic_degradation_limit: float = 0.00
    nanite_policy: NanitePolicy = NanitePolicy.NANITE_PREFERRED
    collision_policy: CollisionPolicy = CollisionPolicy.CUSTOM_UCX
    enabled_strategies: List[StrategyType] = field(default_factory=lambda: [
        StrategyType.MESH_SIMPLIFICATION,
        StrategyType.MATERIAL_OPTIMIZATION,
        StrategyType.TEXTURE_OPTIMIZATION,
        StrategyType.LOD_GENERATION
    ])

@dataclass
class OptimizationOpportunity:
    opportunity_id: str
    strategy_type: StrategyType
    target: str
    estimated_gain: float
    estimated_cost: float
    visual_risk: RiskLevel
    priority: int = 1

@dataclass
class OptimizationCandidate:
    candidate_id: str
    parent_state_hash: str
    state_hash: str
    strategy_type: StrategyType
    parameters: Dict[str, Any] = field(default_factory=dict)
    cost_before: AssetCost = field(default_factory=AssetCost)
    cost_after: AssetCost = field(default_factory=AssetCost)
    visual_delta: float = 0.0 # e.g. -0.01 (-1%)
    technical_delta: float = 0.0
    memory_delta: float = 0.0
    performance_delta: float = 0.0
    accepted: bool = True
    rejection_reason: Optional[str] = None

@dataclass
class OptimizationSession:
    session_id: str
    asset_id: str
    semantic_id: str
    profile_id: str
    baseline_cost: AssetCost = field(default_factory=AssetCost)
    baseline_state_hash: str = ""
    candidates: List[OptimizationCandidate] = field(default_factory=list)
    selected_candidate: Optional[OptimizationCandidate] = None
    status: SessionStatus = SessionStatus.CREATED
    created_at: float = 0.0

@dataclass
class OptimizedAssetResult:
    asset_id: str
    semantic_id: str
    baseline_state_hash: str
    optimized_state_hash: str
    optimization_session_id: str
    optimization_profile_id: str
    selected_candidate_id: str
    baseline_cost: AssetCost
    optimized_cost: AssetCost
    visual_delta: float
    technical_delta: float
    semantic_delta: float
    performance_delta: float
    memory_delta: float
    lod_summary: Dict[str, Any] = field(default_factory=dict)
    optimization_status: str = "ACCEPTED"
    production_candidate: bool = True
    optimization_hash: str = ""
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
