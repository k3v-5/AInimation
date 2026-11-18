from typing import Dict, Any, List, Optional
from ..core.orchestrator_types import AgentType
from ..core.orchestrator_schema import AgentDefinition

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, AgentDefinition] = {}
        self._init_default_agents()

    def _init_default_agents(self):
        self.register_agent(AgentDefinition(
            agent_id="planner_agent",
            agent_type=AgentType.PLANNER,
            capabilities=["intent_parsing", "task_graph_generation"],
            allowed_tools=["intent.compile", "task.create"]
        ))
        self.register_agent(AgentDefinition(
            agent_id="blender_operator",
            agent_type=AgentType.BLENDER_OPERATOR,
            capabilities=["mesh_creation", "mesh_edit", "material_assignment"],
            allowed_tools=["blender.create_mesh", "blender.set_transform", "blender.assign_material"]
        ))
        self.register_agent(AgentDefinition(
            agent_id="gameplay_qa_agent",
            agent_type=AgentType.GAMEPLAY_QA,
            capabilities=["navigation_validation", "door_clearance", "traversal_check"],
            allowed_tools=["qa.validate_door", "qa.validate_stair", "qa.run_proxy_agent"]
        ))
        self.register_agent(AgentDefinition(
            agent_id="correction_agent",
            agent_type=AgentType.CORRECTION,
            capabilities=["root_cause_analysis", "surgical_patch_generation"],
            allowed_tools=["correction.generate_plan"]
        ))

    def register_agent(self, agent: AgentDefinition):
        self.agents[agent.agent_id] = agent

    def find_agent_for_capability(self, capability: str) -> Optional[AgentDefinition]:
        for agent in self.agents.values():
            if capability in agent.capabilities and not agent.is_busy:
                return agent
        return None

    def validate_tool_permission(self, agent_id: str, tool_name: str) -> bool:
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        return tool_name in agent.allowed_tools
