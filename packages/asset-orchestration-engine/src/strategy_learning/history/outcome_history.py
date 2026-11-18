from typing import List, Dict, Any, Optional
from ..core.learning_models import StrategyOutcome

class OutcomeHistory:
    """Stores all executed strategy outcomes across all assets and runs."""

    def __init__(self):
        self._outcomes: List[StrategyOutcome] = []

    def record_outcome(self, outcome: StrategyOutcome):
        self._outcomes.append(outcome)

    def get_outcomes_for_strategy(self, strategy_id: str) -> List[StrategyOutcome]:
        return [o for o in self._outcomes if o.strategy_id == strategy_id]

    def get_outcomes_for_semantic_id(self, semantic_id: str) -> List[StrategyOutcome]:
        return [o for o in self._outcomes if o.semantic_id == semantic_id]

    def list_all(self) -> List[StrategyOutcome]:
        return list(self._outcomes)
