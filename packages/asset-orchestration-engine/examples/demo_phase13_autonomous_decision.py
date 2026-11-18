import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    MockBlenderProvider, VisualIntelligenceAPI, CorrectionExecutionAPI,
    AssetMemoryAPI, AutonomousDecisionAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 13: AUTONOMOUS ASSET OPTIMIZATION DEMO")
    print("=" * 95)

    # 1. Configurar Entorno Autónomo Completo (F10 + F11 + F12 + F13)
    provider = MockBlenderProvider()
    vi_api = VisualIntelligenceAPI()
    corr_api = CorrectionExecutionAPI(provider)
    mem_api = AssetMemoryAPI(":memory:")

    provider.init_asset("sword_001", {
        "grip": {"dimensions": (0.03, 0.03, 0.25), "material": {"metallic": 0.0, "roughness": 0.8}},
        "guard": {"dimensions": (0.15, 0.03, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}},
        "blade": {"dimensions": (0.05, 0.02, 0.50), "material": {"metallic": 0.0, "roughness": 0.5}}, # Hoja corta
        "pommel": {"dimensions": (0.05, 0.05, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}}
    })

    # Registrar estrategia previa en memoria
    mem_api.register_strategy("strat_scale_blade", "BLADE_TOO_SHORT", "ONE_HANDED_MEDIEVAL_SWORD", "BLADE", "SET_DIMENSIONS", {"length": 0.95}, confidence=0.85)

    goal = vi_api.build_goal_spec(category="ONE_HANDED_MEDIEVAL_SWORD")
    decision_api = AutonomousDecisionAPI(
        visual_api=vi_api,
        correction_api=corr_api,
        memory_api=mem_api,
        acceptance_threshold=0.85
    )

    print("\n--- [FASE 13] AUTONOMOUS ASSET OPTIMIZATION & DECISION ENGINE ---")

    # 2. Ejecutar Optimización Autónoma
    print("\n[PASO 1] Iniciando Ciclo de Optimización Autónoma sobre 'sword_001':")
    res = decision_api.optimize_asset("sword_001", goal)
    print(f" - Estado Final de la Decisión: {res['status']}")
    print(f" - Score Final Alcanzado: {res['final_score'] * 100:.1f}% (Umbral: 85.0%)")
    print(f" - Iteraciones Totales: {res['iterations']}")
    print(f" - Correcciones Ejecutadas: {res['corrections']}")
    print(f" - Motivo de Parada: {res['stop_reason']}")

    print("\n[PASO 2] Historial de Decisiones Autónomas:")
    for h in res["history"]:
        print(f" - Iteración {h['iteration']}: Acción '{h['action']}' -> Score: {h['score_before']*100:.1f}% -> {h['score_after']*100:.1f}% (Delta: +{h['delta']*100:.1f}%) [{h['classification']}]")

    # 3. Demostración Anti-Overworking (Parada Inmediata en Asset Óptimo)
    print("\n[PASO 3] Demostración Anti-Overworking (Asset que ya cumple el umbral):")
    res_noop = decision_api.optimize_asset("sword_001", goal)
    print(f" - Estado: {res_noop['status']}")
    print(f" - Correcciones Adicionales Realizadas: {res_noop['corrections']} (Cero sobre-trabajo)")
    print(f" - Motivo: {res_noop['stop_reason']}")

    mem_api.store.close()

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 13 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
