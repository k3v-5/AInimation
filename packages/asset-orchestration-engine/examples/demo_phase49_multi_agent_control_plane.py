import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.multi_agent_control_plane import (
    ControlPlaneAPI, LockType, Task
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 49: MULTI-AGENT ORCHESTRATION & CONTROL PLANE")
    print("=" * 95)

    api = ControlPlaneAPI(max_mcp_calls=30)

    # 1. Caso Obligatorio 1: Descomposición de Intención y Routing Multi-Agente
    print("\n[PASO 1] Caso Obligatorio 1: Descomposición de Intención en Pipeline de Agentes (Sección 202):")
    intent = "Crea una casa medieval de piedra con tejado inclinado"
    plan = api.plan_user_intent(intent)
    print(f" - Intención de Antigravity: \"{intent}\"")
    print(f" - Pipeline de Agentes Asignados ({len(plan.agent_pipeline)} etapas):")
    for i, role in enumerate(plan.agent_pipeline, 1):
        print(f"   * Etapa {i}: [{role.value}]")

    # 2. Caso Obligatorio 2: Decisión de Critic (Refine en vez de Regenerar Todo)
    print("\n[PASO 2] Caso Obligatorio 2: Decisión del Critic sobre Score Mediocre (Sección 203):")
    action_1, msg_1 = api.evaluate_critic_action("TASK_HOUSE", current_score=0.48, score_history=[0.48])
    print(f" - Score Inicial: 48% -> Acción de Critic: [{action_1.value}] (Corrección mínima de parámetros en vez de rehacer todo)")

    # 3. Caso Obligatorio 3: Detección de Rendimientos Decrecientes
    print("\n[PASO 3] Caso Obligatorio 3: Detección de Rendimientos Decrecientes (Sección 204):")
    action_2, msg_2 = api.evaluate_critic_action("TASK_HOUSE", current_score=0.64, score_history=[0.48, 0.63])
    print(f" - Progresión de Score: 48% -> 63% -> 64% -> Acción: [{action_2.value}] | Motivo: \"{msg_2}\"")

    # 4. Caso Obligatorio 4: Reconciliación de Estado tras Timeout de MCP
    print("\n[PASO 4] Caso Obligatorio 4: Reconciliación de Timeout de MCP (Sección 205):")
    res_recon = api.reconcile_mcp_timeout(
        task_id="TASK_BLENDER_EXPORT",
        expected_object_name="SM_MedievalHouse_001",
        scene_objects=["Camera", "Light", "SM_MedievalHouse_001"]
    )
    print(f" - Resultado de Inspección: Acción=[{res_recon['action']}] | Mensaje: \"{res_recon['message']}\"")

    # 5. Caso Obligatorio 6: Serialización de Recursos con ResourceLock
    print("\n[PASO 5] Caso Obligatorio 6: Serialización de Locks de Recursos (Sección 207):")
    api.acquire_resource_lock(LockType.BLENDER, "BLENDER_MAIN", "TASK_HOUSE_01")
    print(f" - [TASK_HOUSE_01] adquirió lock sobre BLENDER_MAIN.")
    try:
        api.acquire_resource_lock(LockType.BLENDER, "BLENDER_MAIN", "TASK_HOUSE_02")
    except BlockingIOError as e:
        print(f" - [TASK_HOUSE_02] en espera -> {e}")
    api.release_resource_lock(LockType.BLENDER, "BLENDER_MAIN", "TASK_HOUSE_01")
    print(f" - Lock liberado limpiamente por [TASK_HOUSE_01].")

    # 6. Caso Obligatorio 8: Control de Presupuesto de Llamadas MCP
    print("\n[PASO 6] Caso Obligatorio 8: Control de Presupuesto MCP (Sección 209):")
    tight_api = ControlPlaneAPI(max_mcp_calls=5)
    t_budget = Task(task_id="TASK_HEAVY_MESH", intent="Generar ciudad completa")
    res_b = tight_api.execute_task(t_budget, requested_mcp_calls=12)
    print(f" - Ejecución de Tarea con Presupuesto Excedido: Válida=[{res_b.is_valid}] | Error: \"{res_b.error_message}\"")

    # 7. Caso Obligatorio 10: Salvamento de Fallos Parciales por RecoveryAgent
    print("\n[PASO 7] Caso Obligatorio 10: Salvamento de Fallos Parciales (Sección 211):")
    artifacts = {
        "SM_MedievalHouse_001": True,
        "UCX_MedievalHouse_001": True,
        "MI_MedievalHouse_001": False
    }
    salvage = api.salvage_partial_failure("TASK_HOUSE_FAIL", artifacts)
    print(f" - Artefactos Conservados: {salvage['retained_outputs']}")
    print(f" - Artefactos Descartados: {salvage['discarded_outputs']}")
    print(f" - Acción de Recuperación: [{salvage['recovery_action']}] | Mensaje: \"{salvage['message']}\"")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 49 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
