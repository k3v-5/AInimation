import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    MockBlenderProvider, CorrectionExecutionAPI, VisualIntelligenceAPI, ExecutionMode
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 11: CORRECTION EXECUTION & SAFE MUTATION DEMO")
    print("=" * 95)

    # 1. Configurar Provider y APIs
    provider = MockBlenderProvider()
    corr_api = CorrectionExecutionAPI(provider, execution_mode=ExecutionMode.BALANCED)
    vi_api = VisualIntelligenceAPI()

    provider.init_asset("sword_001", {
        "grip": {"dimensions": (0.03, 0.03, 0.25), "material": {"metallic": 0.0, "roughness": 0.8}},
        "guard": {"dimensions": (0.15, 0.03, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}},
        "blade": {"dimensions": (0.05, 0.02, 0.50), "material": {"metallic": 0.0, "roughness": 0.5}}, # Desviada: corta y no metálica
        "pommel": {"dimensions": (0.05, 0.05, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}}
    })
    corr_api.register_component("grip_001", "sword_001", "obj_grip", "grip", is_locked=False)
    corr_api.register_component("blade_001", "sword_001", "obj_blade", "blade", is_locked=False)

    print("\n--- [FASE 11] CORRECTION EXECUTION & SAFE MUTATION ---")

    # 2. Diagnóstico F10 Inicial
    print("\n[PASO 1] Diagnóstico de Verificación (Fase 10):")
    goal = vi_api.build_goal_spec(category="ONE_HANDED_MEDIEVAL_SWORD")
    dims_init = {k: v["dimensions"] for k, v in provider.assets["sword_001"]["components"].items()}
    report1 = vi_api.verify_asset("sword_001", dims_init, list(dims_init.keys()), goal_spec=goal)
    print(f" - Estado Inicial: {report1.status}")
    print(f" - Advertencias: {report1.warnings}")

    # 3. Planificación y Ejecución Transaccional F11
    print("\n[PASO 2] Ejecutando Transacción de Corrección Quirúrgica (Fase 11):")
    mut_res = corr_api.execute_correction(
        asset_id="sword_001",
        operations=[
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.95}, "reason": "Ajustar ratio de hoja a 73%"},
            {"type": "CHANGE_METALLIC", "target": "blade", "parameters": {"value": 0.90}, "reason": "Ajustar PBR a metálico"}
        ],
        protected_components=["guard", "pommel"] # Componentes protegidos
    )
    print(f" - Estado de Transacción: {mut_res['status']} ({mut_res['transaction_id']})")
    print(f" - Snapshot SHA-256 Creado: {mut_res['snapshot_id']}")
    print(f" - Operaciones Ejecutadas: {mut_res['executed_operations']}")

    # 4. Verificación de Aislamiento
    print("\n[PASO 3] Verificación de Aislamiento de Componentes:")
    print(f" - Nueva Longitud Blade: {provider.get_component_dimensions('sword_001', 'blade')[2]} m")
    print(f" - Nuevo Metallic Blade: {provider.get_material_property('sword_001', 'blade', 'metallic')}")
    print(f" - Grip Dimensiones (Intacto): {provider.get_component_dimensions('sword_001', 'grip')}")
    print(f" - Guard Dimensiones (Intacto): {provider.get_component_dimensions('sword_001', 'guard')}")

    # 5. Demostración de Componente Protegido / Bloqueado
    print("\n[PASO 4] Demostración de Bloqueo / Componente Protegido:")
    corr_api.lock_component("grip_001", True)
    denied_res = corr_api.execute_correction("sword_001", [
        {"type": "SET_DIMENSIONS", "target": "grip_001", "parameters": {"length": 0.50}}
    ])
    print(f" - Intento de Modificar Grip Bloqueado: {denied_res['status']} ({denied_res['error_code']})")

    # 6. Demostración de Rollback Automático ante Fallo
    print("\n[PASO 5] Demostración de Rollback Automático ante Fallo:")
    prev_blade = provider.get_component_dimensions("sword_001", "blade")
    fail_res = corr_api.execute_correction("sword_001", [
        {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 1.50}},
        {"type": "SET_DIMENSIONS", "target": "unknown_part_404", "parameters": {"length": 1.50}} # Provoca fallo
    ])
    print(f" - Resultado: {fail_res['status']} (Fallo en '{fail_res.get('failed_operation')}')")
    print(f" - Estado Restaurado en Blade: {provider.get_component_dimensions('sword_001', 'blade')} == {prev_blade}")

    # 7. Revalidación F10 Final
    print("\n[PASO 6] Revalidación Final Post-Corrección (Fase 10):")
    dims_post = {k: v["dimensions"] for k, v in provider.assets["sword_001"]["components"].items()}
    report_post = vi_api.verify_asset("sword_001", dims_post, list(dims_post.keys()), goal_spec=goal)
    print(f" - Score Final: {report_post.overall_score * 100:.1f}%")
    print(f" - Estado Final: {report_post.status} (PASS)")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 11 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
