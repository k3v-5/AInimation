import time
from typing import Dict, Any, List, Optional
from ..core.critic_types import (
    CriticStatus, ModificationLevel, CorrectionOperationType,
    RootCauseSeverity, CriticRiskLevel, BudgetStatus, StrategyResult
)
from ..core.critic_schema import (
    RootCause, PreservationContract, CorrectionOp, CorrectionPlan,
    CriticDecision, CriticPolicy, CheckpointSnapshot, CandidateBranch
)
from ..diagnosis.diagnosis_engine import DiagnosisEngine, PriorityEngine
from ..planner.correction_planner import CorrectionPlanner
from ..controller.iteration_controller import IterationController
from ..controller.rollback_controller import RollbackController, CriticMemory

class AICriticAPI:
    """
    AI Critic & Self-Correction API (AOE v37)
    
    Regla Fundamental:
    EL CRITIC NO TIENE PERMISO DE EJECUCIÓN DIRECTA EN BLENDER NI DE PROBAR A CIEGAS.
    IDENTIFICA CAUSAS RAÍZ (Root Cause), PRIORIZA POR IMPACTO Y EMITE PLANES DE CORRECCIÓN
    ATÓMICOS CON CONTRATOS DE PRESERVACIÓN, GESTIONANDO PRESUPUESTOS Y ROLLBACKS.
    """
    def __init__(self, policy: Optional[CriticPolicy] = None):
        self.policy = policy or CriticPolicy()
        self.iteration_ctrl = IterationController(self.policy)
        self.rollback_ctrl = RollbackController()
        self.memory = CriticMemory()

    def diagnose_and_plan(
        self,
        asset_id: str,
        differences: List[Any],
        current_score: float,
        confidence: float = 0.95,
        locked_constraints: Optional[List[str]] = None
    ) -> CriticDecision:
        decision_id = f"DEC_{int(time.time()*1000)}"

        # 1. Comprobar si el score ya cumple criterio de aceptación (PASS)
        if current_score >= 0.90 and not any(getattr(d, 'severity', None) == 'CRITICAL' for d in differences):
            return CriticDecision(
                decision_id=decision_id,
                asset_id=asset_id,
                status=CriticStatus.PASS,
                score=current_score,
                confidence=confidence,
                next_action="DONE"
            )

        # 2. Comprobar baja confianza -> HUMAN_REVIEW
        if confidence < self.policy.human_review_threshold:
            return CriticDecision(
                decision_id=decision_id,
                asset_id=asset_id,
                status=CriticStatus.HUMAN_REVIEW,
                score=current_score,
                confidence=confidence,
                next_action="REQUEST_HUMAN_FEEDBACK",
                stop_reason="LOW_CONFIDENCE_DIAGNOSIS"
            )

        # 3. Diagnóstico de Causa Raíz
        causes = DiagnosisEngine.diagnose_issues(differences, confidence)
        if not causes:
            return CriticDecision(
                decision_id=decision_id,
                asset_id=asset_id,
                status=CriticStatus.DEADLOCK,
                score=current_score,
                confidence=confidence,
                next_action="REQUEST_HUMAN_FEEDBACK",
                stop_reason="NO_EXECUTABLE_CORRECTION"
            )

        # 4. Priorización de Causas Raíz
        ranked_causes = PriorityEngine.rank_causes(causes)

        # 5. Planificación de Corrección Mínima
        try:
            plan = CorrectionPlanner.plan_correction(asset_id, ranked_causes, locked_constraints)
            # Determinar estado
            if any(op.operation_type == CorrectionOperationType.REBUILD_COMPONENT for op in plan.operations):
                status = CriticStatus.REBUILD_COMPONENT
            else:
                status = CriticStatus.CORRECT

            return CriticDecision(
                decision_id=decision_id,
                asset_id=asset_id,
                status=status,
                score=current_score,
                diagnosis=ranked_causes,
                plan=plan,
                confidence=confidence,
                next_action="EXECUTE_PLAN"
            )
        except ValueError as e:
            # Violación de restricción bloqueada
            return CriticDecision(
                decision_id=decision_id,
                asset_id=asset_id,
                status=CriticStatus.BLOCKED,
                score=current_score,
                diagnosis=ranked_causes,
                confidence=confidence,
                next_action="REJECT_AND_STOP",
                stop_reason=str(e)
            )

    def handle_tool_failure(self, error_type: str) -> str:
        """Diferencia entre TOOL_ERROR (retryable) y MODEL_ERROR."""
        if "TIMEOUT" in error_type.upper() or "CONNECTION" in error_type.upper():
            return "RETRY_WITH_BACKOFF"
        return "DIAGNOSE_AND_ADAPT"
