from typing import Dict, Any, List, Optional
from ..core.msp_types import (
    AssetCategoryTag, ComponentConstructionMethod, BasePrimitiveType,
    GeometricOperationType, SymmetryType, DetailLevel, CollisionStrategyType,
    PivotStrategyType, StrategyRiskLevel, ReuseStrategyType
)
from ..core.msp_schema import (
    ParametricSpec, GeometricOperation, ModifierStrategySpec,
    GeometryNodesStrategySpec, ComponentStrategy, GlobalStrategySpec,
    GeometryBudgetDistribution, CostEstimate, ModelingStrategyPlan,
    StrategyValidationResult
)
from ..engine.procedural_modeling_strategy_engine import ProceduralModelingStrategyEngine

class ProceduralModelingStrategyAPI:
    """
    Procedural Modeling Strategy Engine API (AOE v57)
    
    Regla Fundamental:
    DECIDE CÓMO CONSTRUIR CADA PARTE DEL ASSET MEDIANTE UN ModelingStrategyPlan (MSP)
    ESTRUCTURADO Y DETERMINISTA, SIN ACOPLE A BLENDER DIRECTO NI A MCP.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = ProceduralModelingStrategyEngine(engine_version=engine_version)

    def plan_strategy(
        self,
        specification: Any,
        project_config: Optional[Dict[str, Any]] = None
    ) -> ModelingStrategyPlan:
        return self._engine.plan(specification, project_config)

    def validate_plan(self, plan: ModelingStrategyPlan) -> StrategyValidationResult:
        return self._engine.validate(plan)

    def rank_strategies(self, candidates: List[ModelingStrategyPlan]) -> List[ModelingStrategyPlan]:
        return self._engine.rank_strategies(candidates)

    def estimate_cost(self, plan: ModelingStrategyPlan) -> CostEstimate:
        return self._engine.estimate_cost(plan)

    def compute_hash(self, plan: ModelingStrategyPlan) -> str:
        return self._engine.compute_hash(plan)
