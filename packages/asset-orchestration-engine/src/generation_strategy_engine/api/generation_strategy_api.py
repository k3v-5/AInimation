import time
from typing import Dict, Any, List, Optional, Tuple
from ..core.strategy_types import (
    GenerationStrategyType, AssetComplexityLevel, FailureCategory, StageType
)
from ..core.strategy_schema import (
    GenerationStrategy, CandidateStrategy, GenerationPlan, GenerationStage,
    StrategyDecisionRecord, AssetComplexityReport, ReuseAnalysisReport
)
from ..engine.strategy_selector import StrategySelector

class GenerationStrategyAPI:
    """
    Asset Generation Strategy Engine API (AOE v52)
    
    Regla Fundamental:
    EL SISTEMA DEJA DE PREGUNTARSE ÚNICAMENTE "QUÉ HAY QUE CREAR"
    Y DECIDE SISTEMÁTICAMENTE "CUÁL ES LA MEJOR MANERA DE CREARLO",
    ELIMINANDO LA IMPROVISACIÓN DE LA IA SOBRE EL MCP DE BLENDER.
    """
    def __init__(self):
        self.selector = StrategySelector()

    def select_strategy(
        self,
        asset_class: str,
        components_count: int,
        batch_size: int = 1,
        existing_library: Optional[Dict[str, Dict[str, Any]]] = None,
        intent_type: str = "CREATE",
        force_strategy: Optional[GenerationStrategyType] = None,
        expected_frequent_revisions: bool = True
    ) -> Tuple[GenerationStrategyType, StrategyDecisionRecord]:
        strat, scores, override, reason = self.selector.select_strategy(
            asset_class=asset_class,
            components_count=components_count,
            batch_size=batch_size,
            existing_library=existing_library,
            intent_type=intent_type,
            force_strategy=force_strategy,
            expected_frequent_revisions=expected_frequent_revisions
        )
        record = StrategyDecisionRecord(
            decision_id=f"DEC_{int(time.time()*1000)}" if 'time' in globals() else "DEC_001",
            chosen_strategy=strat,
            candidate_scores=scores,
            override_applied=override,
            reason=reason
        )
        return strat, record

    def build_plan(
        self,
        specification_id: str,
        selected_strategy: GenerationStrategyType,
        parameters: Dict[str, Any],
        seed: int = 1337
    ) -> GenerationPlan:
        return self.selector.build_generation_plan(specification_id, selected_strategy, parameters, seed)

    def record_failure(self, asset_class: str, strategy: GenerationStrategyType, category: FailureCategory):
        self.selector.record_strategy_failure(asset_class, strategy, category)
