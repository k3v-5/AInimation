import time
from typing import Dict, Any, List, Optional
from ..core.loop_types import LoopState, DecisionOutcome, StopReason
from ..core.loop_schema import (
    IterativeGenerationRequest, IterationContext, IterationRecord,
    IterationLoopConfiguration, IterativeGenerationResult, LoopValidationResult
)
from ..engine.iteration_decision_engine import IterationDecisionEngine
from ..engine.best_state_tracker import BestStateTracker
from ..engine.checkpoint_manager import CheckpointManager
from ..engine.loop_hasher import LoopHasher

from src.automated_visual_evaluation import AutomatedVisualEvaluationAPI
from src.geometric_validation_qa import GeometricValidationAPI
from src.intelligent_critic_engine import IntelligentCriticAPI
from src.autonomous_correction_engine import AutonomousCorrectionAPI

class IterativeGenerationLoopEngine:
    """
    Iterative Generation Loop Engine (AOE v65)
    
    Regla Fundamental:
    COORDINA EL CICLO CERRADO DE GENERACIÓN, EVALUACIÓN VISUAL (F61), QA GEOMÉTRICO (F62),
    CRÍTICA INTELIGENTE (F63) Y CORRECCIÓN AUTÓNOMA (F64), CONSERVANDO EL MEJOR ESTADO CONOCIDO,
    DETECCIÓN DE CONVERGENCIA, ESTANCAMIENTO, OSCILACIONES Y GARANTÍA ESTRUCTURAL DE TERMINACIÓN.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version
        self.visual_api = AutomatedVisualEvaluationAPI()
        self.geometry_qa_api = GeometricValidationAPI()
        self.critic_api = IntelligentCriticAPI()
        self.correction_api = AutonomousCorrectionAPI()

    def run_loop(
        self,
        request: IterativeGenerationRequest,
        initial_geometry: Any,
        initial_surface: Any,
        initial_presentation: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> IterativeGenerationResult:
        ctx = context or {}
        config = request.configuration
        asset_id = request.asset_id
        sem_id = request.semantic_id
        loop_id = f"LOOP_{asset_id}_{request.job_id}"

        best_tracker = BestStateTracker()
        history: List[IterationRecord] = []
        exec_trace: List[Dict[str, Any]] = []

        curr_geom = initial_geometry
        curr_surf = initial_surface
        curr_pres = initial_presentation
        initial_score: float = 0.0

        # Iteración Loop
        for iter_num in range(config.max_iterations + 1):
            iter_ctx = IterationContext(
                loop_id=loop_id,
                iteration_id=f"ITER_{iter_num}",
                iteration_number=iter_num,
                asset_id=asset_id,
                semantic_id=sem_id,
                status=LoopState.EVALUATING,
                started_at=time.time()
            )

            # 1. Evaluación Visual F61
            v_eval = self.visual_api.evaluate_visuals(
                request.reference_report, curr_geom, {"surface": curr_surf, "presentation": curr_pres}
            )

            # 2. QA Geométrico F62
            g_qa = self.geometry_qa_api.validate_geometry(
                curr_geom, {"visual_evaluation": v_eval, "surface": curr_surf}
            )

            # Scores combinados
            v_score = getattr(v_eval, "global_score", 1.0)
            g_score = getattr(g_qa, "quality_scores", {}).get("overall_geometry_score", 1.0)
            overall_score = round((v_score * 0.5 + g_score * 0.5), 4)

            if iter_num == 0:
                initial_score = overall_score

            # Trazabilidad de estado
            state_hash = f"STATE_HASH_{iter_num}_{v_eval.evaluation_hash[:8]}_{g_qa.validation_hash[:8]}"
            has_critical = any(d.severity == "CRITICAL" for d in g_qa.defects)

            # Actualizar mejor estado
            is_best = best_tracker.update_best(iter_num, overall_score, state_hash, {"geom": curr_geom, "surf": curr_surf})
            if is_best:
                CheckpointManager.save_checkpoint(loop_id, iter_num, iter_ctx, {"score": overall_score})

            # 3. Decisión de Parada / Convergencia
            decision, stop_reason = IterationDecisionEngine.evaluate_decision(
                iter_num, overall_score, v_score, g_score, has_critical, history, config
            )

            record = IterationRecord(
                iteration_number=iter_num,
                state_hash=state_hash,
                visual_score=v_score,
                geometry_score=g_score,
                overall_score=overall_score,
                accepted=is_best,
                corrections_applied=[],
                decision=decision
            )
            history.append(record)

            exec_trace.append({
                "iteration": iter_num,
                "overall_score": overall_score,
                "visual_score": v_score,
                "geometry_score": g_score,
                "decision": decision.value,
                "status": "SUCCESS"
            })

            # Si convergió o debemos parar, finalizar
            if decision != DecisionOutcome.CONTINUE:
                if decision == DecisionOutcome.CONVERGED:
                    final_loop_status = LoopState.CONVERGED
                elif decision == DecisionOutcome.BUDGET_EXHAUSTED:
                    final_loop_status = LoopState.BUDGET_EXHAUSTED
                elif decision == DecisionOutcome.STAGNATED:
                    final_loop_status = LoopState.STAGNATED
                else:
                    final_loop_status = LoopState.COMPLETED
                loop_hash = LoopHasher.compute_loop_hash(
                    loop_id, asset_id, iter_num + 1, best_tracker.best_iteration_number, stop_reason.value
                )
                return IterativeGenerationResult(
                    loop_id=loop_id,
                    asset_id=asset_id,
                    semantic_id=sem_id,
                    status=final_loop_status,
                    iterations_executed=iter_num + 1,
                    accepted_iteration=best_tracker.best_iteration_number,
                    final_state_hash=best_tracker.best_state_hash,
                    final_quality=best_tracker.best_quality_score,
                    initial_quality=initial_score,
                    quality_delta=round(best_tracker.best_quality_score - initial_score, 4),
                    best_iteration=best_tracker.best_iteration_number,
                    stop_reason=stop_reason,
                    iteration_history=history,
                    loop_hash=loop_hash,
                    execution_trace=exec_trace,
                    generation_metadata={"engine_version": self.engine_version}
                )

            # 4. Crítica F63
            critic_res = self.critic_api.generate_critic_diagnosis(request.vas, g_qa, v_eval)

            # 5. Corrección F64
            corr_res = self.correction_api.apply_corrections(critic_res, curr_geom)
            record.corrections_applied = corr_res.actions_applied

        # Finalización por límite de iteraciones
        loop_hash = LoopHasher.compute_loop_hash(
            loop_id, asset_id, len(history), best_tracker.best_iteration_number, StopReason.MAX_ITERATIONS_REACHED.value
        )
        return IterativeGenerationResult(
            loop_id=loop_id,
            asset_id=asset_id,
            semantic_id=sem_id,
            status=LoopState.BUDGET_EXHAUSTED,
            iterations_executed=len(history),
            accepted_iteration=best_tracker.best_iteration_number,
            final_state_hash=best_tracker.best_state_hash,
            final_quality=best_tracker.best_quality_score,
            initial_quality=initial_score,
            quality_delta=round(best_tracker.best_quality_score - initial_score, 4),
            best_iteration=best_tracker.best_iteration_number,
            stop_reason=StopReason.MAX_ITERATIONS_REACHED,
            iteration_history=history,
            loop_hash=loop_hash,
            execution_trace=exec_trace,
            generation_metadata={"engine_version": self.engine_version}
        )

    def validate_result(self, result: IterativeGenerationResult) -> LoopValidationResult:
        errors = []
        warnings = []
        if not result.loop_id:
            errors.append("MISSING_LOOP_ID: Loop ID is mandatory.")
        if result.iterations_executed <= 0:
            errors.append("INVALID_ITERATION_COUNT: Iterations count must be >= 1.")
        return LoopValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def resume_loop(self, loop_id: str) -> Optional[Dict[str, Any]]:
        return CheckpointManager.load_checkpoint(loop_id)
