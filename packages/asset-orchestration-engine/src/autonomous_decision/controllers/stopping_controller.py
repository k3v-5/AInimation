from typing import Tuple
from .budget_controller import BudgetController
from .loop_controller import LoopController
from ..evaluation.goal_evaluator import GoalEvaluator
from ...visual_intelligence.qa.quality_scorer import VerificationReport

class StoppingController:
    def __init__(
        self,
        goal_evaluator: GoalEvaluator,
        budget_controller: BudgetController
    ):
        self.goal_eval = goal_evaluator
        self.budget_ctrl = budget_controller
        self.emergency_stop_triggered = False

    def should_stop(
        self,
        report: VerificationReport,
        iterations: int,
        corrections: int,
        regenerations: int,
        action_history: list,
        score_deltas: list
    ) -> Tuple[bool, str, str]: # (should_stop, final_state, reason)
        # 1. Parada de Emergencia
        if self.emergency_stop_triggered:
            return True, "ABORTED", "EMERGENCY_STOP: Emergency stop explicitly triggered."

        # 2. Objetivo Cumplido (Good Enough)
        ok_goal, msg_goal = self.goal_eval.is_goal_satisfied(report)
        if ok_goal:
            return True, "COMPLETED", msg_goal

        # 3. Presupuesto Agotado
        ok_budget, msg_budget = self.budget_ctrl.can_continue(iterations, corrections, regenerations)
        if not ok_budget:
            return True, "FAILED", msg_budget

        # 4. Oscilación / Bucle Infinito
        is_osc, msg_osc = LoopController.check_oscillation(action_history)
        if is_osc:
            return True, "FAILED", msg_osc

        # 5. Falta de Progreso
        is_no_prog, msg_no_prog = LoopController.check_no_progress(score_deltas)
        if is_no_prog:
            return True, "FAILED", msg_no_prog

        return False, "CORRECTING", "CONTINUE_OPTIMIZATION"
