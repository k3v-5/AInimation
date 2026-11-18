from typing import Dict, Any, List, Optional
from ..core.loop_types import LoopState, DecisionOutcome, StopReason
from ..core.loop_schema import (
    IterativeGenerationRequest, IterationContext, IterationTargets,
    IterationRecord, IterationLoopConfiguration, IterativeGenerationResult,
    LoopValidationResult
)
from ..engine.iterative_generation_loop_engine import IterativeGenerationLoopEngine

class IterativeGenerationLoopAPI:
    """
    Iterative Generation Loop API (AOE v65)
    
    Regla Fundamental:
    COORDINA EL CICLO CERRADO DE GENERACIÓN, EVALUACIÓN VISUAL (F61), QA GEOMÉTRICO (F62),
    CRÍTICA INTELIGENTE (F63) Y CORRECCIÓN AUTÓNOMA (F64), CONSERVANDO EL MEJOR ESTADO CONOCIDO,
    DETECCIÓN DE CONVERGENCIA, ESTANCAMIENTO, OSCILACIONES Y GARANTÍA ESTRUCTURAL DE TERMINACIÓN.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = IterativeGenerationLoopEngine(engine_version=engine_version)

    def execute_iterative_loop(
        self,
        request: IterativeGenerationRequest,
        initial_geometry: Any,
        initial_surface: Any,
        initial_presentation: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> IterativeGenerationResult:
        return self._engine.run_loop(request, initial_geometry, initial_surface, initial_presentation, context)

    def validate_loop_result(self, result: IterativeGenerationResult) -> LoopValidationResult:
        return self._engine.validate_result(result)

    def resume_loop(self, loop_id: str) -> Optional[Dict[str, Any]]:
        return self._engine.resume_loop(loop_id)
