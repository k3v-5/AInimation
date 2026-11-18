from typing import Dict, Any, List, Optional
from ..core.vas_types import (
    RequirementClass, ValidationMethod, RequirementOrigin,
    ContradictionSeverity, AmbiguitySeverity, InformationState, EngineTarget
)
from ..core.vas_schema import (
    VisualCompilationInput, VisualAssetSpecification, TraceabilityRecord,
    InvariantSpec, VariableSpec, ToleranceSpec, AcceptanceCriterion,
    AmbiguityReport, ContradictionReport, UnrealRequirementsSpec,
    ProductionBudgetSpec, ValidationResult
)
from ..engine.visual_specification_compiler import VisualSpecificationCompiler

class VisualSpecificationAPI:
    """
    Visual Specification Compiler API (AOE v56)
    
    Regla Fundamental:
    TRANSFORMA LA INTENCIÓN DEL USUARIO, OBSERVACIONES VISUALES Y RESTRICCIONES DE PROYECTO
    EN UNA VISUAL ASSET SPECIFICATION (VAS) ESTRUCTURADA, DETERMINISTA Y TRAZABLE.
    """
    def __init__(self, compiler_version: str = "1.0.0"):
        self._compiler = VisualSpecificationCompiler(compiler_version=compiler_version)

    def compile_specification(self, comp_input: VisualCompilationInput) -> VisualAssetSpecification:
        return self._compiler.compile(comp_input)

    def validate_specification(self, specification: VisualAssetSpecification) -> ValidationResult:
        return self._compiler.validate(specification)

    def detect_ambiguities(self, specification: VisualAssetSpecification) -> List[AmbiguityReport]:
        return self._compiler.detect_ambiguities(specification)

    def detect_contradictions(self, specification: VisualAssetSpecification) -> List[ContradictionReport]:
        return self._compiler.detect_contradictions(specification)

    def compute_hash(self, specification: VisualAssetSpecification) -> str:
        return self._compiler.compute_hash(specification)
