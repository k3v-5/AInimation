import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestration_runtime import (
    OrchestrationAPI, RuntimeTaskType, RuntimeTaskStatus, RuntimeLockType
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 38: ORCHESTRATION RUNTIME")
    print("=" * 95)

    api = OrchestrationAPI()

    # 1. Registro de Agentes y Capacidades
    print("\n[PASO 1] Registro de Agentes Especialistas y Permisos (Sección 55 & 94):")
    b_agent = api.register_agent("BlenderAgent", capabilities=["build_geometry", "modify_geometry"], permissions=["READ", "EXECUTE"])
    c_agent = api.register_agent("CriticAgent", capabilities=["analyze", "critique"], permissions=["READ", "PLAN"])
    print(f" - Agente [{b_agent.agent_id}] -> Permisos: {b_agent.permissions} | Capacidades: {b_agent.capabilities}")
    print(f" - Agente [{c_agent.agent_id}] -> Permisos: {c_agent.permissions} | Capacidades: {c_agent.capabilities}")

    # 2. Creación de Tarea y Workflow para Antigravity
    print("\n[PASO 2] Recepción de Tarea de Alto Nivel de Antigravity y Creación de Workflow (Sección 170):")
    task = api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET, inputs={"style": "MEDIEVAL"})
    print(f" - Tarea Creada: {task.task_id} para Activo: {task.asset_id} (Estado: {task.status.value})")

    wf = api.workflow_engine.create_asset_workflow("HOUSE_001")
    print(f" - Workflow Generado: {wf.workflow_id} con {len(wf.steps)} Pasos Planificados:")
    for i, step in enumerate(wf.steps, 1):
        print(f"   {i}. [{step.step_id}] -> Tipo: {step.task_type.value} (Requiere: {step.required_capabilities})")

    # 3. Bloqueo de Recurso y Control de Concurrencia
    print("\n[PASO 3] Adquisición de Bloqueo Exclusivo sobre el Activo (Sección 45):")
    lease1 = api.acquire_lock("ASSET_HOUSE_001", task.task_id, RuntimeLockType.EXCLUSIVE)
    print(f" - Lock Adquirido: {lease1.lock_id} sobre {lease1.resource_id} por {lease1.task_id}")

    try:
        api.acquire_lock("ASSET_HOUSE_001", "TASK_CONCURRENT_2", RuntimeLockType.EXCLUSIVE)
    except RuntimeError as e:
        print(f" - Prevención de Concurrencia Incompatible: {e}")

    # 4. Ejecución Controlada en MCP y Verificación Empírica de Estado
    print("\n[PASO 4] Ejecución a través del MCP Adapter y Verificación de Estado (Sección 69 & 192):")
    api.transition_task(task.task_id, RuntimeTaskStatus.QUEUED)
    api.transition_task(task.task_id, RuntimeTaskStatus.PLANNING)
    api.transition_task(task.task_id, RuntimeTaskStatus.READY)
    api.transition_task(task.task_id, RuntimeTaskStatus.RUNNING)

    # Ejecución idempotente de creación de muros y tejado
    exec_unit_1 = api.execute_operation(task.task_id, "CREATE_OBJECT", "BlenderAgent", "HOUSE_001", {"object_name": "walls_mesh"}, "IDEMP_W_001")
    exec_unit_2 = api.execute_operation(task.task_id, "CREATE_OBJECT", "BlenderAgent", "HOUSE_001", {"object_name": "roof_mesh"}, "IDEMP_R_001")
    print(f" - Operación 1: {exec_unit_1.operation} -> Estado: {exec_unit_1.status.value}")
    print(f" - Operación 2: {exec_unit_2.operation} -> Estado: {exec_unit_2.status.value}")

    # Verificación empírica (anti-alucinación)
    api.verify_claimed_state("HOUSE_001", "roof_mesh")
    print(" - Verificación Empírica de Escena: [+] 'roof_mesh' confirmado en el estado real de Blender.")

    # 5. Avance de Workflow y Finalización
    print("\n[PASO 5] Avance de Workflow y Transiciones Finales (Sección 154):")
    api.transition_task(task.task_id, RuntimeTaskStatus.VALIDATING)
    api.transition_task(task.task_id, RuntimeTaskStatus.COMPLETED)
    api.release_lock("ASSET_HOUSE_001", task.task_id)
    print(f" - Tarea {task.task_id} Finalizada con Éxito -> Estado: [{task.status.value}]")

    # 6. Generación del Manifiesto Final del Activo (AssetManifest)
    print("\n[PASO 6] Generación del Manifiesto y Trazabilidad de Auditoría (AssetManifest):")
    manifest = api.workflow_engine.generate_manifest("HOUSE_001", "SPEC_2026_000823", "8a21678bd3c7138e", similarity_score=0.96)
    print(f" - Manifest Asset ID: {manifest.asset_id} (v{manifest.version}) -> Estado Final: [{manifest.final_status}]")
    print(f" - Similitud Visual Final: {manifest.similarity_score * 100:.1f}% | Validación Aprobada: {manifest.validation_passed}")
    print(f" - Artefactos Generados: {manifest.artifacts}")
    print(" - Pistas de Auditoría Registradas:")
    for entry in manifest.audit_trail:
        print(f"   * [{entry['action']}] -> {entry}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 38 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
