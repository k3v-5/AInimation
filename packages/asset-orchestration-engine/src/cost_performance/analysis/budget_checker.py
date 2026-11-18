from typing import Dict, Any, Tuple
from ..core.budget_models import BudgetLimits, BudgetStatus

class BudgetChecker:
    """Validates candidate metrics against defined budget limits."""

    @staticmethod
    def check_budgets(limits: BudgetLimits, candidate: Dict[str, Any]) -> Tuple[BudgetStatus, Dict[str, BudgetStatus]]:
        return limits.check(candidate)
