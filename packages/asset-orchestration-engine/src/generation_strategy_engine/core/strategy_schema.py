from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .strategy_types import (
    GenerationStrategyType, AssetComplexityLevel, FailureCategory, StageType
)

@dataclass
class GenerationStrategy:
    strategy_id: str
    strategy_type: GenerationStrategyType
    target_asset_classes: List[str]
    quality_score: float = 0.90
    reliability_score: float = 0.95
    editability_score: float = 0.90
    base_cost: float = 1.0
    supported_features: List[str] = field(default_factory=lambda: ["dimensions", "materials", "semantic_components"])

@dataclass
class CandidateStrategy:
    strategy: GenerationStrategy
    total_score: float
    expected_rework_cost: float
    is_suitable: bool = True
    rejection_reason: Optional[str] = None

@dataclass
class GenerationStage:
    stage_id: str
    stage_type: StageType
    order: int
    description: str
    quality_gates: Dict[str, float] = field(default_factory=dict)
    required_capabilities: List[str] = field(default_factory=list)

@dataclass
class GenerationCheckpoint:
    checkpoint_id: str
    stage_type: StageType
    seed: int
    timestamp: float
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationPlan:
    plan_id: str
    specification_id: str
    selected_strategy: GenerationStrategyType
    stages: List[GenerationStage]
    parameters: Dict[str, Any]
    seed: int = 1337
    fallback_strategy: Optional[GenerationStrategyType] = None
    is_deterministic: bool = True

@dataclass
class StrategyDecisionRecord:
    decision_id: str
    chosen_strategy: GenerationStrategyType
    candidate_scores: Dict[str, float]
    override_applied: bool = False
    reason: str = ""

@dataclass
class AssetComplexityReport:
    asset_class: str
    complexity_level: AssetComplexityLevel
    component_count: int
    is_batch: bool = False
    batch_size: int = 1
    repeatability: str = "SINGLE"

@dataclass
class ReuseAnalysisReport:
    has_match: bool
    matched_asset_id: Optional[str] = None
    similarity_score: float = 0.0
    recommended_action: str = "FULL_GENERATION"
