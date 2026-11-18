from enum import Enum

class GoldenStatus(str, Enum):
    DRAFT = "DRAFT"
    CANDIDATE = "CANDIDATE"
    GOLDEN = "GOLDEN"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    REVOKED = "REVOKED"

class ReferenceStatus(str, Enum):
    DRAFT = "DRAFT"
    CANDIDATE = "CANDIDATE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

class PromotionState(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    COMMITTING = "COMMITTING"
    PROMOTED = "PROMOTED"
    FAILED = "FAILED"

class ComparisonOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REGRESSION = "REGRESSION"
    IMPROVEMENT = "IMPROVEMENT"
    INCONCLUSIVE = "INCONCLUSIVE"

class VersionBumpType(str, Enum):
    PATCH = "PATCH"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
