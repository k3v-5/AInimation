import copy
from typing import List, Dict, Any, Optional
from ..core.critic_types import BudgetStatus, CriticStatus
from ..core.critic_schema import CriticPolicy, CandidateBranch, CorrectionPlan

class IterationController:
    def __init__(self, policy: Optional[CriticPolicy] = None):
        self.policy = policy or CriticPolicy()
        self.iteration = 0
        self.current_cost = 0
        self.score_history: List[float] = []

    def check_budget(self) -> BudgetStatus:
        if self.iteration >= self.policy.max_iterations:
            return BudgetStatus.BUDGET_EXCEEDED
        if self.current_cost >= self.policy.max_cost:
            return BudgetStatus.BUDGET_EXCEEDED
        return BudgetStatus.OK

    def record_iteration(self, score: float, cost: int = 1):
        self.iteration += 1
        self.current_cost += cost
        self.score_history.append(score)

    def is_plateau(self, patience: int = 3) -> bool:
        if len(self.score_history) < patience:
            return False
        recent = self.score_history[-patience:]
        return all(abs(recent[i] - recent[0]) < self.policy.minimum_improvement for i in range(1, len(recent)))

    def is_oscillating(self) -> bool:
        if len(self.score_history) < 4:
            return False
        deltas = [self.score_history[i+1] - self.score_history[i] for i in range(len(self.score_history)-1)]
        signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in deltas]
        for i in range(len(signs) - 2):
            if signs[i] != 0 and signs[i] == -signs[i+1] and signs[i+1] == -signs[i+2]:
                return True
        return False

    @staticmethod
    def select_best_candidate(candidates: List[CandidateBranch]) -> CandidateBranch:
        return max(candidates, key=lambda c: c.predicted_score)
