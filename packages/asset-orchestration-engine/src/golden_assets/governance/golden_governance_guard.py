from typing import Optional
from ...governance import AgentContractsToolGovernanceAPI, Permission
from ..core.golden_exceptions import GoldenPermissionDeniedError

class GoldenGovernanceGuard:
    """Enforces F72 governance and agent contract verification on Golden Asset operations."""
    def __init__(self, gov_api: Optional[AgentContractsToolGovernanceAPI] = None):
        self.gov = gov_api or AgentContractsToolGovernanceAPI()

    def validate_operation(self, agent_id: str, operation: str):
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            raise GoldenPermissionDeniedError(f"Agent '{agent_id}' has no registered contract for operation '{operation}'.")
