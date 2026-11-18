import time
from typing import Dict, Any
from ..core.agent import Agent
from ..core.agent_contract import AgentContract
from ..core.agent_context import AgentContext
from ..core.agent_result import AgentResult, AssetMutation
from ..core.agent_state import AgentPermission, TaskStatus

class MaterialAgent(Agent):
    """
    Material Agent (F59): Generates PBR shader networks, roughness maps, and UV parameters.
    """
    def __init__(self, agent_id: str = "agent.material", version: str = "1.0.0"):
        contract = AgentContract(
            agent_id=agent_id,
            version=version,
            capabilities=["material.create_pbr", "material.assign_shaders"],
            permissions=[AgentPermission.READ_ASSET, AgentPermission.WRITE_ASSET, AgentPermission.MODIFY_ASSET],
            required_context=["visual_specification"],
            produces=["surface_result", "materials_manifest"],
            allowed_tools=["shader_builder", "material_library"],
            forbidden_tools=["filesystem.delete"]
        )
        super().__init__(agent_id=agent_id, agent_type="MATERIAL", version=version, contract=contract)

    def execute(self, task_input: Dict[str, Any], context: AgentContext) -> AgentResult:
        start_t = time.time()
        self.validate_input(task_input, context)
        
        surf_result = {
            "asset_id": context.asset_id,
            "materials": [
                {"name": "M_DarX_GunMetal", "metallic": 0.95, "roughness": 0.28},
                {"name": "M_DarX_PolymerGrip", "metallic": 0.05, "roughness": 0.80},
                {"name": "M_DarX_AnodizedTrim", "metallic": 0.88, "roughness": 0.18},
                {"name": "M_DarX_PlasmaGlow", "emissive_color": [0.0, 0.85, 1.0], "emission_strength": 8.0}
            ],
            "uv_channels": 2,
            "lightmap_density_ok": True
        }
        
        mutation = AssetMutation(
            asset_id=context.asset_id,
            semantic_id=context.semantic_id,
            operation="ASSIGN_PBR_MATERIALS",
            materials_modified=[m["name"] for m in surf_result["materials"]],
            timestamp=time.time()
        )
        
        return AgentResult(
            success=True,
            status=TaskStatus.COMPLETED,
            agent_id=self.agent_id,
            agent_version=self.version,
            task_id=context.task_id,
            outputs={"surface_result": surf_result},
            mutations=[mutation],
            metrics={"material_count": 4.0, "pbr_validity": 1.0},
            execution_time=time.time() - start_t
        )
