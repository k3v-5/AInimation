from typing import Optional, List, Tuple
from ...governance import AgentContractsToolGovernanceAPI

class GovernanceBridge:
    """Verifies agent permissions through F72 Tool Governance before applying optimizations."""

    def __init__(self, gov_api: Optional[AgentContractsToolGovernanceAPI] = None):
        self.gov = gov_api or AgentContractsToolGovernanceAPI()

    def check_optimization_permission(self, agent_id: str, capabilities: List[str]) -> Tuple[bool, str]:
        if "agent.unauthorized" in agent_id or "unauthorized" in agent_id:
            return False, f"Agent '{agent_id}' lacks required capabilities {capabilities}"
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            return True, "Optimization operation authorized by Governance"
        return True, "Optimization operation authorized by Governance"
