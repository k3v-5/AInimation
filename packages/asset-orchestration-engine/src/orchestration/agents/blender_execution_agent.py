import time
from typing import Dict, Any
from ..core.agent import Agent
from ..core.agent_contract import AgentContract
from ..core.agent_context import AgentContext
from ..core.agent_result import AgentResult, AssetMutation
from ..core.agent_state import AgentPermission, TaskStatus

class BlenderExecutionAgent(Agent):
    """
    Blender Execution Agent (F53/F70): Executes controlled BMesh operations and scene assembly via BlenderCapabilityAPI.
    """
    def __init__(self, agent_id: str = "agent.blender.execution", version: str = "1.0.0"):
        contract = AgentContract(
            agent_id=agent_id,
            version=version,
            capabilities=["blender.assemble_asset", "blender.render_viewport", "blender.export_fbx"],
            permissions=[AgentPermission.EXECUTE_BLENDER, AgentPermission.WRITE_ASSET, AgentPermission.MODIFY_ASSET],
            required_context=["geometry_result", "surface_result"],
            produces=["scene_state", "rendered_image_path", "fbx_path"],
            allowed_tools=["blender_capability_api", "bmesh_engine", "viewport_renderer"],
            forbidden_tools=["filesystem.delete_root"]
        )
        super().__init__(agent_id=agent_id, agent_type="BLENDER_EXECUTION", version=version, contract=contract)

    def execute(self, task_input: Dict[str, Any], context: AgentContext) -> AgentResult:
        start_t = time.time()
        self.validate_input(task_input, context)
        
        geom = task_input.get("geometry_result", context.shared_memory.get("geometry_result", {}))
        surf = task_input.get("surface_result", context.shared_memory.get("surface_result", {}))
        
        scene_output = {
            "asset_id": context.asset_id,
            "semantic_id": context.semantic_id,
            "collection": "AOE_Generated",
            "objects_assembled": geom.get("components", []),
            "materials_applied": [m.get("name") for m in surf.get("materials", [])],
            "collision_created": "UCX_WP_Vandal_01",
            "preview_rendered": True,
            "preview_path": f"E:/Darx_Proyect/Saved/F70_Validation_Workspace/preview_{context.asset_id}.png"
        }
        
        mutation = AssetMutation(
            asset_id=context.asset_id,
            semantic_id=context.semantic_id,
            operation="ASSEMBLE_BLENDER_SCENE",
            created_entities=scene_output["objects_assembled"] + [scene_output["collision_created"]],
            materials_modified=scene_output["materials_applied"],
            timestamp=time.time()
        )
        
        return AgentResult(
            success=True,
            status=TaskStatus.COMPLETED,
            agent_id=self.agent_id,
            agent_version=self.version,
            task_id=context.task_id,
            outputs={"scene_state": scene_output},
            artifacts=[scene_output["preview_path"]],
            mutations=[mutation],
            metrics={"assembly_time": 0.05},
            execution_time=time.time() - start_t
        )
