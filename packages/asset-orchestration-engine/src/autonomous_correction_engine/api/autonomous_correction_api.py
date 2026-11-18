from typing import Dict, Any, List, Optional
from ..core.correction_types import (
    CorrectionStatus, ActionAuthorization, RollbackStatus,
    CorrectionStrategyType, RegressionSeverity, OperationType
)
from ..core.correction_schema import (
    ParameterChange, AssetSnapshot, QualityDeltaReport,
    CorrectionConfiguration, CorrectionResult, CorrectionValidationResult
)
from ..engine.autonomous_correction_engine import AutonomousCorrectionEngine

class AutonomousCorrectionAPI:
    """
    Autonomous Correction API (AOE v64)
    
    Regla Fundamental:
    EJECUTA MODIFICACIONES CONTROLADAS Y DETERMINISTAS SOBRE EL ASSET BASADAS EN EL DIAGNÓSTICO
    DE F63, BAJO UN MODELO ESTRICTO DE TRANSACCIÓN Y SNAPSHOTS CON ROLLBACK AUTOMÁTICO
    ANTE CUALQUIER REGRESIÓN CRÍTICA O FALLA TOPOLÓGICA.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = AutonomousCorrectionEngine(engine_version=engine_version)

    def apply_corrections(
        self,
        critic_result: Any,
        generated_geometry: Any,
        context: Optional[Dict[str, Any]] = None,
        configuration: Optional[CorrectionConfiguration] = None
    ) -> CorrectionResult:
        return self._engine.apply_correction_plan(critic_result, generated_geometry, context, configuration)

    def validate_correction_result(self, result: CorrectionResult) -> CorrectionValidationResult:
        return self._engine.validate_result(result)

    def compute_correction_hash(self, result: CorrectionResult) -> str:
        return self._engine.compute_hash(result)
