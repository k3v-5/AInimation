from typing import Optional
from ...governance import AgentContractsToolGovernanceAPI, Permission
from ..nodes.node_types import NodeType

class GraphPermissionDeniedError(Exception):
    """Raised when an agent attempts unauthorized operations on the knowledge graph."""
    pass

class GraphGovernanceGuard:
    """
    Enforces F72 Agent Contracts and permissions for knowledge graph mutations.
    """
    def __init__(self, gov_api: Optional[AgentContractsToolGovernanceAPI] = None):
        self.gov = gov_api or AgentContractsToolGovernanceAPI()

    def validate_node_creation(self, agent_id: str, node_type: NodeType):
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            raise GraphPermissionDeniedError(f"Agent {agent_id} has no registered contract for graph operation.")

        # Visual Critic cannot create geometry/structural nodes
        if agent_id in ("agent.visual.critic", "agent.qa.validator"):
            if node_type in (NodeType.ASSET_COMPONENT, NodeType.BLENDER_OBJECT, NodeType.MATERIAL):
                raise GraphPermissionDeniedError(f"Agent {agent_id} lacks permission to create structural {node_type.value} nodes.")

    def validate_node_deletion(self, agent_id: str):
        contract = self.gov.contracts.get_contract(agent_id)
        if not contract:
            raise GraphPermissionDeniedError(f"Agent {agent_id} not authorized to delete graph nodes.")
        if Permission.ASSET_DELETE not in contract.permissions:
            raise GraphPermissionDeniedError(f"Agent {agent_id} lacks ASSET_DELETE permission required to delete graph nodes.")
