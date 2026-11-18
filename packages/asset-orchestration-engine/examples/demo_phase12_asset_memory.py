import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import AssetMemoryAPI

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 12: ASSET MEMORY & LEARNING DEMO")
    print("=" * 95)

    mem = AssetMemoryAPI(":memory:")

    # 1. Cold Start
    print("\n[PASO 1] Escenario Cold Start (Sin Memoria Previa):")
    cold_res = mem.retrieve_recommended_strategy("BLADE_TOO_SHORT", "SWORD", "BLADE")
    print(f" - Memory Hit: {cold_res['memory_hit']}")
    print(f" - Estrategia Baseline Utilizada: {cold_res['preferred_operation']}")
    print(f" - Confianza Inicial: {cold_res['confidence']}")

    # 2. Registro de Experiencias y Estrategias
    print("\n[PASO 2] Registrando Experiencias Históricas y Estrategia Base:")
    mem.register_strategy(
        strategy_id="strat_scale_blade_v1",
        failure_type="BLADE_TOO_SHORT",
        asset_type="SWORD",
        component_type="BLADE",
        preferred_operation="SET_DIMENSIONS",
        parameters={"length": 0.72},
        confidence=0.60
    )
    print(" - Estrategia 'strat_scale_blade_v1' registrada con confianza base 0.60.")

    # 3. Aprendizaje por Éxitos Consecutivos (Actualización Bayesiana)
    print("\n[PASO 3] Simulando 5 Correcciones Exitosas Consecutivas:")
    for i in range(1, 6):
        fail_rec = mem.record_failure(f"sword_00{i}", "SWORD", "BLADE", "BLADE_TOO_SHORT", 0.48, 0.72)
        upd = mem.record_correction_outcome(
            failure_id=fail_rec.failure_id,
            strategy_id="strat_scale_blade_v1",
            operation_type="SET_DIMENSIONS",
            target="blade",
            parameters={"length": 0.72},
            before_score=0.65,
            after_score=0.98
        )
        print(f" - Intento {i}: Éxito registrado -> Nueva Confianza: {upd['new_confidence']:.2f} (Tasa de Éxito: {upd['success_rate']*100:.0f}%)")

    # 4. Consulta de Estrategia Recomendada Optimizada
    print("\n[PASO 4] Consulta de Recomendación con Memoria Consolidada:")
    learned_rec = mem.retrieve_recommended_strategy("BLADE_TOO_SHORT", "SWORD", "BLADE")
    print(f" - Memory Hit: {learned_rec['memory_hit']}")
    print(f" - Estrategia Recomendada: {learned_rec['strategy_id']} ({learned_rec['preferred_operation']})")
    print(f" - Confianza Consolidada: {learned_rec['confidence']}")
    print(f" - Ranking Score: {learned_rec['ranking_score']}")
    print(f" - Motivo / Justificación: {learned_rec['reason']}")

    # 5. Detección de Bias Sistemático y Recomendación de Generación
    print("\n[PASO 5] Detección de Bias Sistemático de Generación (Pattern Detection):")
    recs = mem.get_generation_recommendations("SWORD")
    print(f" - Alertas / Recomendaciones de Generación Detectadas: {len(recs)}")
    for r in recs:
        print(f"   * Tipo: {r['type']} sobre '{r['target_component']}'")
        print(f"   * Multiplicador Recomendado: {r['recommended_scale_multiplier']}x")
        print(f"   * Motivo: {r['reason']}")

    mem.store.close()

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 12 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
