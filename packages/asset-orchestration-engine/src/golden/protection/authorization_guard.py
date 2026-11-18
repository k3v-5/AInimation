from typing import Optional
from ...governance import AgentContractsToolGovernanceAPI
from ..core.golden_types import GoldenAuthorizationError

class AuthorizationGuard:
    """Enforces F72 agent contract permissions for all mutating Golden Asset operations."""
    def __init__(self, gov_api: Optional[AgentContractsToolGovernanceAPI] = None):
        self.gov = gov_api or AgentContractsToolGovernanceAPI()

    def check_permission(self, agent_id: str, operation: str):
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            raise GoldenAuthorizationError(f"Agent '{agent_id}' has no registered contract to execute '{operation}'.")
