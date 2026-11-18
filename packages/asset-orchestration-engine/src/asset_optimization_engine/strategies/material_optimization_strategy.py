from typing import Dict, Any, List
from ..core.optimization_types import StrategyType, RiskLevel
from ..core.optimization_schema import OptimizationOpportunity, OptimizationCandidate, AssetCost
from .base_strategy import IOptimizationStrategy

class MaterialOptimizationStrategy(IOptimizationStrategy):
    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.MATERIAL_OPTIMIZATION

    def find_opportunities(self, asset_cost: AssetCost, context: Dict[str, Any]) -> List[OptimizationOpportunity]:
        opps: List[OptimizationOpportunity] = []
        if asset_cost.material_count > 1:
            opps.append(OptimizationOpportunity(
                opportunity_id="OPP_MAT_CONSOLIDATE",
                strategy_type=self.strategy_type,
                target="materials",
                estimated_gain=0.50,
                estimated_cost=0.0,
                visual_risk=RiskLevel.LOW,
                priority=2
            ))
        return opps

    def execute_optimization(
        self,
        opportunity: OptimizationOpportunity,
        current_cost: AssetCost,
        context: Dict[str, Any]
    ) -> OptimizationCandidate:
        cost_after = AssetCost(
            triangle_count=current_cost.triangle_count,
            vertex_count=current_cost.vertex_count,
            mesh_count=current_cost.mesh_count,
            material_count=max(1, current_cost.material_count - 1),
            texture_count=current_cost.texture_count,
            texture_memory_mb=current_cost.texture_memory_mb,
            estimated_draw_calls=max(1, current_cost.estimated_draw_calls - 1),
            total_cost_index=round(current_cost.total_cost_index * 0.85, 2)
        )

        return OptimizationCandidate(
            candidate_id="CAND_MAT_CONSOLIDATE_01",
            parent_state_hash="HASH_PARENT",
            state_hash="HASH_MAT_CONSOLIDATED",
            strategy_type=self.strategy_type,
            parameters={"consolidate_slots": True},
            cost_before=current_cost,
            cost_after=cost_after,
            visual_delta=0.0,
            technical_delta=0.0,
            memory_delta=0.0,
            performance_delta=+0.15,
            accepted=True
        )
