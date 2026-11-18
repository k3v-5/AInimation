class MemoryError(Exception):
    """Base exception for Context & Memory Management system."""
    pass

class MemoryNotFoundError(MemoryError):
    """Raised when a requested memory record is not found."""
    pass

class MemoryPermissionDeniedError(MemoryError):
    """Raised when an agent attempts unauthorized memory operations."""
    pass

class MemoryConflictError(MemoryError):
    """Raised when unresolved contradictions exist between high-priority memories."""
    pass

class ContextBudgetExceededError(MemoryError):
    """Raised when memory assembly strictly exceeds maximum configured tokens/size."""
    pass
