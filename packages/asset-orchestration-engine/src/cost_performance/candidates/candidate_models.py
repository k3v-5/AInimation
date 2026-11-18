from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from ..core.cost_models import CostReport
from ..core.performance_models import PerformanceReport
from ..core.budget_models import BudgetStatus

class CandidateStatus(str, Enum):
    PROPOSED = "PROPOSED"
    EVALUATED = "EVALUATED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"

@dataclass
class CandidateStrategy:
    candidate_id: str
    strategy_name: str
    target_polygon_budget: int = 15000
    target_material_budget: int = 2
    target_texture_resolution: str = "2K"
    lod_policy: str = "3_LEVELS"
    collision_policy: str = "UCX_CONVEX"
    nanite_policy: str = "AUTO"
    quality_score: float = 0.90
    visual_score: float = 0.90
    geometry_score: float = 0.90
    material_score: float = 0.90
    engine_readiness_score: float = 0.95
    cost_report: CostReport = field(default_factory=CostReport)
    performance_report: PerformanceReport = field(default_factory=PerformanceReport)
    budget_status: BudgetStatus = BudgetStatus.WITHIN_BUDGET
    status: CandidateStatus = CandidateStatus.PROPOSED
    rejection_reason: Optional[str] = None
    is_pareto_optimal: bool = False
    optimization_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "strategy_name": self.strategy_name,
            "target_polygon_budget": self.target_polygon_budget,
            "target_material_budget": self.target_material_budget,
            "target_texture_resolution": self.target_texture_resolution,
            "lod_policy": self.lod_policy,
            "collision_policy": self.collision_policy,
            "nanite_policy": self.nanite_policy,
            "quality_score": round(self.quality_score, 4),
            "visual_score": round(self.visual_score, 4),
            "geometry_score": round(self.geometry_score, 4),
            "material_score": round(self.material_score, 4),
            "engine_readiness_score": round(self.engine_readiness_score, 4),
            "total_cost": round(self.cost_report.total_cost, 4),
            "memory_mb": round(self.performance_report.asset_memory_estimate_mb, 4),
            "generation_time": round(self.cost_report.generation_time, 4),
            "budget_status": self.budget_status.value,
            "status": self.status.value,
            "rejection_reason": self.rejection_reason,
            "is_pareto_optimal": self.is_pareto_optimal,
            "optimization_score": round(self.optimization_score, 4)
        }
