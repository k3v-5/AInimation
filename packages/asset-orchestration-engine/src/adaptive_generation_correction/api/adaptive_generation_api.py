from typing import Dict, Any, List, Optional
from ..core.adaptive_types import (
    SessionState, CorrectionOp, ScopeLevel, TerminationReason,
    AdaptiveRiskLevel, ErrorCategory
)
from ..core.adaptive_schema import (
    GenerationAttempt, ErrorDiagnosis, CorrectionCandidate,
    CorrectionTransactionRecord, SessionReport
)
from ..engine.adaptive_generation_engine import AdaptiveGenerationEngine
from ..diagnosis.error_attributor import ErrorAttributor
from ..regeneration.partial_regenerator import PartialRegenerator
from ..transactions.correction_transaction import CorrectionTransaction

from src.visual_reference_matching import ReferenceImageSpec

class AdaptiveGenerationAPI:
    """
    Adaptive Generation & Correction Engine API (AOE v46)
    
    Regla Fundamental:
    EL SISTEMA NUNCA REGENERA UN MODELO ENTERO POR ENSAYO Y ERROR.
    MIDE DIFERENCIAS, ATRIBUYE EL ERROR A PARÁMETROS CONCRETOS, APLICA CAMBIOS MÍNIMOS
    CON REGENERACIÓN QUIRÚRGICA, CONSERVA SIEMPRE LA MEJOR VERSIÓN Y DESHACE REGRESIONES.
    """
    def __init__(self, max_iterations: int = 5, target_score: float = 0.90):
        self.engine = AdaptiveGenerationEngine(max_iterations=max_iterations, target_score=target_score)

    def run_adaptive_session(
        self,
        asset_id: str,
        initial_parameters: Dict[str, Any],
        target_reference: ReferenceImageSpec,
        simulate_collision_failure: bool = False
    ) -> SessionReport:
        return self.engine.start_adaptive_session(
            asset_id=asset_id,
            initial_parameters=initial_parameters,
            target_reference=target_reference,
            simulate_collision_failure=simulate_collision_failure
        )

    def diagnose_errors(
        self,
        measured_ratios: Dict[str, float],
        target_ratios: Dict[str, float],
        current_parameters: Dict[str, Any]
    ) -> List[CorrectionCandidate]:
        return ErrorAttributor.diagnose_and_attribute(measured_ratios, target_ratios, current_parameters)

    def get_dirty_components_for_parameter(self, parameter: str, scope: ScopeLevel = ScopeLevel.PARAMETER) -> List[str]:
        return PartialRegenerator.determine_dirty_components(parameter, scope)
