from typing import Dict, Any, List
from ..core.optimization_schema import AssetCost, OptimizationOpportunity, OptimizationProfile
from ..strategies.strategy_registry import OptimizationStrategyRegistry

class OpportunityAnalyzer:
    @classmethod
    def find_opportunities(
        cls,
        current_cost: AssetCost,
        profile: OptimizationProfile,
        registry: OptimizationStrategyRegistry,
        context: Dict[str, Any]
    ) -> List[OptimizationOpportunity]:
        opportunities: List[OptimizationOpportunity] = []
        for strat_type in profile.enabled_strategies:
            strat = registry.get(strat_type)
            if strat:
                opps = strat.find_opportunities(current_cost, context)
                opportunities.extend(opps)
        
        # Sort by priority
        opportunities.sort(key=lambda o: o.priority)
        return opportunities
