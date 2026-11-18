from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .critic_types import (
    CausalCategory, CriticPriority, RiskLevel, IterationRecommendation,
    EvidenceType, ActionAutonomyLevel, ConflictSeverity
)

@dataclass
class EvidenceItem:
    evidence_type: EvidenceType
    source: str # e.g. "F61_VISUAL_EVAL", "F62_GEOMETRY_QA", "F56_VAS"
    description: str
    metric_value: Any = None
    confidence: float = 0.95

@dataclass
class RequirementDeviation:
    requirement_id: str
    expected: Any
    actual: Any
    absolute_error: float = 0.0
    relative_error: float = 0.0
    tolerance: float = 0.05
    severity: str = "MODERATE"

@dataclass
class RootCause:
    cause_id: str
    category: CausalCategory
    description: str
    evidence: List[EvidenceItem] = field(default_factory=list)
    probability: float = 0.90
    affected_requirements: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    related_parameters: List[str] = field(default_factory=list)
    correction_candidates: List[str] = field(default_factory=list)

@dataclass
class DefectCluster:
    cluster_id: str
    name: str # e.g. "PROPORTION_AND_PLACEMENT_UPPER_BODY"
    primary_category: CausalCategory
    visual_defects: List[str] = field(default_factory=list)
    geometric_defects: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    root_cause_id: Optional[str] = None

@dataclass
class CriticDiagnosis:
    diagnosis_id: str
    category: CausalCategory
    severity: str = "MODERATE"
    priority: CriticPriority = CriticPriority.MEDIUM
    affected_components: List[str] = field(default_factory=list)
    affected_regions: List[str] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)
    probable_causes: List[RootCause] = field(default_factory=list)
    confidence: float = 0.95
    downstream_impact: str = "LOCAL"
    recommended_action: str = "ADJUST_PARAMETER"

@dataclass
class ParameterRecommendation:
    parameter_id: str
    current_value: Any
    recommended_value: Any
    recommended_range: Optional[Tuple[float, float]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    delta: float = 0.0
    confidence: float = 0.95
    reason: str = "ALIGNMENT_WITH_VAS"
    evidence: List[str] = field(default_factory=list)

@dataclass
class CorrectionAction:
    action_id: str
    target: str # e.g. "component.part_body"
    parameter: str # e.g. "width_scale"
    current_value: Any = None
    proposed_value: Any = None
    delta: float = 0.0
    reason: str = "CORRECT_SILHOUETTE_PROPORTION"
    evidence: List[str] = field(default_factory=list)
    expected_improvement: float = 0.15
    risk: RiskLevel = RiskLevel.LOW
    autonomy_level: ActionAutonomyLevel = ActionAutonomyLevel.AUTONOMOUSLY_ACTIONABLE
    dependencies: List[str] = field(default_factory=list)

@dataclass
class CorrectionPlan:
    plan_id: str = "PLAN_DEFAULT"
    ordered_actions: List[CorrectionAction] = field(default_factory=list)
    expected_effect: str = "RESTORE_VISUAL_AND_GEOMETRIC_ALIGNMENT"
    confidence: float = 0.95
    estimated_cost: float = 1.0
    regression_risk: RiskLevel = RiskLevel.LOW
    dependencies: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class CriticConflict:
    conflict_id: str
    objectives: List[str] = field(default_factory=list)
    competing_constraints: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    severity: ConflictSeverity = ConflictSeverity.MODERATE
    recommended_resolution: str = "PRIORITIZE_STRUCTURAL_ACCURACY"

@dataclass
class DiagnosticGraph:
    nodes: List[Dict[str, Any]] = field(default_factory=list) # {id, type, label}
    edges: List[Dict[str, Any]] = field(default_factory=list) # {source, target, relation}

@dataclass
class CriticConfiguration:
    profile: str = "PRODUCTION"
    enabled_rules: List[str] = field(default_factory=lambda: [
        "CAUSAL_PROPORTION", "CAUSAL_TOPOLOGY", "CAUSAL_MATERIAL", "HISTORICAL_OSCILLATION", "HISTORICAL_STAGNATION"
    ])
    stagnation_threshold: int = 3
    oscillation_threshold: int = 2
    priority_weights: Dict[str, float] = field(default_factory=lambda: {
        "impact": 0.4, "dependency": 0.3, "confidence": 0.2, "cost": 0.1
    })

@dataclass
class IntelligentCriticResult:
    critic_id: str = "CRITIC_DEFAULT"
    semantic_id: str = "asset.root"
    asset_id: str = "asset.root"
    iteration_index: int = 1
    diagnoses: List[CriticDiagnosis] = field(default_factory=list)
    root_causes: List[RootCause] = field(default_factory=list)
    defect_clusters: List[DefectCluster] = field(default_factory=list)
    priority_order: List[str] = field(default_factory=list)
    correction_plan: CorrectionPlan = field(default_factory=CorrectionPlan)
    parameter_recommendations: List[ParameterRecommendation] = field(default_factory=list)
    conflicts: List[CriticConflict] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    confidence: float = 0.98
    risk_analysis: Dict[str, RiskLevel] = field(default_factory=lambda: {
        "regression_risk": RiskLevel.LOW,
        "semantic_risk": RiskLevel.LOW,
        "topology_risk": RiskLevel.LOW
    })
    iteration_recommendation: IterationRecommendation = IterationRecommendation.CONTINUE
    acceptance_blockers: List[str] = field(default_factory=list)
    quality_summary: Dict[str, float] = field(default_factory=dict)
    critic_hash: str = ""
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CriticValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
