from dataclasses import dataclass
from typing import Optional, Tuple
from .planner import ChangeBudget

class BudgetManager:
    @staticmethod
    def validate_budget(budget: Optional[ChangeBudget], operations_count: int, affected_objects_count: int) -> Tuple[bool, Optional[str]]:
        if not budget:
            return True, None

        if operations_count > budget.max_operations:
            return False, f"CHANGE_BUDGET_EXCEEDED: Plan contains {operations_count} operations, exceeding max limit of {budget.max_operations}."

        if affected_objects_count > budget.max_objects_affected:
            return False, f"CHANGE_BUDGET_EXCEEDED: Plan affects {affected_objects_count} objects, exceeding max limit of {budget.max_objects_affected}."

        return True, None
