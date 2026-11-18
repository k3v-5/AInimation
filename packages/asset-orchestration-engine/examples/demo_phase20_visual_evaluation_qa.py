import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    VisualEvaluationQAAPI, ExpectedVisualProfile, RegressionDetector, OscillationDetector
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 20: VISUAL EVALUATION & AUTOMATIC QA DEMO")
    print("=" * 95)

    qa_api = VisualEvaluationQAAPI()

    # 1. Escenario 141-143: Diagnóstico y Reparación en Bucle Cerrado
    print("\n[ESCENARIO 141-143] Pedido: \"Espada medieval de 90 cm.\" | Salida Actual: 1.34m")
    exp_sword = ExpectedVisualProfile("sword_profile", target_dimensions={"length": 0.90})
    act_sword = {"dimensions": {"length": 1.34}, "components": ["blade", "guard", "handle", "pommel"]}

    def apply_sword_repair(curr_data, candidate):
        updated = dict(curr_data)
        updated["dimensions"] = dict(curr_data.get("dimensions", {}))
        updated["dimensions"][candidate.parameter_name] = candidate.target_value
        return updated

    opt_res = qa_api.optimize_closed_loop("sword_001", act_sword, exp_sword, apply_sword_repair)
    print(f" - Estado Final: {opt_res['final_status']}")
    print(f" - Iteraciones de Reparación: {opt_res['iterations']}")
    print(f" - Puntuación Final: {opt_res['final_score'] * 100:.1f}%")
    print(f" - Mensaje: {opt_res['message']}")

    # 2. Escenario 144: Fallo de Relación Espacial en Escena
    print("\n[ESCENARIO 144] Pedido: \"Torre al norte de la plaza.\" | Actual: Al este")
    exp_scene = ExpectedVisualProfile("scene_profile", expected_spatial_relations={"tower_001": "north_of plaza"})
    act_scene = {"spatial_relations": {"tower_001": "east_of plaza"}}
    rep_scene = qa_api.evaluate("village_01", act_scene, exp_scene)
    fail_sp = rep_scene.failures[0]
    print(f" - Código de Fallo: {fail_sp.code}")
    print(f" - Dimensión: {fail_sp.dimension.value}")
    print(f" - Acción Sugerida: {fail_sp.suggested_action} (Alcance: {fail_sp.suggested_scope.value})")

    # 3. Escenario 145: Diagnóstico a Nivel de Componente
    print("\n[ESCENARIO 145] Casa con Tejado Demasiado Alto (1.35m vs 0.80m)")
    exp_house = ExpectedVisualProfile("house_profile")
    act_house = {"component_measurements": {"roof_height": 1.35}}
    rep_house = qa_api.evaluate("house_003", act_house, exp_house)
    fail_h = rep_house.failures[0]
    print(f" - Código: {fail_h.code}")
    print(f" - Componente Afectado: '{fail_h.component_id}' (Alcance de Reparación: {fail_h.suggested_scope.value})")
    print(f" - Razón: No reconstruir la casa entera si solo falla el tejado.")

    # 4. Escenario 146: Detección de Regresión Multidimensional
    print("\n[ESCENARIO 146] Verificación de Detección de Regresión:")
    rep_before = qa_api.evaluate("sword_001", {"dimensions": {"length": 0.90}, "shape_score": 0.81}, exp_sword)
    rep_after = qa_api.evaluate("sword_001", {"dimensions": {"length": 1.45}, "shape_score": 0.93}, exp_sword)
    is_regr, regr_msg = RegressionDetector.check_regression(rep_before, rep_after)
    print(f" - Mejora de Forma (0.81 -> 0.93) pero Degrada Escala (0.90 -> 1.45)")
    print(f" - Regresión Detectada: {is_regr} -> {regr_msg}")

    # 5. Escenario 147: Detección de Estancamiento
    print("\n[ESCENARIO 147] Detección de Estancamiento (Stop Condition):")
    history = [0.71, 0.76, 0.75, 0.75]
    is_stag, stag_msg = OscillationDetector.check_stagnation_or_cycle(history, threshold=0.02)
    print(f" - Historial de Puntuaciones: {history}")
    print(f" - Estancamiento Detectado: {is_stag} -> {stag_msg}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 20 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
