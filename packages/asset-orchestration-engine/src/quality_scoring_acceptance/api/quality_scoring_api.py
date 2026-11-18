from typing import Dict, Any, List, Optional
from ..core.scoring_types import (
    AcceptanceStatus, QualityLevel, MetricCategory,
    ConstraintSeverity, QualityTrend, DirectionType, MetricStatus
)
from ..core.scoring_schema import (
    QualityMetric, QualityConstraint, QualityDefect, QualityProfile,
    AcceptanceExplanation, QualityResult, QualityReport, ScoringValidationResult
)
from ..engine.quality_scoring_service import QualityScoringService

class QualityScoringAPI:
    """
    Quality Scoring & Acceptance API (AOE v66)
    
    Regla Fundamental:
    CALCULA EL SCORE OBJETIVO 0-100 PONDERADO Y DETERMINA INEQUÍVOCAMENTE EL ESTADO DE ACEPTACIÓN
    (ACCEPTED, CONDITIONAL, REJECTED) APLICANDO GATES DUROS DONDE NINGÚN SCORE ELEVADO
    PUEDA OCULTAR UNA RESTRICCIÓN CRÍTICA O TOPOLÓGICA INCUMPLIDA.
    """
    def __init__(self, scoring_version: str = "1.0.0"):
        self._service = QualityScoringService(scoring_version=scoring_version)

    def evaluate_asset_quality(
        self,
        asset_id: str,
        semantic_id: str,
        visual_eval_result: Any,
        geometry_qa_result: Any,
        profile: Optional[QualityProfile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> QualityResult:
        return self._service.evaluate_quality(
            asset_id, semantic_id, visual_eval_result, geometry_qa_result, profile, context
        )

    def generate_acceptance_report(
        self,
        quality_result: QualityResult,
        profile_id: str = "DEFAULT_GAME_PROP"
    ) -> QualityReport:
        return self._service.generate_report(quality_result, profile_id)

    def validate_quality_result(self, result: QualityResult) -> ScoringValidationResult:
        return self._service.validate_result(result)
