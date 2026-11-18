from dataclasses import dataclass
from typing import Tuple

@dataclass
class CorrectionBudget:
    max_iterations: int = 10
    max_corrections: int = 6
    max_regenerations: int = 2

class BudgetController:
    def __init__(self, budget: CorrectionBudget = None):
        self.budget = budget or CorrectionBudget()

    def can_continue(self, iterations: int, corrections: int, regenerations: int) -> Tuple[bool, str]:
        if iterations >= self.budget.max_iterations:
            return False, f"BUDGET_EXHAUSTED: Maximum iterations ({self.budget.max_iterations}) reached."
        if corrections >= self.budget.max_corrections:
            return False, f"BUDGET_EXHAUSTED: Maximum corrections ({self.budget.max_corrections}) reached."
        if regenerations >= self.budget.max_regenerations:
            return False, f"BUDGET_EXHAUSTED: Maximum regenerations ({self.budget.max_regenerations}) reached."
        return True, ""
