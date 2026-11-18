class GoldenAssetException(Exception):
    """Base exception for Golden Asset operations."""
    pass

class GoldenIntegrityError(GoldenAssetException):
    """Raised when cryptographic verification or manifest check fails."""
    pass

class GoldenImmutableError(GoldenAssetException):
    """Raised when attempting to modify an immutable published Golden Asset."""
    pass

class GoldenDuplicateError(GoldenAssetException):
    """Raised when attempting to register a duplicate Golden Asset identifier or duplicate physical hash."""
    pass

class GoldenPromotionError(GoldenAssetException):
    """Raised when an asset fails promotion requirements or thresholds."""
    pass

class GoldenPermissionDeniedError(GoldenAssetException):
    """Raised when an agent lacks authorization for a governed Golden Asset operation."""
    pass
