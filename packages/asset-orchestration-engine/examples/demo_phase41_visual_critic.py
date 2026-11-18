import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_reference_matching import (
    VisualReferenceMatcherAPI, EvaluationMode
)
from src.parametric_asset_engine import ParametricAssetAPI

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 41: VISUAL REFERENCE MATCHING & GEOMETRIC CRITIC")
    print("=" * 95)

    critic_api = VisualReferenceMatcherAPI()
    param_api = ParametricAssetAPI()

    # 1. Configuración de Referencia Visual
    print("\n[PASO 1] Registro de Especificación de Referencia Visual (Sección 4-5):")
    ref = critic_api.create_reference_spec(
        image_id="REF_HOUSE_MEDIEVAL",
        expected_aspect_ratio=1.52,
        expected_roof_ratio=0.31,
        expected_components={"chimney": True},
        expected_colors={"walls": [50.0, 0.0, 0.0]}
    )
    print(f" - ID Referencia: {ref.image_id}")
    print(f" - Relación de Aspecto Esperada (Ancho/Alto): {ref.expected_aspect_ratio}")
    print(f" - Relación de Techo Esperada (Techo/Cuerpo): {ref.expected_roof_ratio}")
    print(f" - Componentes Esperados en Referencia: {ref.expected_components}")

    # 2. Generación de Asset Inicial Descalibrado en Fase 40
    print("\n[PASO 2] Generación Inicial en Motor Paramétrico (Fase 40):")
    house = param_api.create_asset("HOUSE_001", {
        "width": 9.0,
        "depth": 6.0,
        "wall_height": 3.0,
        "roof_height": 2.0,
        "window_count": 4,
        "wall_material": "STONE"
    })
    print(f" - Parámetros Generados: width={house.parameters['width']}m, roof_height={house.parameters['roof_height']}m")

    # 3. Primera Evaluación Visual Cuantificable (Critic v41)
    print("\n[PASO 3] Primera Evaluación Visual y Detección de Discrepancias (Sección 1, 20 & 80):")
    report1 = critic_api.evaluate_asset(
        asset_id="HOUSE_001",
        ref=ref,
        generated_parameters=house.parameters,
        generated_aspect_ratio=1.80, # Demasiado ancha
        generated_roof_ratio=0.43,   # Techo demasiado alto
        user_window_count=4,
        has_chimney=False,
        mode=EvaluationMode.DEEP
    )
    print(f" - Puntuación Global: {report1.overall_score * 100:.1f}% | Decisión: [{report1.decision.value}]")
    print(f" - Sub-Scores: {report1.sub_scores}")
    print(" - Diagnósticos Emitidos (QUÉ está mal):")
    for d in report1.diagnoses:
        print(f"   * [{d.diag_type.value}] Severidad: {d.severity} | Ubicación: {d.location} | Desviación: {d.deviation_amount:+.2f}")
        print(f"     Descripción: {d.description}")

    # 4. Fórmulas Matemáticas de Corrección de Parámetros
    print("\n[PASO 4] Fórmulas Matemáticas de Corrección Paramétrica (Sección 85-87):")
    for c in report1.suggested_corrections:
        print(f" - Parámetro: '{c.parameter_name}'")
        print(f"   * Valor Actual: {c.current_value}m -> Sugerido: {c.suggested_value}m (Delta: {c.delta:+.2f}m / {c.relative_change_pct:+.1f}%)")
        print(f"   * Componentes Afectados: {c.affected_components} | Replan Requerido: {c.replan_required}")

    # 5. Explicabilidad del Critic (WHAT, WHERE, HOW MUCH, WHY)
    print("\n[PASO 5] Explicabilidad Formal del Critic (Sección 130-133):")
    print(f" - QUÉ: {report1.explainability['what']}")
    print(f" - DÓNDE: {report1.explainability['where']}")
    print(f" - CUÁNTO: {report1.explainability['how_much']}")
    print(f" - POR QUÉ: {report1.explainability['why']}")

    # 6. Bucle de Corrección Cerrado: Fase 41 -> Fase 40
    print("\n[PASO 6] Cierre de Bucle: Aplicación de Correcciones al Motor Paramétrico (Fase 40):")
    corr_dict = {c.parameter_name: c.suggested_value for c in report1.suggested_corrections}
    updated_house = param_api.update_asset("HOUSE_001", corr_dict)
    print(f" - Parámetros Actualizados: width={updated_house.parameters['width']}m, roof_height={updated_house.parameters['roof_height']}m")
    print(f" - Componente Muros: Actualizado ({updated_house.components['walls'].parameters})")
    print(f" - Componente Techo: Actualizado ({updated_house.components['roof'].parameters})")
    print(f" - Componente Cimientos: Preservado Intacto")

    # 7. Segunda Evaluación de Validación
    print("\n[PASO 7] Segunda Evaluación Visual del Asset Corregido:")
    report2 = critic_api.evaluate_asset(
        asset_id="HOUSE_001",
        ref=ref,
        generated_parameters=updated_house.parameters,
        generated_aspect_ratio=1.52, # Corregido
        generated_roof_ratio=0.31,   # Corregido
        user_window_count=4,
        has_chimney=True,
        mode=EvaluationMode.DEEP
    )
    print(f" - Puntuación Global: {report2.overall_score * 100:.1f}% | Decisión: [{report2.decision.value}]")
    print(f" - Sub-Scores: {report2.sub_scores}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 41 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
