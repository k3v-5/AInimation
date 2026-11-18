from .agent_contract_v2 import AgentContractV2
from .permission_manager import Permission, PermissionManager
from .exceptions import InvalidContractError

class ContractValidator:
    """Validates contract structure, consistency, permissions and limits."""

    @classmethod
    def validate(cls, contract: AgentContractV2) -> bool:
        if not contract.agent_id or not contract.agent_type:
            raise InvalidContractError("Contract must define non-empty agent_id and agent_type.")
        
        # Check tool contradictions
        overlap_tools = set(contract.allowed_tools).intersection(set(contract.forbidden_tools))
        if overlap_tools:
            raise InvalidContractError(f"Contradictory tools found in both allowed and forbidden: {overlap_tools}")
        
        # Check resource contradictions
        overlap_res = set(contract.allowed_resources).intersection(set(contract.forbidden_resources))
        if overlap_res and "*" not in overlap_res:
            raise InvalidContractError(f"Contradictory resources found in both allowed and forbidden: {overlap_res}")

        # Check operation contradictions
        overlap_ops = set(contract.allowed_operations).intersection(set(contract.forbidden_operations))
        if overlap_ops and "*" not in overlap_ops:
            raise InvalidContractError(f"Contradictory operations in both allowed and forbidden: {overlap_ops}")

        # Limits validation
        if contract.max_execution_time <= 0:
            raise InvalidContractError("max_execution_time must be positive.")
        if contract.max_retries < 0 or contract.max_retries > 10:
            raise InvalidContractError("max_retries must be between 0 and 10.")
        if contract.max_concurrency <= 0:
            raise InvalidContractError("max_concurrency must be positive.")

        return True
