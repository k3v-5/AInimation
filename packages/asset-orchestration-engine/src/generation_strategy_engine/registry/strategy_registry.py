from typing import Dict, Any, List, Optional
from ..core.strategy_types import GenerationStrategyType
from ..core.strategy_schema import GenerationStrategy

class GenerationStrategyRegistry:
    def __init__(self):
        self._strategies: Dict[GenerationStrategyType, GenerationStrategy] = {}
        self._init_standard_strategies()

    def _init_standard_strategies(self):
        standards = [
            GenerationStrategy(
                strategy_id="STRAT_SCRIPTED_MODELING",
                strategy_type=GenerationStrategyType.SCRIPTED_MODELING,
                target_asset_classes=["PROP.BARREL", "PROP.CRATE", "WEAPON.SWORD", "PROP", "WEAPON"],
                quality_score=0.92,
                reliability_score=0.98,
                editability_score=0.95,
                base_cost=1.2
            ),
            GenerationStrategy(
                strategy_id="STRAT_PROCEDURAL_GENERATION",
                strategy_type=GenerationStrategyType.PROCEDURAL_GENERATION,
                target_asset_classes=["PROP.BARREL", "PROP", "ENVIRONMENT", "VEGETATION"],
                quality_score=0.89,
                reliability_score=0.96,
                editability_score=0.88,
                base_cost=1.5
            ),
            GenerationStrategy(
                strategy_id="STRAT_COMPONENT_ASSEMBLY",
                strategy_type=GenerationStrategyType.COMPONENT_ASSEMBLY,
                target_asset_classes=["BUILDING.HOUSE", "BUILDING", "ARCHITECTURAL"],
                quality_score=0.94,
                reliability_score=0.97,
                editability_score=0.92,
                base_cost=1.8
            ),
            GenerationStrategy(
                strategy_id="STRAT_EXISTING_ASSET_MODIFICATION",
                strategy_type=GenerationStrategyType.EXISTING_ASSET_MODIFICATION,
                target_asset_classes=["PROP", "BUILDING", "WEAPON", "CHARACTER"],
                quality_score=0.96,
                reliability_score=0.99,
                editability_score=0.98,
                base_cost=0.5
            ),
            GenerationStrategy(
                strategy_id="STRAT_GEOMETRY_NODES",
                strategy_type=GenerationStrategyType.GEOMETRY_NODES,
                target_asset_classes=["ENVIRONMENT", "VEGETATION", "BUILDING", "PROP"],
                quality_score=0.91,
                reliability_score=0.94,
                editability_score=0.85,
                base_cost=1.4
            ),
            GenerationStrategy(
                strategy_id="STRAT_PRIMITIVE_COMPOSITION",
                strategy_type=GenerationStrategyType.PRIMITIVE_COMPOSITION,
                target_asset_classes=["PROP.SIMPLE", "PLACEHOLDER"],
                quality_score=0.70,
                reliability_score=0.80,
                editability_score=0.30, # Pobre editabilidad
                base_cost=0.8
            )
        ]
        for s in standards:
            self._strategies[s.strategy_type] = s

    def get_strategy(self, strategy_type: GenerationStrategyType) -> Optional[GenerationStrategy]:
        return self._strategies.get(strategy_type)

    def list_strategies(self) -> List[GenerationStrategy]:
        return list(self._strategies.values())
