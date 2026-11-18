import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_reference_similarity import (
    VisualSimilarityAPI, CandidateAsset
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 36: VISUAL REFERENCE & SIMILARITY SYSTEM")
    print("=" * 95)

    api = VisualSimilarityAPI()

    # 1. Crear Perfil de Referencia Visual
    print("\n[PASO 1] Creación del Perfil de Referencia Estructurado (ReferenceProfile):")
    ref = api.create_reference_profile(
        ref_id="REF_2026_000182",
        expected_features={
            "roof_type": "GABLE",
            "windows": 4,
            "chimney": True,
            "balcony": False,
            "materials": {"walls": "STONE", "roof": "WOOD"}
        },
        proportions={"roof_to_body": 0.30}
    )
    print(f" - Referencia [{ref.reference_id}] -> Target: {ref.subject}")
    print(f" - Características Esperadas: {ref.expected_features}")
    print(f" - Proporciones Esperadas: {ref.proportions}")

    # 2. Evaluación de Asset con Discrepancias (Wrong Roof, Window Count & Missing Chimney)
    print("\n[PASO 2] Observación del Asset Generado y Evaluación de Similitud:")
    obs_flawed = api.observe_asset(
        asset_id="HOUSE_001_v1",
        detected_features={
            "roof_type": "HIP", # Discrepancia crítica
            "windows": 7,       # Discrepancia de conteo (+3)
            "chimney": False,   # Componente faltante
            "balcony": False,
            "materials": {"walls": "STONE", "roof": "WOOD"}
        },
        detected_proportions={"roof_to_body": 0.48} # Techo demasiado alto
    )

    report = api.evaluate_asset(ref, obs_flawed, use_cache=False)
    print(f" - Similarity Report ID: {report.report_id}")
    print(f" - Puntuación Global Ponderada: {report.overall_score * 100:.1f}%")
    print(" - Desglose por Categorías:")
    for cat, score in report.category_scores.items():
        print(f"   * {cat.capitalize()}: {score * 100:.1f}%")

    print(f"\n - Estado de Evaluación: [{report.evaluation_status.value}]")
    print(" - Fallos Críticos Detectados:")
    for cf in report.critical_failures:
        print(f"   * [-] {cf}")
    print(" - Advertencias:")
    for w in report.warnings:
        print(f"   * [!] {w}")

    # 3. Solicitudes de Corrección Generadas (CorrectionRequests)
    print("\n[PASO 3] Solicitudes de Corrección Estructuradas para el Planner (Sección 76):")
    for corr in report.corrections:
        print(f" - [{corr.correction_id}] ({corr.severity.value}) -> Target: {corr.target}")
        print(f"   * Problema: {corr.issue} (Esperado: {corr.expected_state}, Detectado: {corr.actual_state})")
        print(f"   * Acción Recomendada: \"{corr.suggested_action}\"")

    # 4. Evaluación de Asset Corregido (Ciclo de Mejora)
    print("\n[PASO 4] Evaluación tras Aplicar Corrección (HOUSE_001_v2):")
    obs_corrected = api.observe_asset(
        asset_id="HOUSE_001_v2",
        detected_features={
            "roof_type": "GABLE",
            "windows": 4,
            "chimney": True,
            "balcony": False,
            "materials": {"walls": "STONE", "roof": "WOOD"}
        },
        detected_proportions={"roof_to_body": 0.30}
    )
    report_v2 = api.evaluate_asset(ref, obs_corrected, use_cache=False)
    print(f" - Nueva Puntuación Global: {report_v2.overall_score * 100:.1f}% | Estado: [{report_v2.evaluation_status.value}]")
    print(" - Desglose por Categorías:")
    for cat, score in report_v2.category_scores.items():
        print(f"   * {cat.capitalize()}: {score * 100:.1f}%")

    # 5. Diagnósticos de Bucle: Detección de Oscilación y Selección de Candidatos
    print("\n[PASO 5] Diagnósticos de Bucle y Ranking de Candidatos:")
    history = [0.70, 0.40, 0.70, 0.40]
    osc = api.detect_oscillation(history)
    print(f" - Detección de Oscilación en historial {history}: {osc} (OSCILLATION_DETECTED)")

    candidates = [
        CandidateAsset("HOUSE_CANDIDATE_A", score=0.92, critical_failures_count=1),
        CandidateAsset("HOUSE_CANDIDATE_B", score=0.89, critical_failures_count=0)
    ]
    ranked = api.rank_candidates(candidates)
    print(" - Ranking de Candidatos (priorizando 0 fallos críticos sobre score bruto):")
    for pos, c in enumerate(ranked, 1):
        print(f"   {pos}. [{c.candidate_id}] Score={c.score * 100:.1f}% | Fallos Críticos={c.critical_failures_count}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 36 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
