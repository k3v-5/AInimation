from typing import List, Dict, Any, Optional
from ..core.critic_types import VisualDiagnosisType
from ..core.critic_schema import (
    SilhouetteMetrics, ProportionMetrics, VisualDiagnosis, ParameterCorrection
)

class DiagnosticEngine:
    @staticmethod
    def diagnose(
        sil_metrics: SilhouetteMetrics,
        prop_metrics: ProportionMetrics,
        has_chimney: bool,
        expected_chimney: bool = True
    ) -> List[VisualDiagnosis]:
        diagnoses: List[VisualDiagnosis] = []

        # 1. Diagnóstico de Ancho / Silueta
        if sil_metrics.aspect_ratio_error > 0.10:
            diagnoses.append(VisualDiagnosis(
                diag_type=VisualDiagnosisType.TOO_WIDE,
                location="FACADE_WIDTH",
                severity="HIGH",
                deviation_amount=sil_metrics.aspect_ratio_error,
                description=f"Generated asset is too wide (aspect ratio error: +{sil_metrics.aspect_ratio_error})"
            ))
        elif sil_metrics.aspect_ratio_error < -0.10:
            diagnoses.append(VisualDiagnosis(
                diag_type=VisualDiagnosisType.TOO_NARROW,
                location="FACADE_WIDTH",
                severity="HIGH",
                deviation_amount=sil_metrics.aspect_ratio_error,
                description=f"Generated asset is too narrow (aspect ratio error: {sil_metrics.aspect_ratio_error})"
            ))

        # 2. Diagnóstico de Altura de Techo
        if prop_metrics.roof_to_body_error > 0.05:
            diagnoses.append(VisualDiagnosis(
                diag_type=VisualDiagnosisType.ROOF_TOO_HIGH,
                location="ROOF",
                severity="HIGH",
                deviation_amount=prop_metrics.roof_to_body_error,
                description=f"Roof height ratio exceeds reference by +{prop_metrics.roof_to_body_error}"
            ))
        elif prop_metrics.roof_to_body_error < -0.05:
            diagnoses.append(VisualDiagnosis(
                diag_type=VisualDiagnosisType.ROOF_TOO_FLAT,
                location="ROOF",
                severity="MEDIUM",
                deviation_amount=prop_metrics.roof_to_body_error,
                description=f"Roof is flatter than reference by {prop_metrics.roof_to_body_error}"
            ))

        # 3. Componente Faltante
        if expected_chimney and not has_chimney:
            diagnoses.append(VisualDiagnosis(
                diag_type=VisualDiagnosisType.COMPONENT_MISSING,
                location="ROOF.CHIMNEY",
                severity="MEDIUM",
                deviation_amount=1.0,
                description="Chimney visible in reference but absent in generated model"
            ))

        return diagnoses

class ParameterCorrectionEngine:
    @staticmethod
    def calculate_corrections(
        diagnoses: List[VisualDiagnosis],
        current_parameters: Dict[str, Any],
        expected_aspect_ratio: float = 1.52,
        expected_roof_ratio: float = 0.31
    ) -> List[ParameterCorrection]:
        corrections: List[ParameterCorrection] = []

        for d in diagnoses:
            if d.diag_type == VisualDiagnosisType.TOO_WIDE:
                curr_w = float(current_parameters.get("width", 9.0))
                gen_ar = expected_aspect_ratio + d.deviation_amount
                # Fórmula matemática de corrección de ancho
                sugg_w = round(curr_w * (expected_aspect_ratio / gen_ar), 2)
                delta = round(sugg_w - curr_w, 2)
                pct = round((delta / curr_w) * 100, 1)
                corrections.append(ParameterCorrection(
                    parameter_name="width",
                    current_value=curr_w,
                    suggested_value=sugg_w,
                    delta=delta,
                    relative_change_pct=pct,
                    affected_components=["foundation", "walls", "roof", "windows"],
                    risk="MEDIUM",
                    replan_required=abs(pct) > 20.0
                ))

            elif d.diag_type == VisualDiagnosisType.ROOF_TOO_HIGH:
                curr_h = float(current_parameters.get("roof_height", 2.0))
                gen_rr = expected_roof_ratio + d.deviation_amount
                # Fórmula matemática de corrección de techo
                sugg_h = round(curr_h * (expected_roof_ratio / gen_rr), 2)
                delta = round(sugg_h - curr_h, 2)
                pct = round((delta / curr_h) * 100, 1)
                corrections.append(ParameterCorrection(
                    parameter_name="roof_height",
                    current_value=curr_h,
                    suggested_value=sugg_h,
                    delta=delta,
                    relative_change_pct=pct,
                    affected_components=["roof"], # Solo afecta al techo
                    risk="LOW",
                    replan_required=abs(pct) > 20.0
                ))

        return corrections
