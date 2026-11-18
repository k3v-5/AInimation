from typing import Dict, Any, List, Optional
from ..core.control_types import AgentRole, ToolEffect
from ..core.control_schema import AgentDefinition

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[AgentRole, AgentDefinition] = {}
        self._init_standard_agents()

    def _init_standard_agents(self):
        standard = [
            AgentDefinition(
                agent_id="AGENT_PLANNER",
                role=AgentRole.PLANNER,
                capabilities=["intent_parsing", "dag_planning"],
                allowed_effects=[ToolEffect.READ_ONLY]
            ),
            AgentDefinition(
                agent_id="AGENT_SPECIFICATION",
                role=AgentRole.SPECIFICATION,
                capabilities=["spec_compilation", "constraint_extraction"],
                allowed_effects=[ToolEffect.READ_ONLY]
            ),
            AgentDefinition(
                agent_id="AGENT_DEPENDENCY",
                role=AgentRole.DEPENDENCY,
                capabilities=["world_graph_analysis", "impact_prediction"],
                allowed_effects=[ToolEffect.READ_ONLY]
            ),
            AgentDefinition(
                agent_id="AGENT_BLENDER",
                role=AgentRole.BLENDER,
                capabilities=["mesh_modeling", "material_assignment", "export_fbx"],
                allowed_effects=[ToolEffect.READ_ONLY, ToolEffect.MUTATING],
                concurrency_limit=1 # Serializado por defecto
            ),
            AgentDefinition(
                agent_id="AGENT_VALIDATION",
                role=AgentRole.VALIDATION,
                capabilities=["mesh_inspection", "quality_gate"],
                allowed_effects=[ToolEffect.READ_ONLY]
            ),
            AgentDefinition(
                agent_id="AGENT_CRITIC",
                role=AgentRole.CRITIC,
                capabilities=["visual_evaluation", "defect_attribution"],
                allowed_effects=[ToolEffect.READ_ONLY]
            ),
            AgentDefinition(
                agent_id="AGENT_UNREAL",
                role=AgentRole.UNREAL,
                capabilities=["staging_import", "data_asset_creation", "publication"],
                allowed_effects=[ToolEffect.READ_ONLY, ToolEffect.MUTATING]
            ),
            AgentDefinition(
                agent_id="AGENT_RECOVERY",
                role=AgentRole.RECOVERY,
                capabilities=["rollback", "partial_output_salvage", "retry_orchestration"],
                allowed_effects=[ToolEffect.READ_ONLY, ToolEffect.MUTATING, ToolEffect.DESTRUCTIVE]
            )
        ]
        for ag in standard:
            self._agents[ag.role] = ag

    def get_agent(self, role: AgentRole) -> Optional[AgentDefinition]:
        return self._agents.get(role)

    def list_agents(self) -> List[AgentDefinition]:
        return list(self._agents.values())
