from typing import Optional, Dict, Any
from ...strategy_learning import StrategyLearningAPI, StrategyOutcome

class StrategyLearningBridge:
    """Integrates with F78 Strategy Learning & Optimization."""

    def __init__(self, strat_api: Optional[StrategyLearningAPI] = None):
        self.strat = strat_api or StrategyLearningAPI()

    def record_production_outcome(self, outcome: StrategyOutcome):
        self.strat.record_outcome(outcome)
