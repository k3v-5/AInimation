from typing import Dict, Any, List
from ..core.optimization_types import StrategyType, RiskLevel
from ..core.optimization_schema import OptimizationOpportunity, OptimizationCandidate, AssetCost
from .base_strategy import IOptimizationStrategy

class LODGenerationStrategy(IOptimizationStrategy):
    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.LOD_GENERATION

    def find_opportunities(self, asset_cost: AssetCost, context: Dict[str, Any]) -> List[OptimizationOpportunity]:
        return [
            OptimizationOpportunity(
                opportunity_id="OPP_LOD_GEN",
                strategy_type=self.strategy_type,
                target="mesh.lods",
                estimated_gain=0.60,
                estimated_cost=0.02,
                visual_risk=RiskLevel.LOW,
                priority=1
            )
        ]

    def execute_optimization(
        self,
        opportunity: OptimizationOpportunity,
        current_cost: AssetCost,
        context: Dict[str, Any]
    ) -> OptimizationCandidate:
        base_tris = current_cost.triangle_count
        lods = {
            "LOD0": {"triangles": base_tris, "screen_size": 1.0, "reduction": 1.0},
            "LOD1": {"triangles": int(base_tris * 0.50), "screen_size": 0.5, "reduction": 0.50},
            "LOD2": {"triangles": int(base_tris * 0.25), "screen_size": 0.2, "reduction": 0.25},
            "LOD3": {"triangles": int(base_tris * 0.10), "screen_size": 0.05, "reduction": 0.10}
        }

        cost_after = AssetCost(
            triangle_count=current_cost.triangle_count,
            vertex_count=current_cost.vertex_count,
            mesh_count=current_cost.mesh_count,
            material_count=current_cost.material_count,
            texture_count=current_cost.texture_count,
            texture_memory_mb=current_cost.texture_memory_mb,
            estimated_draw_calls=current_cost.estimated_draw_calls,
            total_cost_index=round(current_cost.total_cost_index * 0.70, 2)
        )

        return OptimizationCandidate(
            candidate_id="CAND_LOD_GEN_01",
            parent_state_hash="HASH_PARENT",
            state_hash="HASH_LOD_GENERATED",
            strategy_type=self.strategy_type,
            parameters={"lods": lods},
            cost_before=current_cost,
            cost_after=cost_after,
            visual_delta=0.0,
            technical_delta=0.0,
            memory_delta=0.0,
            performance_delta=+0.30,
            accepted=True
        )
