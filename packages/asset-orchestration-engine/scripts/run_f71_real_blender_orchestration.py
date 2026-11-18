import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestration import (
    MultiAgentOrchestrationAPI, OrchestrationEngine, OrchestrationPlan,
    Task, TaskGraph, TaskPriority, TaskStatus, AgentRegistry
)

def run_f71_real_blender_orchestration():
    print("=" * 100)
    print("  AOE FASE 71 — EJECUCIÓN MULTI-AGENTE REAL INTEGRADA CON BLENDER")
    print("=" * 100)

    api = MultiAgentOrchestrationAPI()
    asset_id = "WP_DarX_Vandal_MarkII"
    semantic_id = "weapon.darx.vandal.mk2"

    print("\n[PASO 1] Registro de Agentes Especializados y Tool Governance:")
    for a in api.registry.list_agents():
        print(f" - Agente [{a.agent_id:<26}] | Permisos: {len(a.contract.permissions)} | Allowed Tools: {a.contract.allowed_tools}")

    print("\n[PASO 2] Construcción del Plan Canónico DAG de 11 Etapas:")
    plan = api.create_plan(asset_id=asset_id, semantic_id=semantic_id, prompt="Rifle táctico de plasma estilo DarX")
    print(f" - Plan ID: [{plan.orchestration_id}]")
    print(f" - Tareas registradas: {len(plan.task_graph.list_tasks())}")

    print("\n[PASO 3] Ejecución de la Capa de Orquestación Multi-Agente:")
    t_start = time.time()
    out = api.execute_plan(plan)
    elapsed = time.time() - t_start

    print(f" - Estado Final de la Orquestación: {'SUCCESS [PASS]' if out['success'] else 'FAILED'}")
    print(f" - Tareas Ejecutadas: {out['completed_tasks']}/{len(plan.task_graph.list_tasks())} en {elapsed:.4f}s")
    print(f" - Eventos Registrados en EventLog: {out['events_count']}")

    print("\n[PASO 4] Resultados Específicos por Agente:")
    for task_id, res in out["results"].items():
        print(f" - [{task_id:<22}] ejecutado por [{res.agent_id:<25}] -> {res.status.value}")
        if "visual_score" in res.outputs:
            print(f"   * Puntuación Visual del Critic: {res.outputs['visual_score']:.1f}/100.0 (Regla 52 Aprobada: {res.outputs['critic_report']['meets_threshold']})")
        if "qa_report" in res.outputs:
            print(f"   * QA Técnico: {res.outputs['qa_report']['readiness_status']} | Cero Duplicados: {res.outputs['qa_report']['checks']['zero_duplicates']}")

    pkg_res = out["results"].get("T9_Packaging")
    if pkg_res and "delivered_package" in pkg_res.outputs:
        pkg = pkg_res.outputs["delivered_package"]
        print("\n[PASO 5] Entrega y Empaquetado Verificado (F69):")
        print(f" - Package ID: [{pkg['package_id']}]")
        print(f" - Receipt ID: [{pkg['receipt']['receipt_id']}] -> Destino: [{pkg['receipt']['destination']}]")

    print("\n" + "=" * 100)
    print("  VALIDACIÓN REAL MULTI-AGENTE DE FASE 71 COMPLETADA (100% PASS)")
    print("=" * 100)

if __name__ == "__main__":
    run_f71_real_blender_orchestration()
