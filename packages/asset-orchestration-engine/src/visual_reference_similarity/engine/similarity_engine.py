import time
from typing import List, Dict, Any, Optional
from ..core.similarity_types import EvaluationStatus, DifferenceSeverity, CorrectionPriority
from ..core.similarity_schema import (
    ReferenceProfile, AssetObservation, SimilarityWeights, SimilarityReport,
    DifferenceRecord, CorrectionRequest
)
from .difference_detector import DifferenceDetector

class SimilarityEngine:
    @staticmethod
    def evaluate(
        ref: ReferenceProfile,
        obs: AssetObservation,
        weights: Optional[SimilarityWeights] = None
    ) -> SimilarityReport:
        w = weights or SimilarityWeights()
        diffs = DifferenceDetector.detect_differences(ref, obs)

        # 1. Calcular Puntuaciones por Categoría
        # Silueta
        sil_diff = abs(ref.silhouette_aspect_ratio - obs.silhouette_aspect_ratio)
        sil_score = max(0.0, 1.0 - sil_diff * 0.5)

        # Proporciones
        prop_score = 1.0
        for d in diffs:
            if d.metric == "roof_to_body_ratio":
                prop_score -= 0.35
        prop_score = max(0.0, prop_score)

        # Componentes
        comp_score = 1.0
        for d in diffs:
            if d.diff_type.value in ["MISSING", "EXTRA", "WRONG_COUNT"]:
                comp_score -= 0.20
        comp_score = max(0.0, comp_score)

        # Materiales
        mat_score = 1.0
        for d in diffs:
            if d.diff_type.value == "WRONG_MATERIAL":
                mat_score -= 0.30
        mat_score = max(0.0, mat_score)

        style_score = 0.90
        spatial_score = 0.95

        cat_scores = {
            "silhouette": round(sil_score, 3),
            "proportions": round(prop_score, 3),
            "components": round(comp_score, 3),
            "spatial": round(spatial_score, 3),
            "materials": round(mat_score, 3),
            "style": round(style_score, 3)
        }

        # Puntuación Global Ponderada
        overall = (
            sil_score * w.silhouette +
            prop_score * w.proportions +
            comp_score * w.components +
            spatial_score * w.spatial +
            mat_score * w.materials +
            style_score * w.style
        )
        overall = round(overall, 3)

        # 2. Puerta de Fallos Críticos (Critical Failure Gate)
        crit_failures: List[str] = []
        warnings: List[str] = []
        for d in diffs:
            if d.severity == DifferenceSeverity.CRITICAL:
                crit_failures.append(f"CRITICAL: {d.target} has {d.diff_type.value} on {d.metric} (Expected: {d.expected}, Detected: {d.actual})")
            elif d.severity == DifferenceSeverity.HIGH:
                crit_failures.append(f"HIGH_MISMATCH: {d.target} - {d.diff_type.value}")
            else:
                warnings.append(f"WARNING: {d.target} - {d.diff_type.value} ({d.metric})")

        # Estado de Evaluación
        if crit_failures:
            status = EvaluationStatus.FAIL
        elif overall >= 0.90:
            status = EvaluationStatus.PASS
        elif overall >= 0.75:
            status = EvaluationStatus.WARNING
        else:
            status = EvaluationStatus.FAIL

        # 3. Generar Solicitudes de Corrección
        corrections = CorrectionGenerator.generate_corrections(diffs)

        return SimilarityReport(
            report_id=f"SIM_REP_{int(time.time()*1000)}",
            asset_id=obs.asset_id,
            overall_score=overall,
            category_scores=cat_scores,
            critical_failures=crit_failures,
            warnings=warnings,
            differences=diffs,
            corrections=corrections,
            evaluation_status=status,
            recommendations=[c.suggested_action for c in corrections]
        )

class CorrectionGenerator:
    @staticmethod
    def generate_corrections(diffs: List[DifferenceRecord]) -> List[CorrectionRequest]:
        corrections: List[CorrectionRequest] = []
        for i, d in enumerate(diffs):
            corr_id = f"CORR_{int(time.time()*1000)}_{i}"
            if d.metric == "roof_shape":
                action = f"Change roof geometry type from '{d.actual}' to '{d.expected}'"
                prio = CorrectionPriority.CRITICAL
            elif d.metric == "window_count":
                delta = d.expected - d.actual
                action = f"Adjust window count by {delta:+d} to match target ({d.expected})"
                prio = CorrectionPriority.MEDIUM
            elif d.metric == "chimney_presence":
                action = "Add missing chimney component to roof structure"
                prio = CorrectionPriority.HIGH
            elif d.metric == "balcony_presence":
                action = "Remove unrequested balcony component"
                prio = CorrectionPriority.HIGH
            elif d.metric == "roof_to_body_ratio":
                action = f"Reduce roof height ratio to target ({d.expected})"
                prio = CorrectionPriority.HIGH
            elif d.metric == "material_category":
                action = f"Assign material '{d.expected}' to {d.target}"
                prio = CorrectionPriority.MEDIUM
            else:
                action = f"Correct discrepancy on {d.target}"
                prio = CorrectionPriority.LOW

            corrections.append(CorrectionRequest(
                correction_id=corr_id,
                target=d.target,
                issue=d.diff_type.value,
                severity=prio,
                expected_state=d.expected,
                actual_state=d.actual,
                suggested_action=action
            ))
        return corrections
