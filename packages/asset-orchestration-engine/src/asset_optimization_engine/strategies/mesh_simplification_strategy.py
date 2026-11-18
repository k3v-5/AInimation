from typing import Dict, Any, List
from ..core.optimization_types import StrategyType, RiskLevel
from ..core.optimization_schema import OptimizationOpportunity, OptimizationCandidate, AssetCost
from .base_strategy import IOptimizationStrategy

class MeshSimplificationStrategy(IOptimizationStrategy):
    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.MESH_SIMPLIFICATION

    def find_opportunities(self, asset_cost: AssetCost, context: Dict[str, Any]) -> List[OptimizationOpportunity]:
        opps: List[OptimizationOpportunity] = []
        if asset_cost.triangle_count > 60:
            opps.append(OptimizationOpportunity(
                opportunity_id="OPP_MESH_SIMPLIFY",
                strategy_type=self.strategy_type,
                target="mesh.root",
                estimated_gain=0.30, # 30% reduction
                estimated_cost=0.01,
                visual_risk=RiskLevel.LOW,
                priority=1
            ))
        return opps

    def execute_optimization(
        self,
        opportunity: OptimizationOpportunity,
        current_cost: AssetCost,
        context: Dict[str, Any]
    ) -> OptimizationCandidate:
        new_triangles = int(current_cost.triangle_count * 0.70)
        new_vertices = int(current_cost.vertex_count * 0.70)
        
        cost_after = AssetCost(
            triangle_count=new_triangles,
            vertex_count=new_vertices,
            mesh_count=current_cost.mesh_count,
            material_count=current_cost.material_count,
            texture_count=current_cost.texture_count,
            texture_memory_mb=current_cost.texture_memory_mb,
            estimated_draw_calls=current_cost.estimated_draw_calls,
            total_cost_index=round(current_cost.total_cost_index * 0.75, 2)
        )

        return OptimizationCandidate(
            candidate_id="CAND_MESH_SIMPLIFY_01",
            parent_state_hash="HASH_PARENT",
            state_hash="HASH_MESH_SIMPLIFIED",
            strategy_type=self.strategy_type,
            parameters={"decimate_ratio": 0.70},
            cost_before=current_cost,
            cost_after=cost_after,
            visual_delta=-0.005, # negligible 0.5% loss
            technical_delta=0.0,
            memory_delta=0.0,
            performance_delta=+0.25,
            accepted=True
        )
