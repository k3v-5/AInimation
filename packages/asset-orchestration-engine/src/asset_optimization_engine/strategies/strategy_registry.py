from typing import Dict, List, Optional
from ..core.optimization_types import StrategyType
from .base_strategy import IOptimizationStrategy
from .mesh_simplification_strategy import MeshSimplificationStrategy
from .material_optimization_strategy import MaterialOptimizationStrategy
from .texture_optimization_strategy import TextureOptimizationStrategy
from .lod_generation_strategy import LODGenerationStrategy

class OptimizationStrategyRegistry:
    def __init__(self):
        self._strategies: Dict[StrategyType, IOptimizationStrategy] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(MeshSimplificationStrategy())
        self.register(MaterialOptimizationStrategy())
        self.register(TextureOptimizationStrategy())
        self.register(LODGenerationStrategy())

    def register(self, strategy: IOptimizationStrategy):
        self._strategies[strategy.strategy_type] = strategy

    def get(self, strategy_type: StrategyType) -> Optional[IOptimizationStrategy]:
        return self._strategies.get(strategy_type)

    def list_strategies(self) -> List[StrategyType]:
        return list(self._strategies.keys())
