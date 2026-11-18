class OrchestrationError(Exception):
    """Base exception for orchestration layer."""
    pass

class CyclicDependencyError(OrchestrationError):
    """Raised when a task graph contains cyclic dependencies."""
    pass

class ToolAccessDeniedError(OrchestrationError):
    """Raised when an agent attempts to access an unauthorized tool."""
    pass

class PermissionDeniedError(OrchestrationError):
    """Raised when an agent attempts an action without required permissions."""
    pass

class AgentNotFoundError(OrchestrationError):
    """Raised when a required agent is not found in the registry."""
    pass

class AgentContractViolationError(OrchestrationError):
    """Raised when an agent input/output violates its contract."""
    pass

class TaskExecutionError(OrchestrationError):
    """Raised when a task fails during execution."""
    pass

class ResourceLockConflictError(OrchestrationError):
    """Raised when two concurrent tasks compete for incompatible locks."""
    pass
