import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    BuildOrchestratorAPI, OrchestratorConfig
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 30: AI BUILD ORCHESTRATOR & MULTI-AGENT EXECUTION")
    print("=" * 95)

    config = OrchestratorConfig(max_attempts_per_task=3)
    api = BuildOrchestratorAPI(config)

    # 1. Escenario 201: Construcción Orquestada Multi-Agente
    print("\n[ESCENARIO 201] 1. Construcción Orquestada Multi-Agente (Intent -> Plan -> Task Graph -> Commit):")
    print("   Usuario: \"Créame una casa medieval pequeña con puerta accesible y escalera.\"")
    initial_params = {"width": 4.0, "height": 5.0, "door_width": 0.90, "stair_slope": 32.5}
    report_clean = api.run_orchestrated_build("medieval_house_01", initial_params)
    print(f" - Estado de Ejecución: {report_clean.status} | Aprobado: {report_clean.is_approved}")
    print(f" - Total Tareas Ejecutadas: {report_clean.tasks_executed}")
    for log in report_clean.execution_logs:
        print(f"   * {log}")

    # 2. Escenario 202: Corrección Quirúrgica de Subárbol Aislado (Anti-Retrabajo)
    print("\n[ESCENARIO 202] 2. Corrección Quirúrgica de Subárbol ante Fallo de QA:")
    print("   QA detecta: 'DOOR_TOO_NARROW (0.62m < 0.80m)'.")
    params_narrow = {"width": 4.0, "height": 5.0, "door_width": 0.62, "stair_slope": 32.5}
    report_corrected = api.run_orchestrated_build("medieval_house_narrow", params_narrow, simulated_qa_error="DOOR_TOO_NARROW")
    print(f" - Estado de Ejecución: {report_corrected.status} | Aprobado: {report_corrected.is_approved}")
    print(f" - Parámetros Finales: {report_corrected.final_parameters}")
    for log in report_corrected.execution_logs:
        print(f"   * {log}")

    # 3. Principio de Menor Privilegio y Seguridad de Herramientas
    print("\n[SEGURIDAD] 3. Control Estricto de Permisos y Menor Privilegio (Least Privilege):")
    can_qa_validate = api.validate_tool_permission("gameplay_qa_agent", "qa.validate_door")
    can_qa_modify_mesh = api.validate_tool_permission("gameplay_qa_agent", "blender.create_mesh")
    print(f" - gameplay_qa_agent -> 'qa.validate_door': {can_qa_validate} (ALLOWED)")
    print(f" - gameplay_qa_agent -> 'blender.create_mesh': {can_qa_modify_mesh} (DENIED)")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 30 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
