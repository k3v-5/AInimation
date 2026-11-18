from typing import Dict, Any, List, Optional
from ..core.qa_types import (
    GeometricDefectCategory, DefectSeverity, ValidationStatus,
    ValidationProfileType, CorrectionSafetyLevel, MeshWatertightMode,
    NgonPolicy
)
from ..core.qa_schema import (
    GeometricDefect, GeometricCorrectionHint, MeshInventory,
    TopologyStatistics, UnrealReadinessReport, GeometryValidationConfiguration,
    GeometricValidationResult, QAValidationResult
)
from ..engine.geometric_validation_engine import GeometricValidationEngine

class GeometricValidationAPI:
    """
    Geometric Validation & Topology QA API (AOE v62)
    
    Regla Fundamental:
    VALIDA ESTRUCTURALMENTE LA MALLA (MANIFOLD, NORMALES, TOPOLOGÍA, ESCALA, PRESUPUESTO, UCX)
    EN MODO READ-ONLY SIN MODIFICAR LA GEOMETRÍA, DESACOPLANDO LA VERDAD ESTRUCTURAL
    DE LA EVALUACIÓN VISUAL DE F61 Y PREPARANDO LA EVIDENCIA PARA F63 Y F64.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = GeometricValidationEngine(engine_version=engine_version)

    def validate_geometry(
        self,
        geometry: Any,
        context: Optional[Dict[str, Any]] = None,
        configuration: Optional[GeometryValidationConfiguration] = None
    ) -> GeometricValidationResult:
        return self._engine.validate(geometry, context, configuration)

    def validate_component(
        self,
        component_id: str,
        geometry: Any,
        context: Optional[Dict] = None
    ) -> GeometricValidationResult:
        return self._engine.validate_component(component_id, geometry, context)

    def validate_qa_result(self, result: GeometricValidationResult) -> QAValidationResult:
        return self._engine.validate_result(result)

    def compute_qa_hash(self, result: GeometricValidationResult) -> str:
        return self._engine.compute_hash(result)
