from typing import Optional
from ..core.strategy_models import StrategyRecord

class StrategyGuard:
    """Enforces immutability of protected system-level strategies."""

    PROTECTED_STRATEGIES = {"SYSTEM_DEFAULT_STRATEGY", "GOLDEN_BASELINE_STRATEGY"}

    @classmethod
    def can_modify_strategy(cls, strategy_id: str) -> bool:
        return strategy_id not in cls.PROTECTED_STRATEGIES

class RegressionGuard:
    """Detects and flags strategies that trigger quality drops against baselines."""

    @staticmethod
    def is_regression(new_score: float, baseline_score: float) -> bool:
        return (new_score - baseline_score) < -0.05
