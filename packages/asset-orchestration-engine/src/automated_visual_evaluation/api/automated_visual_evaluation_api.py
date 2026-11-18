from typing import Dict, Any, List, Optional
from ..core.evaluation_types import (
    EvaluationCategory, DefectType, DefectSeverity,
    DefectCauseCategory, AcceptanceStatus, EvaluationLevel,
    RegressionStatus
)
from ..core.evaluation_schema import (
    VisualDefect, CorrectionHint, CategoryEvaluation,
    RegionEvaluation, RequirementEvaluationResult, EvaluationDelta,
    EvaluationConfiguration, VisualEvaluationResult, EvaluationValidationResult
)
from ..engine.automated_visual_evaluation_engine import AutomatedVisualEvaluationEngine

class AutomatedVisualEvaluationAPI:
    """
    Automated Visual Evaluation Engine API (AOE v61)
    
    Regla Fundamental:
    COMPARA LA ESPECIFICACIÓN VISUAL / REFERENCIA CONTRA EL RENDER DEL ASSET GENERADO,
    LOCALIZANDO DEFECTOS, ESTIMANDO CAUSAS MULTI-HIPÓTESIS Y EMITIENDO HINTS DE CORRECCIÓN
    ACCIONABLES PARA F63 (CRITIC) Y F64 (CORRECTOR).
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = AutomatedVisualEvaluationEngine(engine_version=engine_version)

    def evaluate_visuals(
        self,
        reference: Optional[Any] = None,
        generated: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
        configuration: Optional[EvaluationConfiguration] = None
    ) -> VisualEvaluationResult:
        return self._engine.evaluate(reference, generated, context, configuration)

    def evaluate_category(
        self,
        category: EvaluationCategory,
        reference: Any,
        generated: Any,
        context: Dict[str, Any]
    ) -> CategoryEvaluation:
        return self._engine.evaluate_category(category, reference, generated, context)

    def detect_defects(self, evaluation_context: Dict[str, Any]) -> List[VisualDefect]:
        return self._engine.detect_defects(evaluation_context)

    def compare_iterations(
        self,
        previous: VisualEvaluationResult,
        current: VisualEvaluationResult
    ) -> EvaluationDelta:
        return self._engine.compare_iterations(previous, current)

    def validate_evaluation(self, result: VisualEvaluationResult) -> EvaluationValidationResult:
        return self._engine.validate(result)

    def compute_evaluation_hash(self, result: VisualEvaluationResult) -> str:
        return self._engine.compute_hash(result)
