from typing import Dict, List, Optional
from .agent import Agent
from .exceptions import AgentNotFoundError

class AgentRegistry:
    """
    Registry for all available specialized agents in the orchestration layer.
    """
    def __init__(self):
        self._agents: Dict[str, Agent] = {}

    def register(self, agent: Agent):
        if agent.agent_id in self._agents:
            raise ValueError(f"Agent with ID {agent.agent_id} is already registered.")
        if not agent.contract:
            raise ValueError(f"Agent {agent.agent_id} does not possess a valid contract.")
        self._agents[agent.agent_id] = agent

    def unregister(self, agent_id: str):
        if agent_id in self._agents:
            del self._agents[agent_id]

    def get(self, agent_id: str) -> Agent:
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"Agent {agent_id} not found in registry.")
        return self._agents[agent_id]

    def list_agents(self) -> List[Agent]:
        return list(self._agents.values())

    def find_by_capability(self, capability: str) -> List[Agent]:
        matched = []
        for agent in self._agents.values():
            if capability in agent.contract.capabilities or "*" in agent.contract.capabilities:
                matched.append(agent)
        return matched

    def find_by_type(self, agent_type: str) -> List[Agent]:
        return [a for a in self._agents.values() if a.agent_type == agent_type]

    def validate_agent(self, agent_id: str) -> bool:
        agent = self.get(agent_id)
        return bool(agent.agent_id and agent.contract and agent.version)
