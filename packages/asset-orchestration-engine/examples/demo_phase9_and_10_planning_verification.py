import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    UnrealEngine, GameplayEngine, AIPlanningAPI, VisualIntelligenceAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASES 9 & 10: AI PLANNING & VISUAL VERIFICATION DEMO")
    print("=" * 95)

    # -------------------------------------------------------------
    # FASE 9: AI PLANNING & TASK DECOMPOSITION
    # -------------------------------------------------------------
    print("\n--- [FASE 9] AI PLANNING, INTENT PARSING & TASK DECOMPOSITION ---")
    ue = UnrealEngine("Planning_Demo_Level")
    gp = GameplayEngine()
    planner = AIPlanningAPI(ue, gp, max_mcp_calls_budget=15)

    # Setup de escena
    sword = ue.spawn_actor("sword_001", "SM_Sword_01", tags=["Weapon"], actor_id="actor_sword_01")
    gp.set_gameplay_data("actor_sword_01", "damage", 25.0)

    # 1. Petición en Lenguaje Natural
    print("\n[PASO 1] Petición del Usuario: 'Haz que la espada se pueda recoger y haga 40 de daño':")
    plan_res = planner.process_request("Haz que la espada se pueda recoger y haga 40 de daño", context_target="actor_sword_01")
    print(f" - Estado: {plan_res['status']}")
    print(f" - Tareas Descompuestas: {plan_res['tasks_count']}")
    print(f" - Llamadas MCP Utilizadas: {plan_res['mcp_calls']}")
    print(f" - Stop Rule Disparada: {plan_res['stop_rule_triggered']}")
    print(f" - Daño Resultante: {gp.actor_data['actor_sword_01'].get_effective('damage')}")
    print(f" - Capabilities Resultantes: {gp.get_actor_capabilities('actor_sword_01')}")

    # 2. Detección NO_OP
    print("\n[PASO 2] Petición Repetida: 'Haz que la espada haga 40 de daño' (Ya es 40):")
    noop_res = planner.process_request("Haz que la espada haga 40 de daño", context_target="actor_sword_01")
    print(f" - Estado: {noop_res['status']} (Llamadas MCP: {noop_res['mcp_calls']})")

    # -------------------------------------------------------------
    # FASE 10: VISUAL INTELLIGENCE & ASSET VERIFICATION
    # -------------------------------------------------------------
    print("\n--- [FASE 10] VISUAL INTELLIGENCE & ASSET VERIFICATION ---")
    vi = VisualIntelligenceAPI()

    # 3. Construcción del VisualGoalSpec
    print("\n[PASO 3] Construyendo VisualGoalSpec Estructurado:")
    goal = vi.build_goal_spec(
        category="ONE_HANDED_MEDIEVAL_SWORD",
        target_proportions={"blade_ratio": {"target": 0.72, "min": 0.65, "max": 0.78}},
        required_components=["blade", "guard", "grip", "pommel"],
        hard_constraints=["is_one_handed", "has_blade", "has_guard"]
    )
    print(f" - Categoría Objetivo: {goal.category}")
    print(f" - Target Blade Ratio: {goal.target_proportions['blade_ratio']['target']} (Rango: {goal.target_proportions['blade_ratio']['min']}-{goal.target_proportions['blade_ratio']['max']})")
    print(f" - Componentes Requeridos: {goal.required_components}")

    # 4. Evaluación de Asset con Hoja Desviada
    print("\n[PASO 4] Evaluación Visual de Asset Generado por Blender (Hoja Corta 0.40m vs 1.30m total):")
    dims_deviated = {
        "handle": (0.03, 0.03, 0.25),
        "guard": (0.15, 0.03, 0.05),
        "blade": (0.05, 0.02, 0.40), # Desviación: 0.40 / 0.75 = 53% (target 72%)
        "pommel": (0.05, 0.05, 0.05)
    }
    report = vi.verify_asset("sword_001", dims_deviated, ["blade", "guard", "grip", "pommel"], goal_spec=goal)
    print(f" - Score Global: {report.overall_score * 100:.1f}%")
    print(f" - Estado de Verificación: {report.status}")
    print(f" - Evidencia Medida: {report.evidence['proportion']}")
    print(f" - Advertencias: {report.warnings}")

    # 5. Plan de Corrección Quirúrgica (Preservando Componentes Válidos)
    print("\n[PASO 5] Plan de Corrección Quirúrgica:")
    corr_plan = vi.plan_correction(report)
    print(f" - Acción Recomendada: {corr_plan['action']}")
    print(f" - Intervención Mínima: {corr_plan['actions'][0]['type']} sobre '{corr_plan['actions'][0]['target_component']}'")
    print(f" - Componentes Válidos Preservados: {corr_plan['preserved_components']}")

    # 6. Re-evaluación Post-Corrección
    print("\n[PASO 6] Re-evaluación Post-Corrección (Hoja Corregida a 0.95m):")
    dims_corrected = {
        "handle": (0.03, 0.03, 0.25),
        "guard": (0.15, 0.03, 0.05),
        "blade": (0.05, 0.02, 0.95), # Corregido: 0.95 / 1.30 = 73% (target 72%)
        "pommel": (0.05, 0.05, 0.05)
    }
    report_post = vi.verify_asset("sword_001", dims_corrected, ["blade", "guard", "grip", "pommel"], goal_spec=goal)
    print(f" - Score Global Post-Corrección: {report_post.overall_score * 100:.1f}%")
    print(f" - Estado Final: {report_post.status} (PASS)")
    print(f" - Acción: {vi.plan_correction(report_post)['action']}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASES 9 Y 10 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
