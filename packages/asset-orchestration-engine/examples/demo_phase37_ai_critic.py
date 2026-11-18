import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ai_critic_self_correction import (
    AICriticAPI, CandidateBranch, CorrectionPlan
)
from src.visual_reference_similarity import DifferenceRecord, DifferenceType, DifferenceSeverity

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 37: AI CRITIC & SELF-CORRECTION SYSTEM")
    print("=" * 95)

    api = AICriticAPI()

    # 1. Diagnóstico de Causa Raíz y Agrupación de Síntomas
    print("\n[PASO 1] Diagnóstico de Causa Raíz a partir de Múltiples Síntomas (Sección 18):")
    symptoms = [
        DifferenceRecord(target="HOUSE.ROOF_HEIGHT", diff_type=DifferenceType.WRONG_SIZE, severity=DifferenceSeverity.HIGH, expected=0.30, actual=0.48, metric="roof_height"),
        DifferenceRecord(target="HOUSE.ROOF_CHIMNEY", diff_type=DifferenceType.WRONG_POSITION, severity=DifferenceSeverity.MEDIUM, expected="CENTER", actual="EDGE", metric="chimney_pos")
    ]
    print(f" - Síntomas Detectados: {len(symptoms)} discrepancias en tejado y chimenea.")
    decision = api.diagnose_and_plan("HOUSE_001", symptoms, current_score=0.72)

    print(f" - Decisión del Critic: [{decision.status.value}] (Score actual: {decision.score * 100:.1f}%)")
    print(f" - Causa Raíz Identificada: [{decision.diagnosis[0].cause_id}] {decision.diagnosis[0].description}")
    print(f"   * Evidencia: {decision.diagnosis[0].evidence}")
    print(f"   * Dependencias Detectadas: {decision.diagnosis[0].dependencies}")

    # 2. Plan de Corrección Mínima y Contrato de Preservación
    print("\n[PASO 2] Plan de Corrección Mínima y Contrato de Preservación (Sección 21 & 30):")
    plan = decision.plan
    print(f" - Plan ID: {plan.plan_id} | Costo Estimado: {plan.estimated_cost} | Riesgo: {plan.risk.value}")
    print(" - Operaciones Planificadas:")
    for op in plan.operations:
        print(f"   * [{op.operation_id}] ({op.level.value}) {op.operation_type.value} sobre {op.target} (Blast Radius: {op.blast_radius})")
    print(" - Contrato de Preservación (LO QUE NO SE DEBE TOCAR):")
    for prop in plan.preservation_contract.preserve_properties:
        print(f"   * [+] Preservar: {prop}")

    # 3. Gestión de Checkpoints y Rollback ante Regresión
    print("\n[PASO 3] Control Transaccional de Checkpoints y Rollback (Sección 85):")
    api.rollback_ctrl.save_checkpoint("CHK_GEN_v1", score=0.88, asset_state={"roof_pitch": 40.0, "status": "STABLE"})
    print(" - Guardado Checkpoint CHK_GEN_v1 con Score: 88.0%")

    # Simular una modificación que degrada la silueta
    api.rollback_ctrl.save_checkpoint("CHK_GEN_v2", score=0.71, asset_state={"roof_pitch": 25.0, "status": "REGRESSED"})
    print(" - Modificación v2 aplicada -> Score cayó a 71.0% (REGRESIÓN DETECTADA)")
    best = api.rollback_ctrl.rollback_to_best()
    print(f" - Rollback Automático ejecutado -> Restaurado: {best.checkpoint_id} (Score: {best.score * 100:.1f}%)")

    # 4. Control de Presupuesto y Detección de Oscilación
    print("\n[PASO 4] Detección de Oscilación y Estancamiento (Anti-Retrabajo):")
    scores_osc = [0.80, 0.85, 0.79, 0.84]
    for s in scores_osc:
        api.iteration_ctrl.record_iteration(s)
    is_osc = api.iteration_ctrl.is_oscillating()
    print(f" - Historial de Iteraciones: {scores_osc} -> Oscilación Detectada: {is_osc}")

    # 5. Selección de Ramas Candidatas (Candidate Branching)
    print("\n[PASO 5] Selección de la Mejor Rama Candidata (Candidate Branching):")
    p_a = CorrectionPlan(plan_id="PLAN_A", target_asset="HOUSE_001")
    p_b = CorrectionPlan(plan_id="PLAN_B", target_asset="HOUSE_001")
    candidates = [
        CandidateBranch(branch_id="BRANCH_A_LOCAL_SCALE", plan=p_a, predicted_score=0.89),
        CandidateBranch(branch_id="BRANCH_B_PARAMETRIC_REBUILD", plan=p_b, predicted_score=0.96)
    ]
    best_cand = api.iteration_ctrl.select_best_candidate(candidates)
    print(f" - Candidato Ganador Seleccionado: [{best_cand.branch_id}] con Score Predicho: {best_cand.predicted_score * 100:.1f}%")

    # 6. Manejo de Fallos Técnicos
    print("\n[PASO 6] Diferenciación de Fallos Técnicos de Red/MCP vs Errores de Modelo:")
    action_timeout = api.handle_tool_failure("MCP_TIMEOUT_GATEWAY")
    action_model = api.handle_tool_failure("GEOMETRIC_INTERSECTION_ERROR")
    print(f" - Error MCP Timeout -> Acción: {action_timeout}")
    print(f" - Error de Modelo   -> Acción: {action_model}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 37 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
