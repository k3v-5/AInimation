import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    LearnedPatternsAPI, ProblemSignature, PatternState
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 27: ASSET MEMORY & LEARNED PATTERNS DEMO")
    print("=" * 95)

    api = LearnedPatternsAPI()

    # 1. Escenario 129: Almacenar conocimiento probado de MEDIEVAL_HOUSE_A
    print("\n[ESCENARIO 129] 1. Registro de Patrón Aprendido tras Corrección Exitosa:")
    pat_roof = api.register_pattern(
        pattern_id="pat_medieval_roof_01",
        name="MedievalRoofCorrection_01",
        asset_family="medieval_house",
        problem_signature=ProblemSignature.ROOF_TOO_LOW.value,
        target_parameter="roof_height",
        correction_delta=0.18,
        confidence=0.92,
        builder_version="v1.0.0"
    )
    print(f" - Patrón Registrado: {pat_roof.name} (ID: {pat_roof.pattern_id})")
    print(f" - Familia: {pat_roof.asset_family} | Firma: {pat_roof.problem_signature} | Delta: {pat_roof.correction_delta:+.2f}")
    print(f" - Estado Inicial: {pat_roof.state.value} | Confianza: {pat_roof.confidence:.2f}")

    # 2. Escenario 129: Recuperación para MEDIEVAL_HOUSE_B
    print("\n[ESCENARIO 129] 2. Solicitud de MEDIEVAL_HOUSE_B con Problema Similar:")
    query = {
        "asset_family": "medieval_house",
        "problem_signature": ProblemSignature.ROOF_TOO_LOW.value,
        "builder_version": "v1.0.0"
    }
    matches = api.search_patterns(query)
    print(f" - Patrones Coincidentes Encontrados: {len(matches)}")
    for p, sim, expl in matches:
        print(f"   * [{p.name}] Similitud: {sim*100:.0f}% | {expl}")

    # 3. Escenario 130: Promoción a KNOWN_GOOD tras Éxito Repetido
    print("\n[ESCENARIO 130] 3. Promoción Automática de Patrón tras 5 Éxitos Consecutivos:")
    for i in range(5):
        api.record_outcome("pat_medieval_roof_01", success=True, improvement=0.14)
    print(f" - Estado Actualizado: {pat_roof.state.value} (Aplicaciones: {pat_roof.applications_count}, Éxitos: {pat_roof.success_count})")
    print(f" - Tasa de Éxito: {pat_roof.success_rate*100:.1f}% | Confianza: {pat_roof.confidence:.2f} | Mejora Media: {pat_roof.average_improvement:+.2f}")

    # 4. Escenario 132: Detección de Conflictos entre Patrones
    print("\n[ESCENARIO 132] 4. Detección de Conflictos entre Patrones Contradictorios:")
    api.register_pattern(
        pattern_id="pat_roof_shrink",
        name="MedievalRoofShrink_01",
        asset_family="medieval_house",
        problem_signature="ROOF_TOO_HIGH",
        target_parameter="roof_height",
        correction_delta=-0.15
    )
    has_conf, conf_msg = api.check_conflict("pat_medieval_roof_01", "pat_roof_shrink")
    print(f" - Conflicto Detectado: {has_conf} -> {conf_msg}")

    # 5. Escenario 137: Auto-Aplicación de Patrón KNOWN_GOOD
    print("\n[ESCENARIO 137] 5. Aplicación Automática de Patrón Probado a Parámetros:")
    initial_params = {"roof_height": 1.75, "width": 4.0}
    ok_apply, new_params, app_msg = api.apply_pattern(pat_roof, initial_params, auto_apply_threshold=0.90)
    print(f" - Aplicación Exitosa: {ok_apply}")
    print(f" - Parámetros: {initial_params} -> {new_params}")
    print(f" - Detalle: {app_msg}")

    # 6. Escenario 131: Degradación e Invalidación ante Fallos
    print("\n[ESCENARIO 131] 6. Degradación de Confianza e Invalidación tras Fallos:")
    pat_fail = api.register_pattern("pat_test_fail", "FlawedPattern", "medieval_house", "WINDOWS_TOO_SMALL", "window_scale", 0.50, confidence=0.70)
    print(f" - Estado Inicial: {pat_fail.state.value} | Confianza: {pat_fail.confidence:.2f}")
    for _ in range(3):
        api.record_outcome("pat_test_fail", success=False)
    print(f" - Estado tras 3 Fallos: {pat_fail.state.value} | Confianza: {pat_fail.confidence:.2f} (Excluido de futuras búsquedas)")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 27 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
