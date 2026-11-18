from abc import ABC, abstractmethod
from typing import Dict, Any
from ..core.geom_schema import GenerationContext, GeometryValidationResult, CompensationResult

class IGeometryOperation(ABC):
    def __init__(self, operation_id: str, target_component: str, parameters: Dict[str, Any]):
        self.operation_id = operation_id
        self.target_component = target_component
        self.parameters = parameters

    @abstractmethod
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        pass

    @abstractmethod
    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        pass
