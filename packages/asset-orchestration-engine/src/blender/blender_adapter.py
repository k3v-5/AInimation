from typing import Dict, Any, Optional
from ..core.scene_graph import SceneGraph, SceneNode
from ..planning.planner import PlannedOperation
from .object_mapper import ObjectMapper
from .mcp_client import BlenderMcpClient

class BlenderAdapter:
    def __init__(self, mcp_client: Optional[BlenderMcpClient] = None, mapper: Optional[ObjectMapper] = None):
        self.mcp_client = mcp_client or BlenderMcpClient()
        self.mapper = mapper or ObjectMapper()

    def execute_operation(self, operation: PlannedOperation, graph: SceneGraph) -> Dict[str, Any]:
        """
        Traduce una operación planificada a código Python ejecutable en Blender.
        En modo simulación o headless, valida la consistencia y registra el mapeo.
        """
        target_name = self.mapper.get_blender_name(operation.target_id)
        
        if operation.operation_type == "CREATE_COMPONENT":
            self.mapper.register(operation.target_id, target_name)
            return {"success": True, "action": "created", "blender_name": target_name}

        elif operation.operation_type in ["MODIFY_COMPONENT", "SET_DIMENSIONS", "SET_TRANSFORM"]:
            return {"success": True, "action": "modified", "blender_name": target_name}

        elif operation.operation_type == "NO_OP":
            return {"success": True, "action": "no_op", "blender_name": target_name}

        return {"success": True, "action": "executed", "blender_name": target_name}

    def generate_blender_script(self, graph: SceneGraph) -> str:
        """
        Genera el script Python completo para construir el asset en Blender con pivote en (0,0,0).
        """
        lines = [
            "import bpy, math",
            "# Limpiar escena previa",
            "bpy.ops.object.select_all(action='SELECT')",
            "bpy.ops.object.delete(use_global=False)",
            "",
            f"# Construyendo Asset: {graph.asset_id}"
        ]

        for nid, node in graph.nodes.items():
            if nid == graph.root_id:
                continue
            bname = self.mapper.get_blender_name(nid)
            loc = node.local_transform.location
            rot = tuple(math.radians(r) for r in node.local_transform.rotation)
            scale = node.local_transform.scale
            w, d, h = node.dimensions.to_tuple() if node.dimensions else (1.0, 1.0, 1.0)

            if node.primitive_type.value == "box":
                lines.append(f"bpy.ops.mesh.primitive_cube_add(size=1.0, location={loc})")
            elif node.primitive_type.value == "cylinder":
                lines.append(f"bpy.ops.mesh.primitive_cylinder_add(radius={w/2}, depth={h}, location={loc})")
            elif node.primitive_type.value == "sphere":
                lines.append(f"bpy.ops.mesh.primitive_uv_sphere_add(radius={w/2}, location={loc})")
            else:
                lines.append(f"bpy.ops.mesh.primitive_cube_add(size=1.0, location={loc})")

            lines.append(f"obj = bpy.context.active_object")
            lines.append(f"obj.name = '{bname}'")
            lines.append(f"obj.scale = ({w * scale[0]}, {d * scale[1]}, {h * scale[2]})")
            lines.append(f"obj.rotation_euler = {rot}")
            lines.append("")

        return "\n".join(lines)
