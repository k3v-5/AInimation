import time
from typing import Dict, Any, List, Optional
from ..core.adaptive_types import (
    SessionState, CorrectionOp, ScopeLevel, TerminationReason,
    AdaptiveRiskLevel, ErrorCategory
)
from ..core.adaptive_schema import (
    GenerationAttempt, ErrorDiagnosis, CorrectionCandidate,
    CorrectionTransactionRecord, SessionReport
)
from ..diagnosis.error_attributor import ErrorAttributor
from ..regeneration.partial_regenerator import PartialRegenerator
from ..transactions.correction_transaction import CorrectionTransaction

from src.parametric_asset_engine import ParametricAssetAPI
from src.visual_reference_matching import VisualReferenceMatcherAPI, ReferenceImageSpec

class AdaptiveGenerationEngine:
    def __init__(self, max_iterations: int = 5, target_score: float = 0.90):
        self.max_iterations = max_iterations
        self.target_score = target_score
        
        self.param_api = ParametricAssetAPI()
        self.critic_api = VisualReferenceMatcherAPI()
        self.transaction_mgr = CorrectionTransaction()
        
        self.attempts: List[GenerationAttempt] = []
        self.best_attempt: Optional[GenerationAttempt] = None
        self.session_state = SessionState.CREATED
        self.termination_reason: Optional[TerminationReason] = None
        self.score_history: List[float] = []

    def start_adaptive_session(
        self,
        asset_id: str,
        initial_parameters: Dict[str, Any],
        target_reference: ReferenceImageSpec,
        simulate_collision_failure: bool = False
    ) -> SessionReport:
        self.session_state = SessionState.GENERATING
        start_time = time.time()
        
        current_params = dict(initial_parameters)
        
        # 1. Intento Inicial
        current_asset = self.param_api.create_asset(asset_id, current_params)
        
        # Evaluación Inicial
        initial_ratio = current_params.get("roof_height", 1.80) / (current_params.get("wall_height", 3.0) + current_params.get("roof_height", 1.80))
        eval_report = self.critic_api.evaluate_asset(
            asset_id=asset_id,
            ref=target_reference,
            generated_parameters=current_params,
            generated_aspect_ratio=1.52,
            generated_roof_ratio=initial_ratio
        )
        
        attempt_0 = GenerationAttempt(
            attempt_id="ATTEMPT_00",
            parameters=dict(current_params),
            total_score=eval_report.overall_score,
            is_hard_constraint_pass=not simulate_collision_failure
        )
        self.attempts.append(attempt_0)
        self.best_attempt = attempt_0
        self.score_history.append(attempt_0.total_score)

        # Si falla restricción dura (Hard constraint) -> Early exit
        if simulate_collision_failure:
            self.session_state = SessionState.FAILED
            self.termination_reason = TerminationReason.SYSTEM_FAILURE
            return self._build_report(asset_id, start_time)

        # Bucle de Corrección Adaptativa
        for i in range(1, self.max_iterations + 1):
            if self.best_attempt.total_score >= self.target_score:
                self.session_state = SessionState.ACCEPTED
                self.termination_reason = TerminationReason.ACCEPTED
                break

            self.session_state = SessionState.DIAGNOSING
            
            # Diagnóstico de diferencias
            current_roof_ratio = current_params.get("roof_height", 1.80) / (current_params.get("wall_height", 3.0) + current_params.get("roof_height", 1.80))
            candidates = ErrorAttributor.diagnose_and_attribute(
                measured_ratios={"roof_ratio": current_roof_ratio, "window_spacing": current_params.get("window_spacing", 1.20)},
                target_ratios={"roof_ratio": target_reference.expected_roof_ratio, "window_spacing": 1.0},
                current_parameters=current_params
            )

            if not candidates:
                self.session_state = SessionState.BLOCKED
                self.termination_reason = TerminationReason.NO_IMPROVEMENT
                break

            corr = candidates[0]
            
            # Comprobar componentes dirty
            dirty_comps = PartialRegenerator.determine_dirty_components(corr.parameter, corr.scope)
            
            # Iniciar Transacción Atómica
            tx_id = f"TX_{i:02d}"
            self.transaction_mgr.begin_transaction(tx_id, f"ATTEMPT_{i:02d}", current_params, dirty_comps)
            
            # Aplicar cambio mínimo
            current_params[corr.parameter] = corr.new_value
            self.param_api.update_asset(asset_id, {corr.parameter: corr.new_value})
            
            # Evaluar nuevo intento
            new_roof_ratio = current_params.get("roof_height", 1.80) / (current_params.get("wall_height", 3.0) + current_params.get("roof_height", 1.80))
            new_eval = self.critic_api.evaluate_asset(
                asset_id=asset_id,
                ref=target_reference,
                generated_parameters=current_params,
                generated_aspect_ratio=1.52,
                generated_roof_ratio=new_roof_ratio
            )
            
            attempt_curr = GenerationAttempt(
                attempt_id=f"ATTEMPT_{i:02d}",
                parent_attempt_id=self.attempts[-1].attempt_id,
                parameters=dict(current_params),
                total_score=new_eval.overall_score
            )
            self.attempts.append(attempt_curr)
            self.score_history.append(attempt_curr.total_score)

            # Comprobar si mejoró o empeoró
            if attempt_curr.total_score > self.best_attempt.total_score:
                self.transaction_mgr.commit(tx_id)
                self.best_attempt = attempt_curr
            else:
                # Rollback si empeoró
                current_params = self.transaction_mgr.rollback(tx_id)
                self.param_api.update_asset(asset_id, current_params)

            # Detección de Estancamiento (Plateau)
            if len(self.score_history) >= 3:
                d1 = self.score_history[-1] - self.score_history[-2]
                if abs(d1) < 0.005:
                    self.session_state = SessionState.ACCEPTED if self.best_attempt.total_score >= 0.85 else SessionState.BLOCKED
                    self.termination_reason = TerminationReason.NO_IMPROVEMENT
                    break

        if not self.termination_reason:
            if self.best_attempt.total_score >= self.target_score:
                self.session_state = SessionState.ACCEPTED
                self.termination_reason = TerminationReason.ACCEPTED
            else:
                self.session_state = SessionState.BLOCKED
                self.termination_reason = TerminationReason.BUDGET_EXCEEDED

        return self._build_report(asset_id, start_time)

    def _build_report(self, asset_id: str, start_time: float) -> SessionReport:
        duration = round(time.time() - start_time, 3)
        rework_efficiency = round((len(self.attempts) / max(1, len(self.score_history))), 2)
        return SessionReport(
            session_id=f"SESS_{int(time.time()*1000)}",
            asset_id=asset_id,
            status=self.session_state,
            termination_reason=self.termination_reason or TerminationReason.ACCEPTED,
            total_attempts=len(self.attempts),
            score_history=list(self.score_history),
            best_attempt=self.best_attempt,
            duration=duration,
            rework_efficiency=rework_efficiency
        )
