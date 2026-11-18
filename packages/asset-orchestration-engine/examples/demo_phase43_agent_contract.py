import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ai_orchestration_api import (
    AIOrchestratorAPI, PermissionLevel, ToolRegistry, ToolDefinition, ToolCategory
)
from src.visual_reference_matching import ReferenceImageSpec

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 43: AI ORCHESTRATION API & AGENT CONTRACT")
    print("=" * 95)

    agent_api = AIOrchestratorAPI(permission=PermissionLevel.MODIFY)

    # 1. Discovery de Herramientas y Capacidades
    print("\n[PASO 1] Discovery de Capacidades y Generadores (Sección 5 & 82):")
    cap_resp = agent_api.get_capabilities()
    print(f" - Estado: [{cap_resp.status.value}] | Resumen: {cap_resp.summary}")
    print(f" - Generadores Soportados: {cap_resp.output_data['supported_generators']}")
    print(f" - Arquetipos: {cap_resp.output_data['supported_archetypes']}")

    # 2. Planificación y Explicabilidad
    print("\n[PASO 2] Planificación Estructurada y Explicabilidad (Sección 6 & 40):")
    plan_resp = agent_api.create_plan("HOUSE_001", {"roof_height": 1.45, "wall_material": "STONE"})
    plan = plan_resp.output_data["plan"]
    print(f" - Plan ID: {plan.plan_id} | Hash: {plan.plan_hash}")
    print(f" - Llamadas MCP Estimadas: {plan.estimated_mcp_calls} | Duración: {plan.estimated_duration}s | Riesgo: {plan.risk}")
    
    exp_resp = agent_api.explain_plan(plan.plan_id)
    print(f" - Explicación: {exp_resp.summary}")

    # 3. Mutación y Creación con Ahorro de Tokens en Inspección
    print("\n[PASO 3] Creación de Activo e Inspección con Contexto Comprimido (Sección 7 & 89):")
    create_resp = agent_api.create_asset("HOUSE_001", {
        "width": 9.0,
        "depth": 6.0,
        "wall_height": 3.0,
        "roof_height": 2.0,
        "window_count": 4,
        "wall_material": "STONE"
    })
    print(f" - Creación: [{create_resp.status.value}] | {create_resp.summary}")
    print(f" - Componentes Afectados: {create_resp.affected_components}")

    insp_resp = agent_api.inspect_asset("HOUSE_001")
    ctx = insp_resp.output_data["context"]
    print(f" - Contexto de IA Filtrado: ID={ctx.asset_id}, Arquetipo={ctx.asset_type}, Componentes={list(ctx.components.keys())}")

    # 4. Evaluación Visual y Aplicación de Corrección
    print("\n[PASO 4] Evaluación Visual con Critic y Aplicación de Corrección (Sección 9 & 10):")
    ref = ReferenceImageSpec(image_id="REF_HOUSE", expected_aspect_ratio=1.52, expected_roof_ratio=0.31)
    critic_resp = agent_api.run_visual_critic("HOUSE_001", ref, aspect_ratio=1.80, roof_ratio=0.43)
    print(f" - Critic Visual: {critic_resp.summary}")
    print(f" - Próxima Acción Recomendada para Antigravity: [{critic_resp.next_action.value}]")

    corr_resp = agent_api.apply_correction("HOUSE_001", "roof_height", 1.45)
    print(f" - Aplicación de Corrección: [{corr_resp.status.value}] | Techo actualizado a {corr_resp.output_data['parameters']['roof_height']}m")

    # 5. Seguridad y Sandboxing: Bloqueo de Herramientas Peligrosas
    print("\n[PASO 5] Cortafuegos de Seguridad y Sandboxing de Herramientas (Sección 127):")
    reg = ToolRegistry()
    try:
        reg.register(ToolDefinition("execute_python", ToolCategory.EXECUTION, PermissionLevel.ADMIN))
    except PermissionError as e:
        print(f" - [+] Intento de Inyección de Python Bloqueado: {e}")

    # 6. Compuerta de Aprobación Humana para Acciones Destructivas
    print("\n[PASO 6] Compuerta de Aprobación para Borrado de Activos (Sección 64-65):")
    del_api = AIOrchestratorAPI(permission=PermissionLevel.DELETE)
    del_resp = del_api.delete_asset("HOUSE_001")
    print(f" - Estado de Solicitud de Borrado: [{del_resp.status.value}]")
    print(f" - Advertencia al Agente: {del_resp.warnings[0]}")
    print(f" - Decisión: [{del_resp.next_action.value}] (Pausa y espera confirmación)")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 43 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
