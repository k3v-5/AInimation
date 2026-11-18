from typing import Dict, Any, List, Optional
from ..core.geom_types import (
    OperationState, TransactionState, MeshTopologyType,
    ExportRole, ValidationSeverity, GenerationStatus
)
from ..core.geom_schema import (
    GenerationContext, GeneratedGeometryResult, GeometryObjectSpec,
    ComponentGenerationResult, TopologySummary, GeometryValidationResult,
    CompensationResult, CheckpointSpec
)
from ..engine.geometry_generation_engine import GeometryGenerationEngine

class GeometryGenerationAPI:
    """
    Geometry Generation Engine API (AOE v58)
    
    Regla Fundamental:
    TRANSFORMA EL ModelingStrategyPlan (MSP) EN GEOMETRÍA REAL Y DETERMINISTA,
    CON SOPORTE PARA REGENERACIÓN PARCIAL, TOPOLOGY QA Y HASH INMUTABLE.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self._engine = GeometryGenerationEngine(engine_version=engine_version)

    def generate_geometry(
        self,
        strategy: Any,
        context: Optional[GenerationContext] = None
    ) -> GeneratedGeometryResult:
        return self._engine.generate(strategy, context)

    def generate_component(
        self,
        component_id: str,
        strategy: Any,
        context: Optional[GenerationContext] = None
    ) -> ComponentGenerationResult:
        return self._engine.generate_component(component_id, strategy, context)

    def regenerate_geometry(
        self,
        target_components: List[str],
        strategy: Any,
        context: Optional[GenerationContext] = None
    ) -> GeneratedGeometryResult:
        return self._engine.regenerate(target_components, strategy, context)

    def validate_geometry(self, result: GeneratedGeometryResult) -> GeometryValidationResult:
        return self._engine.validate(result)

    def rollback_generation(self, generation_id: str) -> CompensationResult:
        return self._engine.rollback(generation_id)

    def compute_geometry_hash(self, result: GeneratedGeometryResult) -> str:
        return self._engine.compute_hash(result)
