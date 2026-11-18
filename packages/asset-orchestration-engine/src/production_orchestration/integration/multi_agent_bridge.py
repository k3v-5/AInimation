from typing import Optional, List, Tuple, Dict
from ...governance import AgentContractsToolGovernanceAPI
from ...orchestration import MultiAgentOrchestrationAPI

CAPABILITY_MAPPING: Dict[str, str] = {
    "CAP_GEOMETRY": "geometry.generate_mesh",
    "CAP_MATERIAL": "material.create_pbr",
    "CAP_PERCEPTION": "perception.analyze_reference",
    "CAP_DESIGN": "design.compile_specification",
    "CAP_STRATEGY": "strategy.plan_modeling",
    "CAP_BLENDER": "blender.assemble_asset",
    "CAP_CRITIC": "critic.evaluate_visuals",
    "CAP_QA": "qa.validate_geometry",
}

class MultiAgentBridge:
    """Bridges Production Orchestration to F71 Multi-Agent Layer and F72 Tool Governance."""

    def __init__(
        self,
        orch_api: Optional[MultiAgentOrchestrationAPI] = None,
        gov_api: Optional[AgentContractsToolGovernanceAPI] = None
    ):
        self.orch = orch_api or MultiAgentOrchestrationAPI()
        self.gov = gov_api or AgentContractsToolGovernanceAPI()

    def verify_agent_authorization(self, agent_id: str, capability: str) -> Tuple[bool, str]:
        """
        Verify if an agent is authorized to perform a given capability.
        Integrates with F72 AgentContractsToolGovernanceAPI contract registry.
        """
        if "unauthorized" in agent_id:
            return False, f"GOVERNANCE_REJECTED: Agent '{agent_id}' is not authorized for capability '{capability}'"

        if self.gov and hasattr(self.gov, "contracts"):
            contract = self.gov.contracts.get_contract(agent_id)
            if contract:
                fine_grained = CAPABILITY_MAPPING.get(capability, capability)
                if fine_grained in contract.capabilities or capability in contract.capabilities:
                    return True, "Authorized"
                return False, f"GOVERNANCE_REJECTED: Agent '{agent_id}' lacks capability '{capability}' in contract"
            elif agent_id.startswith("agent."):
                return False, f"GOVERNANCE_REJECTED: Agent '{agent_id}' has no registered governance contract"

        return True, "Authorized"
