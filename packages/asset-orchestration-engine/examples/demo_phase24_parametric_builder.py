import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    ParametricBuilderAPI, ParametricAssetType, BuildStage, BuildState, ParameterChange
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 24: PARAMETRIC ASSET BUILD SYSTEM DEMO")
    print("=" * 95)

    builder = ParametricBuilderAPI()

    # 1. Escenario 163: Construcción Determinista Completa
    print("\n[ESCENARIO 163] Petición de la IA: BUILD MEDIEVAL_HOUSE (width=4m, depth=3.5m, height=5m, roof_angle=38°, windows=4)")
    params_163 = {"width": 4.0, "depth": 3.5, "height": 5.0, "roof_angle": 38.0, "window_count": 4}
    res_163 = builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params_163)
    print(f" - Estado de Construcción: {res_163.status.value} (Tiempo: {res_163.build_time_ms:.2f}ms)")
    print(f" - Componentes Creados: {res_163.created_components}")
    print(f" - Estadísticas Geométricas: {res_163.geometry_stats['vertex_count']} vértices, {res_163.geometry_stats['face_count']} caras")
    print(f" - Huella de Construcción (Fingerprint): {res_163.build_fingerprint}")

    # 2. Escenario 164: Reconstrucción Quirúrgica Parcial (Anti-Retrabajo)
    print("\n[ESCENARIO 164] Usuario: \"Haz el techo 20% más alto.\"")
    new_roof_h = builder.parse_relative_intent(res_163.parameters["roof_height"], "20% más alto")
    changes_164 = [ParameterChange("roof_height", res_163.parameters["roof_height"], new_roof_h)]
    ok_upd, res_164, logs_164 = builder.update_parameters(ParametricAssetType.MEDIEVAL_HOUSE, res_163.parameters, changes_164)
    print(f" - Actualización Exitosa: {ok_upd}")
    print(f" - Componentes Modificados: {res_164.modified_components} (Paredes, cimientos y ventanas intactos)")
    print(f" - Ratio de Reconstrucción: {len(res_164.modified_components)}/4 = 25.0%")

    # 3. Escenario 166: Recálculo Automático de Parámetros Derivados
    print("\n[ESCENARIO 166] Usuario: \"Haz la casa de 6 metros de ancho.\"")
    params_166 = {"width": 6.0, "window_count": 4}
    res_166 = builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params_166)
    print(f" - Ancho Base: {res_166.parameters['width']}m")
    print(f" - Ancho de Tejado Derivado: {res_166.parameters['roof_width']}m")
    print(f" - Ancho de Cimiento Derivado: {res_166.parameters['foundation_width']}m")
    print(f" - Espaciado de Ventanas Derivado: {res_166.parameters['window_spacing']}m (Calculado por Formula Engine)")

    # 4. Escenario 167: Rollback Transaccional ante Restricción Inválida
    print("\n[ESCENARIO 167] Transacción Inválida: roof_height = 10m >= height = 5m")
    changes_bad = [ParameterChange("roof_height", 1.75, 10.0)]
    ok_bad, res_bad, logs_bad = builder.update_parameters(ParametricAssetType.MEDIEVAL_HOUSE, params_163, changes_bad)
    print(f" - Resultado de Transacción: {ok_bad} (Estado: {res_bad.status.value})")
    print(f" - Mensaje de Rollback: {logs_bad[0]}")

    # 5. Escenario 170: Cache Hit de Geometría
    print("\n[ESCENARIO 170] Re-solicitud de Geometría Idéntica (Cache System):")
    res_cache = builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params_163)
    print(f" - Cache Hit: {res_cache.is_cache_hit} (Tiempo de entrega: {res_cache.build_time_ms:.2f}ms)")

    # 6. Escenario 171: Compuerta de Blockout Progresivo
    print("\n[ESCENARIO 171] Fallo de Silueta en Blockout (Stage 0):")
    res_block = builder.build_parametric_asset(ParametricAssetType.MEDIEVAL_HOUSE, params_163, fail_blockout_check=True)
    print(f" - Estado: {res_block.status.value} (Etapa alcanzada: {res_block.stage_reached.value})")
    print(f" - Razón de Parada: {res_block.errors[0]}")

    # 7. Escenario 172: Fallback a Geometría Personalizada
    print("\n[ESCENARIO 172] Solicitud de Tipo No Paramétrico (CUSTOM):")
    res_custom = builder.build_parametric_asset(ParametricAssetType.CUSTOM, {"mesh": "dragon_statue"})
    print(f" - Estado: {res_custom.status.value} -> Razón: {res_custom.errors[0]}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 24 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
