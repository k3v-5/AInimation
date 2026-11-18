from typing import Optional
from ...governance import AgentContractsToolGovernanceAPI
from ..core.failure_types import FailureType

class GovernanceBridge:
    """Enforces F72 Agent Contracts and ToolGuard authorization on diagnostic and corrective actions."""
    def __init__(self, gov_api: Optional[AgentContractsToolGovernanceAPI] = None):
        self.gov = gov_api or AgentContractsToolGovernanceAPI()

    def check_correction_permission(self, agent_id: str, capability: str) -> bool:
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            return False
        
        # Check direct or semantic capability match
        req = capability.lower().replace("cap_", "")
        for cap in contract.capabilities:
            cap_l = cap.lower()
            if req in cap_l or cap_l in req or "correction" in cap_l or "fix" in cap_l:
                return True
        return False
