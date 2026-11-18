from typing import Dict, List, Optional
from .agent_contract_v2 import AgentContractV2
from .contract_validator import ContractValidator
from .permission_manager import Permission
from .exceptions import InvalidContractError

class ContractRegistry:
    """Central repository for all Agent Contracts V2."""
    def __init__(self):
        self._contracts: Dict[str, AgentContractV2] = {}

    def register_contract(self, contract: AgentContractV2):
        if contract.agent_id in self._contracts:
            raise InvalidContractError(f"Contract for agent {contract.agent_id} already registered.")
        ContractValidator.validate(contract)
        self._contracts[contract.agent_id] = contract

    def get_contract(self, agent_id: str) -> Optional[AgentContractV2]:
        return self._contracts.get(agent_id)

    def remove_contract(self, agent_id: str):
        if agent_id in self._contracts:
            del self._contracts[agent_id]

    def list_contracts(self) -> List[AgentContractV2]:
        return list(self._contracts.values())

    def find_by_capability(self, capability: str) -> List[AgentContractV2]:
        matched = []
        for c in self._contracts.values():
            if capability in c.capabilities or "*" in c.capabilities:
                matched.append(c)
        return matched

    def find_by_permission(self, permission: Permission) -> List[AgentContractV2]:
        return [c for c in self._contracts.values() if permission in c.permissions]
