from typing import Dict, Any, List
from ..core.optimization_types import StrategyType, RiskLevel
from ..core.optimization_schema import OptimizationOpportunity, OptimizationCandidate, AssetCost
from .base_strategy import IOptimizationStrategy

class TextureOptimizationStrategy(IOptimizationStrategy):
    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.TEXTURE_OPTIMIZATION

    def find_opportunities(self, asset_cost: AssetCost, context: Dict[str, Any]) -> List[OptimizationOpportunity]:
        opps: List[OptimizationOpportunity] = []
        if asset_cost.texture_memory_mb > 8.0:
            opps.append(OptimizationOpportunity(
                opportunity_id="OPP_TEX_DOWNSCALE",
                strategy_type=self.strategy_type,
                target="textures",
                estimated_gain=0.50, # 50% VRAM saved
                estimated_cost=0.01,
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
        new_vram = round(current_cost.texture_memory_mb * 0.50, 2)
        cost_after = AssetCost(
            triangle_count=current_cost.triangle_count,
            vertex_count=current_cost.vertex_count,
            mesh_count=current_cost.mesh_count,
            material_count=current_cost.material_count,
            texture_count=current_cost.texture_count,
            texture_memory_mb=new_vram,
            estimated_draw_calls=current_cost.estimated_draw_calls,
            total_cost_index=round(current_cost.total_cost_index * 0.80, 2)
        )

        return OptimizationCandidate(
            candidate_id="CAND_TEX_DOWNSCALE_01",
            parent_state_hash="HASH_PARENT",
            state_hash="HASH_TEX_DOWNSCALED",
            strategy_type=self.strategy_type,
            parameters={"max_resolution": 1024, "channel_pack": True},
            cost_before=current_cost,
            cost_after=cost_after,
            visual_delta=-0.005,
            technical_delta=0.0,
            memory_delta=round(current_cost.texture_memory_mb - new_vram, 2),
            performance_delta=+0.10,
            accepted=True
        )
