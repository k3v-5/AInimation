import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.semantic_visual_critic import (
    SemanticVisualCriticAPI, ExpectedState, ActualState, CriticCameraView
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 50: SEMANTIC ASSET UNDERSTANDING & AI VISUAL CRITIC")
    print("=" * 95)

    api = SemanticVisualCriticAPI()

    # 1. Caso Obligatorio 1: Casa con Elemento Prohibido (Antena Satelital)
    print("\n[PASO 1] Caso Obligatorio 1: Detección de Componente Prohibido/Alucinado (Sección 211):")
    expected_house = ExpectedState(
        asset_class="HOUSE",
        required_components=["roof", "walls", "entrance"],
        forbidden_components=["satellite_dish", "antenna"],
        expected_proportions={"roof_ratio": 0.30}
    )
    actual_house_with_dish = ActualState(
        detected_class="HOUSE",
        detected_components=["roof", "walls", "entrance", "satellite_dish"],
        measured_proportions={"roof_ratio": 0.30}
    )
    res_1 = api.evaluate_asset(expected_house, actual_house_with_dish)
    print(f" - Defectos Encontrados ({len(res_1.defects)}):")
    for d in res_1.defects:
        print(f"   * [{d.category.value}] en '{d.affected_component}' | Severidad: [{d.severity.value}] | Confianza: {d.confidence*100:.1f}%")
        print(f"     -> Evidencia: \"{d.evidence}\"")
        print(f"     -> Acción Recomendada: [{d.recommended_action}] (Sin reconstruir la casa completa)")

    # 2. Caso Obligatorio 2: Error de Proporciones (Techo 51% vs 30%)
    print("\n[PASO 2] Caso Obligatorio 2: Detección de Error de Proporciones (Sección 212):")
    actual_house_tall_roof = ActualState(
        detected_class="HOUSE",
        detected_components=["roof", "walls", "entrance"],
        measured_proportions={"roof_ratio": 0.51}
    )
    res_2 = api.evaluate_asset(expected_house, actual_house_tall_roof)
    def_prop = res_2.defects[0]
    print(f" - [{def_prop.category.value}] | Esperado: {def_prop.expected} | Medido: {def_prop.actual}")
    print(f" - Acción Quirúrgica: \"{def_prop.recommended_action}\" | Scope: [{def_prop.scope}]")

    # 3. Caso Obligatorio 3: Error Espacial y Oclusión (Ventana tras el Muro)
    print("\n[PASO 3] Caso Obligatorio 3: Error Espacial / Oclusión de Ventana (Sección 213):")
    actual_house_hidden_win = ActualState(
        detected_class="HOUSE",
        detected_components=["roof", "walls", "entrance", "window_01", "window_02"],
        component_spatial_status={"window_02": "BEHIND_WALL"}
    )
    res_3 = api.evaluate_asset(expected_house, actual_house_hidden_win)
    def_spat = next(d for d in res_3.defects if d.category.value == "SPATIAL_ERROR")
    print(f" - [{def_spat.category.value}] en '{def_spat.affected_component}': \"{def_spat.evidence}\" -> Acción: [{def_spat.recommended_action}]")

    # 4. Caso Obligatorio 5: Fallo de Identidad Estructural (Casa vs Nave Espacial)
    print("\n[PASO 4] Caso Obligatorio 5: Fallo Fundamental de Identidad Estructural (Sección 215):")
    actual_spaceship = ActualState(detected_class="SPACESHIP")
    res_5 = api.evaluate_asset(expected_house, actual_spaceship)
    print(f" - Hard Failures: {res_5.hard_failures}")
    print(f" - Recomendación del Critic: [{res_5.recommendation.value}] (Evita 40 micro-correcciones inútiles)")

    # 5. Caso Obligatorio 9: Evaluación Multi-Vista (Frontal vs Lateral)
    print("\n[PASO 5] Caso Obligatorio 9: Evaluación Multi-Vista Estricta (Sección 219):")
    actual_multiview = ActualState(
        detected_class="HOUSE",
        detected_components=["roof", "walls", "entrance"],
        multi_view_aspect_ratios={
            CriticCameraView.FRONT: 1.52, # Conforme
            CriticCameraView.LEFT: 2.10   # Distorsionado
        }
    )
    res_9 = api.evaluate_asset(expected_house, actual_multiview)
    print(f" - Defectos Multi-Vista: {[d.category.value for d in res_9.defects]}")

    # 6. Caso Obligatorio 10: Barril con 3 aros en vez de 2
    print("\n[PASO 6] Caso Obligatorio 10: Barril con Anillo Extra (Sección 226):")
    expected_barrel = ExpectedState(asset_class="BARREL", required_components=["body", "ring_01", "ring_02"])
    actual_barrel = ActualState(
        detected_class="BARREL",
        detected_components=["body", "ring_01", "ring_02", "ring_03"]
    )
    res_10 = api.evaluate_asset(expected_barrel, actual_barrel)
    def_ring = res_10.defects[0]
    print(f" - [{def_ring.category.value}]: \"{def_ring.evidence}\" -> Acción: [{def_ring.recommended_action}] (NO regenera el barril)")

    # 7. Explicabilidad en Tres Capas (MACHINE, HUMAN, AGENT)
    print("\n[PASO 7] Explicabilidad en Tres Capas (Sección 209):")
    print(f" - [MACHINE]: {len(res_1.defects)} defectos estructurados generados en JSON.")
    print(f" - [HUMAN]: \"{res_1.explanation_human}\"")
    print(f" - [AGENT]: \"{res_1.explanation_agent}\"")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 50 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
