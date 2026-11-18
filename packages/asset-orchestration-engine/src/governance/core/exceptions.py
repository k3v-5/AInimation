class GovernanceError(Exception):
    """Base exception for governance and authorization layer."""
    pass

class AuthorizationDeniedError(GovernanceError):
    """Raised when an operation is denied by the Authorization Engine."""
    pass

class AgentIdentityViolationError(GovernanceError):
    """Raised when an agent attempts impersonation or invalid identity declaration."""
    pass

class ContextIntegrityError(GovernanceError):
    """Raised when agent context has been tampered with or corrupted."""
    pass

class ContractIntegrityError(GovernanceError):
    """Raised when agent contract is tampered with during an active task."""
    pass

class MutationViolationError(GovernanceError):
    """Raised when a mutation exceeds authorized boundaries or fails validation."""
    pass

class DeleteProtectionViolationError(GovernanceError):
    """Raised when a destructive delete operation is attempted without explicit delete permission."""
    pass

class EmergencyStopActiveError(GovernanceError):
    """Raised when an operation is attempted while an administrative emergency stop is active."""
    pass

class InvalidContractError(GovernanceError):
    """Raised when a contract contains contradictions, invalid limits or unknown capabilities."""
    pass

class ResourceOwnershipConflictError(GovernanceError):
    """Raised when an agent attempts to write to a resource owned by another task/agent."""
    pass
