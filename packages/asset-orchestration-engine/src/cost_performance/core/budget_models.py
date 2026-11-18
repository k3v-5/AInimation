from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
from enum import Enum

class BudgetStatus(str, Enum):
    WITHIN_BUDGET = "WITHIN_BUDGET"
    NEAR_LIMIT = "NEAR_LIMIT"
    OVER_BUDGET = "OVER_BUDGET"

@dataclass
class BudgetLimits:
    polygon_budget: int = 20000
    material_budget: int = 4
    texture_memory_budget_mb: float = 32.0
    asset_memory_budget_mb: float = 35.0
    generation_time_budget_sec: float = 60.0
    disk_budget_mb: float = 25.0
    collision_budget_hulls: int = 12

    def check(self, candidate_metrics: Dict[str, Any]) -> Tuple[BudgetStatus, Dict[str, BudgetStatus]]:
        breakdown: Dict[str, BudgetStatus] = {}

        # 1. Polygons
        polys = candidate_metrics.get("triangle_count", candidate_metrics.get("polygon_count", 0))
        if polys > self.polygon_budget:
            breakdown["polygon"] = BudgetStatus.OVER_BUDGET
        elif polys > self.polygon_budget * 0.85:
            breakdown["polygon"] = BudgetStatus.NEAR_LIMIT
        else:
            breakdown["polygon"] = BudgetStatus.WITHIN_BUDGET

        # 2. Materials
        mats = candidate_metrics.get("material_count", 0)
        if mats > self.material_budget:
            breakdown["material"] = BudgetStatus.OVER_BUDGET
        elif mats == self.material_budget:
            breakdown["material"] = BudgetStatus.NEAR_LIMIT
        else:
            breakdown["material"] = BudgetStatus.WITHIN_BUDGET

        # 3. Texture Memory
        tex_mem = candidate_metrics.get("texture_memory_mb", 0.0)
        if tex_mem > self.texture_memory_budget_mb:
            breakdown["texture_memory"] = BudgetStatus.OVER_BUDGET
        elif tex_mem > self.texture_memory_budget_mb * 0.85:
            breakdown["texture_memory"] = BudgetStatus.NEAR_LIMIT
        else:
            breakdown["texture_memory"] = BudgetStatus.WITHIN_BUDGET

        # 4. Generation Time
        gen_time = candidate_metrics.get("generation_time", 0.0)
        if gen_time > self.generation_time_budget_sec:
            breakdown["generation_time"] = BudgetStatus.OVER_BUDGET
        elif gen_time > self.generation_time_budget_sec * 0.85:
            breakdown["generation_time"] = BudgetStatus.NEAR_LIMIT
        else:
            breakdown["generation_time"] = BudgetStatus.WITHIN_BUDGET

        # Overall Status
        if any(s == BudgetStatus.OVER_BUDGET for s in breakdown.values()):
            overall = BudgetStatus.OVER_BUDGET
        elif any(s == BudgetStatus.NEAR_LIMIT for s in breakdown.values()):
            overall = BudgetStatus.NEAR_LIMIT
        else:
            overall = BudgetStatus.WITHIN_BUDGET

        return overall, breakdown

    def to_dict(self) -> Dict[str, Any]:
        return {
            "polygon_budget": self.polygon_budget,
            "material_budget": self.material_budget,
            "texture_memory_budget_mb": self.texture_memory_budget_mb,
            "asset_memory_budget_mb": self.asset_memory_budget_mb,
            "generation_time_budget_sec": self.generation_time_budget_sec,
            "disk_budget_mb": self.disk_budget_mb,
            "collision_budget_hulls": self.collision_budget_hulls
        }
