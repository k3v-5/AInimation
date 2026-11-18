from typing import Dict, Any
from .base_operation import IGeometryOperation
from ..core.geom_schema import GenerationContext, GeometryValidationResult, CompensationResult

class ApplyBevelOp(IGeometryOperation):
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        w = float(self.parameters.get("width", 0.005))
        if w < 0:
            return GeometryValidationResult(is_valid=False, errors=["INVALID_BEVEL_WIDTH: Width cannot be negative."])
        return GeometryValidationResult(is_valid=True)

    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.modifiers.append({"type": "BEVEL", "parameters": self.parameters})
            # Aumento topológico realista por bevel
            obj.topology.vertex_count += 16
            obj.topology.triangle_count += 32
        return state

    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.modifiers = [m for m in obj.modifiers if m["type"] != "BEVEL"]
            obj.topology.vertex_count = max(8, obj.topology.vertex_count - 16)
            obj.topology.triangle_count = max(12, obj.topology.triangle_count - 32)
        return CompensationResult(success=True, compensated_operations=[self.operation_id])

class ApplyMirrorOp(IGeometryOperation):
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        axis = self.parameters.get("axis", "X").upper()
        if axis not in {"X", "Y", "Z"}:
            return GeometryValidationResult(is_valid=False, errors=[f"INVALID_MIRROR_AXIS: Unknown axis '{axis}'."])
        return GeometryValidationResult(is_valid=True)

    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.modifiers.append({"type": "MIRROR", "parameters": self.parameters})
            # Duplica vértices y triángulos por simetría
            obj.topology.vertex_count *= 2
            obj.topology.triangle_count *= 2
        return state

    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.modifiers = [m for m in obj.modifiers if m["type"] != "MIRROR"]
            obj.topology.vertex_count = max(8, obj.topology.vertex_count // 2)
            obj.topology.triangle_count = max(12, obj.topology.triangle_count // 2)
        return CompensationResult(success=True, compensated_operations=[self.operation_id])

class ApplyArrayOp(IGeometryOperation):
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        count = int(self.parameters.get("count", 2))
        if count < 1:
            return GeometryValidationResult(is_valid=False, errors=["INVALID_ARRAY_COUNT: Count must be at least 1."])
        return GeometryValidationResult(is_valid=True)

    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        obj = state["objects"].get(self.target_component)
        if obj:
            count = int(self.parameters.get("count", 2))
            obj.modifiers.append({"type": "ARRAY", "parameters": self.parameters})
            obj.topology.vertex_count *= count
            obj.topology.triangle_count *= count
        return state

    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.modifiers = [m for m in obj.modifiers if m["type"] != "ARRAY"]
        return CompensationResult(success=True, compensated_operations=[self.operation_id])

class ApplyBooleanOp(IGeometryOperation):
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        op = self.parameters.get("operation", "DIFFERENCE").upper()
        if op not in {"UNION", "DIFFERENCE", "INTERSECT"}:
            return GeometryValidationResult(is_valid=False, errors=[f"INVALID_BOOLEAN_OP: '{op}' is not supported."])
        return GeometryValidationResult(is_valid=True)

    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.modifiers.append({"type": "BOOLEAN", "parameters": self.parameters})
        return state

    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        obj = state["objects"].get(self.target_component)
        if obj:
            obj.modifiers = [m for m in obj.modifiers if m["type"] != "BOOLEAN"]
        return CompensationResult(success=True, compensated_operations=[self.operation_id])
