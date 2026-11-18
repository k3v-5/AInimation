from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List
from ..core.optimization_types import StrategyType, RiskLevel
from ..core.optimization_schema import OptimizationOpportunity, OptimizationCandidate, AssetCost

class IOptimizationStrategy(ABC):
    @property
    @abstractmethod
    def strategy_type(self) -> StrategyType:
        pass

    @abstractmethod
    def find_opportunities(self, asset_cost: AssetCost, context: Dict[str, Any]) -> List[OptimizationOpportunity]:
        pass

    @abstractmethod
    def execute_optimization(
        self,
        opportunity: OptimizationOpportunity,
        current_cost: AssetCost,
        context: Dict[str, Any]
    ) -> OptimizationCandidate:
        pass
