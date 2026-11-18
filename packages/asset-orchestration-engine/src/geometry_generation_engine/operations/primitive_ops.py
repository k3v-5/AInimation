from typing import Dict, Any, Tuple
from .base_operation import IGeometryOperation
from ..core.geom_schema import (
    GenerationContext, GeometryValidationResult, CompensationResult,
    GeometryObjectSpec, TopologySummary, MeshTopologyType, ExportRole
)

class CreatePrimitiveOp(IGeometryOperation):
    def validate(self, context: GenerationContext) -> GeometryValidationResult:
        prim = self.parameters.get("primitive", "CUBE").upper()
        allowed = {"CUBE", "CYLINDER", "SPHERE", "TORUS", "PLANE", "CONE", "PROFILE", "CUSTOM_MESH"}
        if prim not in allowed:
            return GeometryValidationResult(is_valid=False, errors=[f"INVALID_PRIMITIVE: Unknown primitive type '{prim}'."])
        return GeometryValidationResult(is_valid=True)

    def execute(self, context: GenerationContext, state: Dict[str, Any]) -> Dict[str, Any]:
        prim = self.parameters.get("primitive", "CUBE").upper()
        obj_id = f"OBJ_{self.target_component.upper()}"
        name = f"SM_{getattr(context.strategy_plan, 'semantic_id', 'Prop')}_{self.target_component.capitalize()}"
        
        # Geometría abstracta según primitiva
        if prim == "CYLINDER":
            v_count, f_count, t_count = 64, 34, 64
            dims = {"x": 1.0, "y": 1.0, "z": 1.2}
            bounds = {"min": (-0.5, -0.5, 0.0), "max": (0.5, 0.5, 1.2)}
        elif prim == "TORUS":
            v_count, f_count, t_count = 128, 64, 128
            dims = {"x": 1.05, "y": 1.05, "z": 0.15}
            bounds = {"min": (-0.525, -0.525, 0.0), "max": (0.525, 0.525, 0.15)}
        else: # CUBE / BOX
            v_count, f_count, t_count = 8, 6, 12
            dims = {"x": 1.0, "y": 1.0, "z": 1.0}
            bounds = {"min": (-0.5, -0.5, 0.0), "max": (0.5, 0.5, 1.0)}

        topo = TopologySummary(
            vertex_count=v_count,
            edge_count=v_count + f_count,
            face_count=f_count,
            triangle_count=t_count,
            ngon_count=0,
            non_manifold_count=0,
            degenerate_face_count=0,
            is_manifold=True
        )

        obj_spec = GeometryObjectSpec(
            object_id=obj_id,
            semantic_component_id=self.target_component,
            semantic_id=getattr(context.strategy_plan, "semantic_id", "asset_001.root"),
            name=name,
            geometry_type=MeshTopologyType.TRIANGLE_MESH,
            dimensions=dims,
            bounds=bounds,
            topology=topo,
            material_slots=[f"M_{self.target_component.capitalize()}"],
            export_role=ExportRole.RENDER_MESH
        )

        state["objects"][self.target_component] = obj_spec
        state["created_objects"].append(obj_id)
        return state

    def rollback(self, context: GenerationContext, state: Dict[str, Any]) -> CompensationResult:
        obj_id = f"OBJ_{self.target_component.upper()}"
        if self.target_component in state.get("objects", {}):
            del state["objects"][self.target_component]
        return CompensationResult(success=True, compensated_operations=[self.operation_id], message=f"Removed {obj_id}")
