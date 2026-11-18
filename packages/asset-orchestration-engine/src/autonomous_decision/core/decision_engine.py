import uuid
from typing import Dict, Any, Optional, List, Tuple
from ..state.decision_state import DecisionState, DecisionStateEnum
from ..evaluation.goal_evaluator import GoalEvaluator
from ..evaluation.progress_evaluator import ProgressEvaluator, ProgressClassification
from ..controllers.budget_controller import BudgetController, CorrectionBudget
from ..controllers.stopping_controller import StoppingController
from ..planning.action_planner import ActionPlanner
from .decision_logger import DecisionLogger, DecisionLogEntry
from ...visual_intelligence.api.visual_intelligence_api import VisualIntelligenceAPI
from ...visual_intelligence.core.visual_goal_builder import VisualGoalSpec
from ...correction_execution.api.correction_execution_api import CorrectionExecutionAPI
from ...memory.api.asset_memory_api import AssetMemoryAPI

class DecisionEngine:
    """
    Autonomous Asset Optimization & Decision Engine (AOE v13)
    
    Regla de Oro:
    LA IA PROPONE. EL MOTOR DECIDE. BLENDER EJECUTA. EL VALIDADOR COMPRUEBA. LA MEMORIA APRENDE.
    SI EL ASSET YA CUMPLE EL OBJETIVO (GOOD ENOUGH >= 0.85), NO HACER NADA MÁS (STOP).
    """
    def __init__(
        self,
        visual_api: VisualIntelligenceAPI,
        correction_api: CorrectionExecutionAPI,
        memory_api: Optional[AssetMemoryAPI] = None,
        acceptance_threshold: float = 0.85,
        budget: Optional[CorrectionBudget] = None
    ):
        self.visual_api = visual_api
        self.correction_api = correction_api
        self.memory_api = memory_api
        self.goal_eval = GoalEvaluator(acceptance_threshold=acceptance_threshold)
        self.budget_ctrl = BudgetController(budget=budget)
        self.stopping_ctrl = StoppingController(self.goal_eval, self.budget_ctrl)
        self.planner = ActionPlanner(memory_api=memory_api)
        self.logger = DecisionLogger()

    def optimize_asset_autonomously(
        self,
        asset_id: str,
        goal_spec: VisualGoalSpec,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        state = DecisionState(asset_id=asset_id, state=DecisionStateEnum.ANALYZING)
        action_history: List[str] = []
        score_deltas: List[float] = []

        # 1. Evaluación Inicial
        provider = self.correction_api.provider
        dims_init = {k: v["dimensions"] for k, v in provider.assets.get(asset_id, {}).get("components", {}).items()}
        mats_init = {k: v.get("material", {}) for k, v in provider.assets.get(asset_id, {}).get("components", {}).items()}
        report = self.visual_api.verify_asset(asset_id, dims_init, list(dims_init.keys()), materials=mats_init, goal_spec=goal_spec)
        state.current_score = report.overall_score
        state.best_score = report.overall_score

        # 2. Bucle Autónomo de Decisión y Optimización
        while True:
            state.iteration_count += 1

            # A. Comprobar si debemos detenernos (Goal Achieved, Budget, Oscillation, No Progress)
            should_stop, final_state_str, stop_reason = self.stopping_ctrl.should_stop(
                report=report,
                iterations=state.iteration_count,
                corrections=state.correction_count,
                regenerations=state.regeneration_count,
                action_history=action_history,
                score_deltas=score_deltas
            )

            if should_stop:
                state.state = DecisionStateEnum(final_state_str)
                return {
                    "success": (final_state_str == "COMPLETED"),
                    "status": final_state_str,
                    "final_score": state.current_score,
                    "iterations": state.iteration_count,
                    "corrections": state.correction_count,
                    "stop_reason": stop_reason,
                    "history": state.history
                }

            # B. Planificar Siguiente Acción basada en Utilidad
            state.state = DecisionStateEnum.PLANNING
            next_action = self.planner.plan_next_action(report, asset_type=goal_spec.category)
            if not next_action:
                state.state = DecisionStateEnum.FAILED
                return {"success": False, "status": "FAILED", "stop_reason": "NO_VIABLE_ACTION_CANDIDATE", "final_score": state.current_score}

            if dry_run:
                return {
                    "success": True,
                    "status": "dry_run",
                    "planned_action": next_action.operation_type,
                    "target": next_action.target,
                    "utility": next_action.utility,
                    "reason": next_action.reason
                }

            # C. Ejecutar Acción mediante Fase 11
            state.state = DecisionStateEnum.EXECUTING
            score_before = state.current_score
            exec_res = self.correction_api.execute_correction(
                asset_id=asset_id,
                operations=[{
                    "type": next_action.operation_type,
                    "target": next_action.target,
                    "parameters": next_action.parameters,
                    "reason": next_action.reason
                }]
            )
            state.correction_count += 1
            action_history.append(next_action.operation_type)

            # D. Validar Post-Mutación mediante Fase 10
            state.state = DecisionStateEnum.VALIDATING
            dims_cur = {k: v["dimensions"] for k, v in provider.assets.get(asset_id, {}).get("components", {}).items()}
            mats_cur = {k: v.get("material", {}) for k, v in provider.assets.get(asset_id, {}).get("components", {}).items()}
            report = self.visual_api.verify_asset(asset_id, dims_cur, list(dims_cur.keys()), materials=mats_cur, goal_spec=goal_spec)
            score_after = report.overall_score
            state.previous_score = score_before
            state.current_score = score_after

            # E. Evaluar Progreso y Registrar Memoria F12
            prog_class, delta = ProgressEvaluator.evaluate_progress(score_before, score_after)
            score_deltas.append(delta)

            if score_after > state.best_score:
                state.best_score = score_after

            if self.memory_api:
                self.memory_api.record_correction_outcome(
                    failure_id=f"fail_auto_{state.iteration_count}",
                    strategy_id=next_action.strategy_id,
                    operation_type=next_action.operation_type,
                    target=next_action.target,
                    parameters=next_action.parameters,
                    before_score=score_before,
                    after_score=score_after,
                    is_rollback=(prog_class == ProgressClassification.SEVERE_REGRESSION)
                )

            # F. Registrar Decisión
            log_entry = DecisionLogEntry(
                decision_id=f"dec_{uuid.uuid4().hex[:6]}",
                asset_id=asset_id,
                iteration=state.iteration_count,
                selected_action=next_action.operation_type,
                rejected_actions=[],
                reason=next_action.reason,
                utility=next_action.utility,
                score_before=score_before,
                score_after=score_after
            )
            self.logger.log(log_entry)
            state.history.append({
                "iteration": state.iteration_count,
                "action": next_action.operation_type,
                "score_before": score_before,
                "score_after": score_after,
                "delta": delta,
                "classification": prog_class.value
            })
