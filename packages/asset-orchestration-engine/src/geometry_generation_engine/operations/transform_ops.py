from typing import Dict, Any
from .base_operation import IGeometryOperation
from ..core.geom_schema import GenerationContext, GeometryValidationResult, CompensationResult

class TransformOp(IGeometryOperation):
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        return GeometryValidationResult(is_valid=True)

    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        obj = state["objects"].get(self.target_component)
        if obj:
            loc = self.parameters.get("location", (0,0,0))
            rot = self.parameters.get("rotation", (0,0,0))
            scale = self.parameters.get("scale", (1,1,1))
            obj.transform = {"location": loc, "rotation": rot, "scale": scale}
        return state

    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.transform = {"location": (0,0,0), "rotation": (0,0,0), "scale": (1,1,1)}
        return CompensationResult(success=True, compensated_operations=[self.operation_id])

class SetPivotOp(IGeometryOperation):
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        return GeometryValidationResult(is_valid=True)

    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        strategy = self.parameters.get("pivot_strategy", "BASE_CENTER_GROUNDED")
        state["pivot"] = {"strategy": strategy, "origin": (0.0, 0.0, 0.0)}
        return state

    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        state["pivot"] = {"strategy": "CENTER", "origin": (0.0, 0.0, 0.0)}
        return CompensationResult(success=True, compensated_operations=[self.operation_id])
