from typing import Optional, Dict, Any
from ...strategy_learning import StrategyLearningAPI, StrategyOutcome

class StrategyLearningBridge:
    """Feeds chosen optimization outcomes into F78 Strategy Learning System."""

    def __init__(self, strat_api: Optional[StrategyLearningAPI] = None):
        self.strat_api = strat_api or StrategyLearningAPI()

    def record_optimization_outcome(self, outcome: StrategyOutcome):
        self.strat_api.record_outcome(outcome)
