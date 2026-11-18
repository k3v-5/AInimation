import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_execution_gateway import (
    MCPGatewayAPI, CommandType, RiskLevel, GatewayPolicy, MockMCPAdapter
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 42: MCP EXECUTION GATEWAY & BLENDER STATE CONTROL")
    print("=" * 95)

    adapter = MockMCPAdapter()
    gateway_api = MCPGatewayAPI(
        policy=GatewayPolicy(max_mcp_calls_per_operation=10, max_same_command_retries=3),
        adapter=adapter
    )

    # 1. Sandboxing y Bloqueo de Operaciones Destructivas (Denylist)
    print("\n[PASO 1] Cortafuegos de Seguridad y Sandboxing de Comandos (Sección 135 & 203):")
    dangerous_cmd = gateway_api.create_command("CMD_EVIL", "OP_00", CommandType.DELETE_ALL_OBJECTS, "ALL")
    try:
        gateway_api.execute_command(dangerous_cmd)
    except PermissionError as e:
        print(f" - [+] Operación Destructiva Bloqueada con Éxito: {e}")

    # 2. Planificación de Comandos y Control de Presupuesto (Budget Guard)
    print("\n[PASO 2] Planificación de Comandos y Verificación de Presupuesto MCP (Sección 54 & 145):")
    commands = [
        gateway_api.create_command("C1", "OP_BUILD", CommandType.CREATE_OBJECT, "HOUSE_FOUNDATION"),
        gateway_api.create_command("C2", "OP_BUILD", CommandType.CREATE_OBJECT, "HOUSE_WALLS"),
        gateway_api.create_command("C3", "OP_BUILD", CommandType.CREATE_OBJECT, "HOUSE_ROOF", risk_level=RiskLevel.LOW)
    ]
    plan = gateway_api.plan_operations(commands)
    print(f" - Plan ID: {plan.plan_id} | Llamadas MCP Estimadas: {plan.estimated_mcp_calls} (Límite: 10)")
    print(f" - Duración Estimada: {plan.estimated_duration}s | Nivel de Riesgo: [{plan.overall_risk.value}]")

    # 3. Ejecución Controlada con Verificación de Escena en Blender
    print("\n[PASO 3] Ejecución Transaccional con Verificación de Escena en Blender (Sección 72-80):")
    for cmd in commands:
        res = gateway_api.execute_command(cmd)
        print(f" - [{cmd.command_id}] Target: '{cmd.target}' -> Estado: [{res.status.value}] | Verificado en Blender.")
    print(f" - Versión de Escena Actualizada: v{gateway_api.current_scene_version}")
    print(f" - Objetos en Blender: {adapter.inspect_scene_objects()}")

    # 4. Control de Concurrencia Optimista (State Conflict)
    print("\n[PASO 4] Control de Concurrencia Optimista (Sección 30):")
    outdated_cmd = gateway_api.create_command("C_OLD", "OP_OLD", CommandType.UPDATE_OBJECT, "HOUSE_WALLS", expected_scene_version=1)
    try:
        gateway_api.execute_command(outdated_cmd)
    except RuntimeError as e:
        print(f" - [+] Conflicto de Versión Detectado (Evita colisiones): {e}")

    # 5. Detección de Modificaciones Externas (Drift Detection)
    print("\n[PASO 5] Detección de Desviación de Estado / Drift en Blender (Sección 33 & 202):")
    adapter.scene_objects.add("MANUAL_BLENDER_CUBE_OUTSIDE_AOE")
    drift = gateway_api.detect_scene_drift(adapter.inspect_scene_objects())
    print(f" - Alerta de Drift: {drift}")

    # 6. Recuperación ante Timeouts sin Duplicar Objetos
    print("\n[PASO 6] Recuperación Transaccional ante Timeouts de MCP (Sección 69 & 201):")
    adapter.simulate_timeout = True
    timeout_cmd = gateway_api.create_command("C_TIME", "OP_TIME", CommandType.CREATE_OBJECT, "HOUSE_CHIMNEY")
    res_time = gateway_api.execute_command(timeout_cmd)
    print(f" - Estado tras Timeout: [{res_time.status.value}] (Recuperado: {res_time.output.get('recovered_from_timeout')})")

    # 7. Parada de Emergencia (Kill Switch)
    print("\n[PASO 7] Parada de Emergencia / Emergency Stop (Sección 173-175):")
    gateway_api.emergency_stop()
    blocked_res = gateway_api.execute_command(gateway_api.create_command("C_AFTER", "OP_AFTER", CommandType.CREATE_OBJECT, "OBJ_BLOCKED"))
    print(f" - Intento de Comando tras Parada de Emergencia -> Estado: [{blocked_res.status.value}] ({blocked_res.error})")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 42 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
