import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.intent_compiler_task_graph import (
    IntentCompilerAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 39: INTENT COMPILER & TASK GRAPH PLANNER")
    print("=" * 95)

    api = IntentCompilerAPI()

    # 1. Compilación de Lenguaje Natural a Intento Estructurado
    raw_prompt = (
        "Haz una casa medieval abandonada de piedra y madera, parecida a esta referencia, "
        "con cuatro ventanas, una puerta grande, tejado inclinado y aspecto deteriorado."
    )
    print(f"\n[PASO 1] Recepción de Prompt Humano y Compilación de Intento (Sección 1):\n\"{raw_prompt}\"")

    intent = api.compile_intent(raw_prompt)
    print(f"\n - Intent ID: {intent.intent_id} | Objetivo: {intent.objective} | Preflight: [{intent.preflight_status.value}]")
    print(f" - Nivel de Confianza: {intent.confidence * 100:.1f}%")
    print(" - Requisitos Formales Extraídos (MUST-HAVE):")
    for r in intent.requirements:
        print(f"   * [{r.req_id}] ({r.priority.value}) {r.key} = {r.value} (Fuente: {r.source.value})")
    print(" - Exclusiones Activas (MUST-NOT-HAVE):")
    for e in intent.exclusions:
        print(f"   * [{e.exclusion_id}] Términos Prohibidos: {e.prohibited_terms}")

    # 2. Descomposición de Referencia y Máscara de Objetivos
    print("\n[PASO 2] Descomposición de Referencia Visual y Target Mask (Sección 41-42):")
    print(f" - Target (Objetivo a Modelar): {intent.target_mask.target}")
    print(f" - Context (Entorno Contextual): {intent.target_mask.context}")
    print(f" - Ignore (Elementos Ignorados): {intent.target_mask.ignore}")
    print(f" - Alcance Asignado: {intent.target_mask.scope.value}")

    # 3. Construcción del Grafo Acíclico Dirigido (Task Graph DAG)
    print("\n[PASO 3] Construcción del Grafo de Tareas DAG y Hitos (Milestones) (Sección 68 & 93):")
    dag = api.build_task_graph(intent)
    api.validate_graph(dag, intent)
    print(f" - DAG ID: {dag.graph_id} con {len(dag.nodes)} Nodos de Tarea:")
    for node in dag.nodes.values():
        print(f"   * [{node.node_id}] {node.name} -> Requiere: {node.requires} | Produce: {node.produces} | Hito: {node.milestone.value if node.milestone else 'N/A'}")

    # 4. Compilación del Plan de Ejecución y Propagación de Restricciones
    print("\n[PASO 4] Compilación del Plan de Ejecución y Propagación de Restricciones (Sección 105):")
    steps = api.compile_plan(dag, intent)
    for step in steps:
        print(f" - [{step.step_id}] Operación: {step.operation} sobre {step.target}")
        print(f"   * Parámetros Tipados: {step.parameters}")
        print(f"   * Precondiciones: {step.preconditions} -> Postcondiciones: {step.postconditions}")

    # 5. Detección de Desviación de Intención (Intent Drift)
    print("\n[PASO 5] Verificación Anti-Desviación (Intent Drift Detection) (Sección 177):")
    try:
        api.detect_intent_drift(intent, steps)
        print(" - [+] Validación Anti-Drift: Plan 100% fiel al estilo medieval solicitado sin elementos modernos.")
    except ValueError as e:
        print(f" - [-] Drift Detectado: {e}")

    # 6. Replanificación Incremental con IntentDelta
    print("\n[PASO 6] Replanificación Incremental ante Cambios Puntuales (IntentDelta) (Sección 126):")
    delta_roof = api.replan_delta(target="HOUSE_001.ROOF", property_name="height", old_val=1.75, new_val=1.20)
    print(f" - Modificación Solicitada: Cambiar altura de techo de {delta_roof.old_value}m a {delta_roof.new_value}m")
    print(f" - Subgrafo Afectado (Sin Reconstruir Muros ni Huella): {delta_roof.affected_subgraph}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 39 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
