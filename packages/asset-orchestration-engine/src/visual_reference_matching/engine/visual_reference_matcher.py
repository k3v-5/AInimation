import time
from typing import Dict, Any, List, Optional
from ..core.critic_types import (
    EvaluationMode, CriticDecisionType, ReferenceRole
)
from ..core.critic_schema import (
    ReferenceImageSpec, VisualDiagnosis, ParameterCorrection,
    VisualScoreReport, ScoringWeights
)
from ..analyzers.silhouette_analyzer import SilhouetteAnalyzer, ProportionAnalyzer, MaterialAnalyzer
from ..diagnostic.diagnostic_engine import DiagnosticEngine, ParameterCorrectionEngine

class VisualReferenceMatcher:
    def __init__(self):
        self.history: List[float] = []

    def evaluate_model(
        self,
        asset_id: str,
        ref: ReferenceImageSpec,
        generated_parameters: Dict[str, Any],
        generated_aspect_ratio: float,
        generated_roof_ratio: float,
        user_window_count: int = 4,
        has_chimney: bool = False,
        mode: EvaluationMode = EvaluationMode.STANDARD,
        weights: Optional[ScoringWeights] = None
    ) -> VisualScoreReport:
        w = weights or ScoringWeights()

        # 1. Análisis de Silueta
        sil_metrics = SilhouetteAnalyzer.analyze(ref, generated_aspect_ratio)

        # 2. Análisis de Proporciones y Conteo de Componentes
        gen_win_count = generated_parameters.get("window_count", 4)
        prop_metrics = ProportionAnalyzer.analyze(ref, generated_roof_ratio, user_window_count, gen_win_count)

        # 3. Análisis de Materiales (si modo DEEP)
        mat_score = 1.0
        if mode == EvaluationMode.DEEP and "walls" in ref.expected_colors:
            gen_lab = [52.0, 1.0, 1.0] # Generado
            mat_metrics = MaterialAnalyzer.analyze_lab_color(ref.expected_colors["walls"], gen_lab)
            mat_score = mat_metrics.score

        # 4. Puntuaciones por Subcategoría
        sub_scores = {
            "silhouette": sil_metrics.score,
            "proportions": prop_metrics.score,
            "components": 1.0 if gen_win_count == user_window_count else 0.8,
            "spatial": 0.95,
            "material": mat_score,
            "style": 0.90
        }

        # Puntuación Global Ponderada
        overall = (
            sub_scores["silhouette"] * w.silhouette +
            sub_scores["proportions"] * w.proportions +
            sub_scores["components"] * w.components +
            sub_scores["spatial"] * w.spatial +
            sub_scores["material"] * w.material +
            sub_scores["style"] * w.style
        )
        overall = round(overall, 3)

        # 5. Diagnóstico de Causa Raíz
        diagnoses = DiagnosticEngine.diagnose(sil_metrics, prop_metrics, has_chimney, ref.expected_components.get("chimney", False))

        # 6. Mapeo a Correcciones Paramétricas
        corrections = ParameterCorrectionEngine.calculate_corrections(
            diagnoses, generated_parameters, ref.expected_aspect_ratio, ref.expected_roof_ratio
        )

        # 7. Decisión del Critic
        if overall >= 0.88 and not any(d.severity == "HIGH" for d in diagnoses):
            decision = CriticDecisionType.ACCEPT
        elif any(c.replan_required for c in corrections):
            decision = CriticDecisionType.REPLAN
        elif corrections:
            decision = CriticDecisionType.CORRECT
        else:
            decision = CriticDecisionType.ACCEPT_WITH_WARNINGS

        # 8. Explicabilidad Formal (WHAT, WHERE, HOW MUCH, WHY)
        explainability = {
            "what": f"Asset exhibits {len(diagnoses)} visual deviations against reference [{ref.image_id}].",
            "where": ", ".join([d.location for d in diagnoses]) if diagnoses else "None",
            "how_much": f"Aspect ratio error: {sil_metrics.aspect_ratio_error:+.2f}, Roof ratio error: {prop_metrics.roof_to_body_error:+.2f}",
            "why": f"Reference expects aspect ratio {ref.expected_aspect_ratio} and roof ratio {ref.expected_roof_ratio}."
        }

        self.history.append(overall)

        return VisualScoreReport(
            report_id=f"VSR_{int(time.time()*1000)}",
            asset_id=asset_id,
            overall_score=overall,
            sub_scores=sub_scores,
            diagnoses=diagnoses,
            suggested_corrections=corrections,
            decision=decision,
            explainability=explainability
        )

    def detect_oscillation(self, history: List[float]) -> bool:
        if len(history) < 4:
            return False
        deltas = [history[i+1] - history[i] for i in range(len(history)-1)]
        signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in deltas]
        for i in range(len(signs) - 2):
            if signs[i] != 0 and signs[i] == -signs[i+1] and signs[i+1] == -signs[i+2]:
                return True
        return False
