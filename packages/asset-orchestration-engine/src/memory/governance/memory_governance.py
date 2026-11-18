from typing import Optional
from ..core.exceptions import MemoryPermissionDeniedError
from ..core.memory_types import MemoryRecord, MemoryScope
from ...governance import AgentContractsToolGovernanceAPI, Permission

class MemoryGovernanceGuard:
    """
    Enforces F72 Agent Contracts and Permissions on all memory mutations.
    """
    def __init__(self, governance_api: Optional[AgentContractsToolGovernanceAPI] = None):
        self.gov = governance_api or AgentContractsToolGovernanceAPI()

    def validate_write_access(self, agent_id: str, scope: MemoryScope):
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            raise MemoryPermissionDeniedError(f"Agent {agent_id} has no registered contract for memory write.")
        
        # Read-only agents cannot write memory
        if agent_id in ("agent.qa.validator",) and scope in (MemoryScope.GLOBAL, MemoryScope.PROJECT):
            raise MemoryPermissionDeniedError(f"Agent {agent_id} cannot write project-level memory.")

    def validate_invalidation_access(self, agent_id: str):
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            raise MemoryPermissionDeniedError(f"Agent {agent_id} not authorized to invalidate memory.")
        if agent_id in ("agent.perception", "agent.qa.validator"):
            raise MemoryPermissionDeniedError(f"Agent {agent_id} lacks MEMORY_INVALIDATE authority.")
