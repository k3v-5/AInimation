import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestration import (
    MultiAgentOrchestrationAPI, OrchestrationEngine, OrchestrationPlan,
    Task, TaskGraph, TaskPriority, TaskStatus, AgentRegistry,
    PerceptionAgent, DesignAnalysisAgent, StrategyAgent, GeometryAgent,
    MaterialAgent, BlenderExecutionAgent, VisualCriticAgent, QAAgent,
    CorrectionAgent, PackagingAgent
)

def run_demo():
    print("=" * 90)
    print("  AOE FASE 71 — MULTI-AGENT ORCHESTRATION LAYER DEMONSTRATION")
    print("=" * 90)

    api = MultiAgentOrchestrationAPI()
    
    print("\n[PASO 1] Registro y Validación de Agentes Especializados:")
    for a in api.registry.list_agents():
        print(f" - Agente: [{a.agent_id:<25}] | Tipo: [{a.agent_type:<18}] | Version: [{a.version}] | Capabilities: {len(a.contract.capabilities)}")

    print("\n[PASO 2] Construcción del Plan de Orquestación y Grafo DAG:")
    plan = api.create_plan(asset_id="WP_DarX_Vandal_MarkII", semantic_id="weapon.darx.vandal.mk2", prompt="Rifle táctico de plasma estilo DarX")
    print(f" - Plan ID: [{plan.orchestration_id}]")
    print(f" - Objetivo: {plan.objective}")
    print(f" - Total Tareas en Grafo: {len(plan.task_graph.list_tasks())}")
    
    layers = plan.task_graph.get_execution_layers()
    print(" - Capas de Ejecución Paralela / Secuencial:")
    for idx, layer in enumerate(layers):
        task_names = [t.task_id for t in layer]
        print(f"   * Capa {idx + 1}: {task_names}")

    print("\n[PASO 3] Ejecución Coordinada Multi-Agente (Perception -> QA -> Delivery):")
    t_start = time.time()
    out = api.execute_plan(plan)
    elapsed = time.time() - t_start
    
    print(f" - Orquestación Finalizada: {'SUCCESS [PASS]' if out['success'] else 'FAILED'}")
    print(f" - Tareas Completadas: {out['completed_tasks']}/{len(plan.task_graph.list_tasks())} en {elapsed:.4f}s")
    print(f" - Eventos Registrados en EventLog: {out['events_count']}")

    print("\n[PASO 4] Resultados por Agente y Trazabilidad del Digital Twin:")
    for task_id, res in out["results"].items():
        mut_count = len(res.mutations)
        print(f" - Tarea [{task_id:<20}] por [{res.agent_id:<25}] -> Status: [{res.status.value}] | Mutaciones DT: {mut_count}")

    pkg_res = out["results"].get("T9_Packaging")
    if pkg_res and "delivered_package" in pkg_res.outputs:
        pkg = pkg_res.outputs["delivered_package"]
        print("\n[PASO 5] Paquete Entregado por PackagingAgent:")
        print(f" - Package ID: [{pkg['package_id']}]")
        print(f" - Status de Entrega: [{pkg['delivery_status']}]")
        print(f" - Destino: [{pkg['receipt']['destination']}]")

    print("\n" + "=" * 90)
    print("  DEMOSTRACIÓN DE FASE 71 COMPLETADA CON ÉXITO")
    print("=" * 90)

if __name__ == "__main__":
    run_demo()
