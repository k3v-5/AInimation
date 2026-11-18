from typing import Dict, Any, List, Optional
from ..core.critic_types import (
    EvaluationMode, VisualDiagnosisType, CriticDecisionType,
    ReferenceRole, EvaluationStage, ColorSpaceType
)
from ..core.critic_schema import (
    ReferenceImageSpec, SilhouetteMetrics, ProportionMetrics,
    MaterialMetrics, VisualDiagnosis, ParameterCorrection,
    ScoringWeights, VisualScoreReport
)
from ..engine.visual_reference_matcher import VisualReferenceMatcher

class VisualReferenceMatcherAPI:
    """
    Visual Reference Matching & Geometric Critic API (AOE v41)
    
    Regla Fundamental:
    EL CRITIC NO EMITE OPINIONES VAGAS. CALCULA MÉTRICAS MATEMÁTICAS (IoU, Error de Aspect Ratio,
    Delta E Lab), IDENTIFICA LA CAUSA RAÍZ (QUÉ, DÓNDE, CUÁNTO, POR QUÉ) Y FORMULA DELTAS DE
    PARÁMETROS EXACTOS PARA QUE EL MOTOR PARAMÉTRICO REGENERE SOLO LO AFECTADO.
    """
    def __init__(self):
        self.matcher = VisualReferenceMatcher()

    def create_reference_spec(
        self,
        image_id: str,
        expected_aspect_ratio: float = 1.52,
        expected_roof_ratio: float = 0.31,
        expected_components: Optional[Dict[str, Any]] = None,
        expected_colors: Optional[Dict[str, List[float]]] = None,
        role: ReferenceRole = ReferenceRole.SILHOUETTE
    ) -> ReferenceImageSpec:
        return ReferenceImageSpec(
            image_id=image_id,
            role=role,
            expected_aspect_ratio=expected_aspect_ratio,
            expected_roof_ratio=expected_roof_ratio,
            expected_components=expected_components or {},
            expected_colors=expected_colors or {}
        )

    def evaluate_asset(
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
        return self.matcher.evaluate_model(
            asset_id=asset_id,
            ref=ref,
            generated_parameters=generated_parameters,
            generated_aspect_ratio=generated_aspect_ratio,
            generated_roof_ratio=generated_roof_ratio,
            user_window_count=user_window_count,
            has_chimney=has_chimney,
            mode=mode,
            weights=weights
        )

    def detect_oscillation(self, history: List[float]) -> bool:
        return self.matcher.detect_oscillation(history)
