from enum import Enum

class GoldenAssetStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REVOKED = "REVOKED"
    CORRUPTED = "CORRUPTED"

class MutationType(str, Enum):
    NO_CHANGE = "NO_CHANGE"
    GEOMETRY_CHANGED = "GEOMETRY_CHANGED"
    MATERIAL_CHANGED = "MATERIAL_CHANGED"
    SCENE_CHANGED = "SCENE_CHANGED"
    REFERENCE_CHANGED = "REFERENCE_CHANGED"
    UNREAL_READINESS_CHANGED = "UNREAL_READINESS_CHANGED"
    MANIFEST_CHANGED = "MANIFEST_CHANGED"
    MULTIPLE_CHANGES = "MULTIPLE_CHANGES"
    CORRUPTED = "CORRUPTED"

class RegressionLevel(str, Enum):
    IMPROVEMENT = "IMPROVEMENT"
    ACCEPTABLE_VARIATION = "ACCEPTABLE_VARIATION"
    REGRESSION = "REGRESSION"
    CRITICAL_REGRESSION = "CRITICAL_REGRESSION"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"

class GoldenAssetException(Exception):
    """Base exception for Golden Asset operations."""
    pass

class GoldenImmutabilityError(GoldenAssetException):
    """Raised when an ACTIVE Golden Asset is illegally mutated."""
    pass

class GoldenIntegrityError(GoldenAssetException):
    """Raised when cryptographic or manifest hash verification fails."""
    pass

class GoldenDuplicateError(GoldenAssetException):
    """Raised when attempting to register a duplicate golden_id or duplicate version."""
    pass

class GoldenAuthorizationError(GoldenAssetException):
    """Raised when an agent lacks authorization for a governed Golden Asset operation."""
    pass
