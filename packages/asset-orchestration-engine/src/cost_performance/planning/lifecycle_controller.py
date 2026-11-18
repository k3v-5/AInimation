from typing import Dict, Any, Optional
from enum import Enum
from .optimization_plan import OptimizationPlan
from ..candidates.candidate_models import CandidateStatus

class LifecycleStage(str, Enum):
    ANALYZE = "ANALYZE"
    SIMULATE = "SIMULATE"
    RECOMMEND = "RECOMMEND"
    APPLY = "APPLY"
    VALIDATE = "VALIDATE"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"

class LifecycleController:
    """Manages atomic state progression of asset optimization runs."""

    def __init__(self, plan: OptimizationPlan):
        self.plan = plan
        self.current_stage = LifecycleStage.ANALYZE
        self.is_committed = False
        self.is_rolled_back = False

    def advance_to_simulate(self):
        self.current_stage = LifecycleStage.SIMULATE

    def advance_to_recommend(self):
        self.current_stage = LifecycleStage.RECOMMEND

    def advance_to_apply(self):
        self.current_stage = LifecycleStage.APPLY

    def advance_to_validate(self):
        self.current_stage = LifecycleStage.VALIDATE

    def commit(self):
        self.current_stage = LifecycleStage.COMMIT
        self.is_committed = True
        if self.plan.selected_strategy_id:
            for c in self.plan.candidate_strategies:
                if c.candidate_id == self.plan.selected_strategy_id:
                    c.status = CandidateStatus.COMMITTED

    def rollback(self, reason: str = "Validation failure or regression"):
        self.current_stage = LifecycleStage.ROLLBACK
        self.is_rolled_back = True
        if self.plan.selected_strategy_id:
            for c in self.plan.candidate_strategies:
                if c.candidate_id == self.plan.selected_strategy_id:
                    c.status = CandidateStatus.ROLLED_BACK
                    c.rejection_reason = reason
