from typing import Dict, Any, List, Optional
from ..core.strategy_models import StrategyRecord

class StrategyHistory:
    """Manages versioned repository of generation strategies."""

    def __init__(self):
        self._strategies: Dict[str, StrategyRecord] = {}

    def register_strategy(self, strategy: StrategyRecord):
        self._strategies[strategy.strategy_id] = strategy

    def get_strategy(self, strategy_id: str) -> Optional[StrategyRecord]:
        return self._strategies.get(strategy_id)

    def list_strategies(self, asset_type: Optional[str] = None) -> List[StrategyRecord]:
        if asset_type:
            return [s for s in self._strategies.values() if s.asset_type == asset_type]
        return list(self._strategies.values())

    def update_strategy(self, strategy: StrategyRecord):
        self._strategies[strategy.strategy_id] = strategy
