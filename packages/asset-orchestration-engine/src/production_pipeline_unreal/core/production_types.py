from enum import Enum

class AssetLifecycle(str, Enum):
    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    VALIDATING = "VALIDATING"
    APPROVED = "APPROVED"
    EXPORTING = "EXPORTING"
    EXPORTED = "EXPORTED"
    STAGING = "STAGING"
    IMPORTED = "IMPORTED"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"
    FAILED = "FAILED"

class PivotType(str, Enum):
    CENTER = "CENTER"
    BASE = "BASE"
    CUSTOM = "CUSTOM"
    SOCKET_DEFINED = "SOCKET_DEFINED"

class CollisionStrategy(str, Enum):
    AUTO_CONVEX = "AUTO_CONVEX"
    CUSTOM = "CUSTOM"
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"

class NanitePolicy(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    FORCED = "FORCED"
    PROHIBITED = "PROHIBITED"

class ChangeClass(str, Enum):
    NON_BREAKING = "NON_BREAKING"
    COMPATIBLE = "COMPATIBLE"
    BREAKING = "BREAKING"

class QualityGateStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"

class SourceOwnership(str, Enum):
    AI = "AI"
    MANUAL = "MANUAL"
    HYBRID = "HYBRID"
