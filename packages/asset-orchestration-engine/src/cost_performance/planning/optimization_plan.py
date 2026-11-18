import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..candidates.candidate_models import CandidateStrategy
from ..core.quality_floor import QualityFloor
from ..core.optimization_profiles import OptimizationProfile
from ..core.budget_models import BudgetLimits

@dataclass
class OptimizationPlan:
    plan_id: str
    asset_semantic_id: str
    baseline: Dict[str, Any]
    candidate_strategies: List[CandidateStrategy] = field(default_factory=list)
    quality_floor: QualityFloor = field(default_factory=QualityFloor)
    optimization_profile: OptimizationProfile = field(default_factory=OptimizationProfile.balanced)
    budget_limits: BudgetLimits = field(default_factory=BudgetLimits)
    pareto_front_ids: List[str] = field(default_factory=list)
    selected_strategy_id: Optional[str] = None
    rejected_strategy_ids: List[str] = field(default_factory=list)
    rejection_reasons: Dict[str, str] = field(default_factory=dict)
    expected_delta: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.90
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "asset_semantic_id": self.asset_semantic_id,
            "baseline": self.baseline,
            "candidate_strategies": [c.to_dict() for c in self.candidate_strategies],
            "quality_floor": self.quality_floor.to_dict(),
            "optimization_profile": self.optimization_profile.to_dict(),
            "budget_limits": self.budget_limits.to_dict(),
            "pareto_front_ids": self.pareto_front_ids,
            "selected_strategy_id": self.selected_strategy_id,
            "rejected_strategy_ids": self.rejected_strategy_ids,
            "rejection_reasons": self.rejection_reasons,
            "expected_delta": self.expected_delta,
            "confidence": round(self.confidence, 4),
            "created_at": self.created_at
        }
