import time
from typing import Dict, List, Optional
from ..core.runtime_types import AgentState
from ..core.runtime_schema import AgentProfile

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, AgentProfile] = {}

    def register_agent(self, agent_id: str, capabilities: List[str], permissions: Optional[List[str]] = None) -> AgentProfile:
        profile = AgentProfile(
            agent_id=agent_id,
            capabilities=capabilities,
            permissions=permissions or ["READ", "PLAN", "EXECUTE"],
            state=AgentState.IDLE,
            last_heartbeat=time.time()
        )
        self.agents[agent_id] = profile
        return profile

    def heartbeat(self, agent_id: str):
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = time.time()
            self.agents[agent_id].state = AgentState.IDLE

    def check_agent_health(self, agent_id: str, timeout_seconds: float = 10.0) -> AgentState:
        if agent_id not in self.agents:
            return AgentState.OFFLINE
        ag = self.agents[agent_id]
        if time.time() - ag.last_heartbeat > timeout_seconds:
            ag.state = AgentState.OFFLINE
        return ag.state

    def verify_permission(self, agent_id: str, required_permission: str):
        if agent_id not in self.agents:
            raise KeyError(f"Agent '{agent_id}' is not registered.")
        ag = self.agents[agent_id]
        if required_permission not in ag.permissions and "ADMIN" not in ag.permissions:
            raise PermissionError(f"PERMISSION_DENIED: Agent '{agent_id}' does not have permission '{required_permission}'.")

    def verify_capabilities(self, agent_id: str, required_capabilities: List[str]):
        if agent_id not in self.agents:
            raise KeyError(f"Agent '{agent_id}' is not registered.")
        ag = self.agents[agent_id]
        for cap in required_capabilities:
            if cap not in ag.capabilities:
                raise ValueError(f"PLAN_INVALID: Agent '{agent_id}' is missing required capability '{cap}'.")
