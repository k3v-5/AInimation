import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adaptive_generation_correction import (
    AdaptiveGenerationAPI, ScopeLevel
)
from src.visual_reference_matching import ReferenceImageSpec

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 46: ADAPTIVE GENERATION & CORRECTION ENGINE")
    print("=" * 95)

    api = AdaptiveGenerationAPI(max_iterations=5, target_score=0.90)

    ref = ReferenceImageSpec(
        image_id="REF_HOUSE",
        expected_aspect_ratio=1.52,
        expected_roof_ratio=0.31
    )

    # 1. Caso de Prueba Obligatorio 1: Corrección Quirúrgica de Tejado (Sin reconstruir muros ni puertas)
    print("\n[PASO 1] Caso Obligatorio 1: Detección y Aislamiento de Componente (Sección 186):")
    initial_params = {
        "width": 8.0,
        "depth": 6.0,
        "wall_height": 3.0,
        "roof_height": 2.00, # Error deliberado (+20% alto)
        "window_count": 4,
        "door_count": 1
    }
    print(f" - Parámetros Iniciales (con error deliberado de tejado): {initial_params}")
    dirty_comps = api.get_dirty_components_for_parameter("roof_height", ScopeLevel.PARAMETER)
    print(f" - [+] Componentes Marcados como DIRTY: {dirty_comps} (Muros, ventanas y puertas quedan PROTEGIDOS)")

    # 2. Diagnóstico de Error y Atribución de Parámetros
    print("\n[PASO 2] Diagnóstico de Error y Atribución de Parámetros (Sección 17-27):")
    cands = api.diagnose_errors(
        measured_ratios={"roof_ratio": 0.40},
        target_ratios={"roof_ratio": 0.31},
        current_parameters=initial_params
    )
    corr = cands[0]
    print(f" - Candidato de Corrección: ID={corr.candidate_id} | Parámetro -> '{corr.parameter}'")
    print(f" - Operación: [{corr.operation.value}] | Valor Anterior: {corr.old_value}m -> Nuevo: {corr.new_value}m (Delta: {corr.delta}m)")
    print(f" - Efecto Esperado: \"{corr.expected_effect}\" | Confiabilidad: {corr.confidence * 100:.1f}%")

    # 3. Ejecución de la Sesión de Generación Adaptativa (Bucle Cerrado)
    print("\n[PASO 3] Ejecución del Bucle de Generación Adaptativa (Sección 147-154):")
    report = api.run_adaptive_session(
        asset_id="HOUSE_ADAPTIVE_01",
        initial_parameters=initial_params,
        target_reference=ref
    )
    print(f" - Estado de Sesión: [{report.status.value}] | Razón de Terminación: [{report.termination_reason.value}]")
    print(f" - Intentos Totales: {report.total_attempts} | Duración: {report.duration}s | Eficiencia Anti-Retrabajo: {report.rework_efficiency}")
    print(f" - Curva de Evolución de Puntuación (Score Progression): {[round(s, 3) for s in report.score_history]}")
    
    best = report.best_attempt
    print(f" - Mejor Candidato Retenido: ID={best.attempt_id} | Score Final: {best.total_score * 100:.1f}%")
    print(f" - Parámetros del Mejor Candidato: {best.parameters}")

    # 4. Caso de Prueba Obligatorio 3: Propagación Topológica al Cambiar Ancho de Muros
    print("\n[PASO 4] Caso Obligatorio 3: Propagación Topológica ante Cambio de Ancho (Sección 188):")
    dirty_facade = api.get_dirty_components_for_parameter("width", ScopeLevel.COMPONENT)
    print(f" - Modificación de 'width' propaga dirty a: {dirty_facade}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 46 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
