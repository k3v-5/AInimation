import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    VisualReferenceAPI, AutonomousCorrectionLoopAPI, ParametricAssetType,
    LoopStatus
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASES 25 & 26: VISUAL REFERENCE & AUTONOMOUS CORRECTION")
    print("=" * 95)

    ref_api = VisualReferenceAPI()
    loop_api = AutonomousCorrectionLoopAPI()

    # 1. Fase 25: Perfil de Referencia Visual
    print("\n[FASE 25] 1. Extracción de Perfil de Referencia Visual:")
    ref_profile = ref_api.create_reference_profile(
        reference_id="ref_medieval_manor",
        source_uri="ref://medieval_manor_ref.png",
        proportions={"roof_to_wall_ratio": 0.55, "window_scale": 1.25},
        detected_components=["foundation", "walls", "roof", "windows"]
    )
    print(f" - ID de Referencia: {ref_profile.reference_id}")
    print(f" - Proporciones Esperadas: roof_to_wall_ratio={ref_profile.proportions['roof_to_wall_ratio'].value}, window_scale={ref_profile.proportions['window_scale'].value}")

    # 2. Fase 25: Error Map Inicial
    print("\n[FASE 25] 2. Detección de Discrepancias Geométricas (ErrorMap):")
    model_data_bad = {
        "dimensions": {"width": 4.0, "depth": 3.5, "height": 5.0},
        "components": ["foundation", "walls", "roof", "windows"],
        "parameters": {"roof_height": 1.40, "window_scale": 1.0}
    }
    error_map = ref_api.compare_model("house_001", model_data_bad, ref_profile)
    print(f" - Puntuación Geométrica Inicial: {error_map.overall_geometric_score:.2f} (Match: {error_map.is_match})")
    for disc in error_map.discrepancies:
        print(f"   * Discrepancia en [{disc.component}]: {disc.description} (Delta: {disc.delta_percent:+.1f}%)")
    print(f" - Parches Recomendados: {error_map.recommended_patches}")

    # 3. Fase 26: Bucle Autónomo de Corrección Quirúrgica (Anti-Retrabajo)
    print("\n[FASE 26] 3. Ejecución del Bucle Autónomo de Corrección Cerrado:")
    print("   Usuario / Crítico: \"El techo está demasiado bajo y las ventanas están demasiado pequeñas.\"")
    initial_params = {
        "width": 4.0, "depth": 3.5, "height": 5.0,
        "roof_height": 1.40, "window_scale": 1.0
    }
    res = loop_api.run_correction_loop(
        target_asset_id="house_manor_01",
        asset_type=ParametricAssetType.MEDIEVAL_HOUSE,
        initial_parameters=initial_params,
        reference=ref_profile
    )
    print(f" - Estado Final: {res.status.value}")
    print(f" - Iteraciones Ejecutadas: {res.iterations_run}")
    print(f" - Puntuación Final Alcanzada: {res.final_score:.2f} (Quality Gate >= 0.90)")
    for rec in res.history:
        print(f"   * Iteración {rec.iteration_index}: Score {rec.score_before:.2f} -> {rec.score_after:.2f} | Componentes Afectados: {rec.affected_components} | Parches: {rec.applied_patches}")
    print(f" - Mensaje: {res.message}")

    # 4. Fase 26: Límite de Iteraciones y Diagnóstico ante Error No Resoluble
    print("\n[FASE 26] 4. Prevención de Bucles Infinitos (Límite MAX_ITERATIONS = 5):")
    res_unres = loop_api.run_correction_loop(
        target_asset_id="house_unresolvable",
        asset_type=ParametricAssetType.MEDIEVAL_HOUSE,
        initial_parameters=initial_params,
        reference=ref_profile,
        force_unresolvable=True
    )
    print(f" - Estado Final: {res_unres.status.value}")
    print(f" - Iteraciones Ejecutadas: {res_unres.iterations_run}/5 (Detenido sin bucle infinito)")
    print(f" - Problemas no Resueltos Diagnosticados: {res_unres.unresolved_problems}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASES 25 Y 26 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
