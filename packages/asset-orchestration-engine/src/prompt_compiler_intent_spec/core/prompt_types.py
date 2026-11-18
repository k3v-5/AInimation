from enum import Enum

class IntentType(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    DUPLICATE = "DUPLICATE"
    CONVERT = "CONVERT"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    VALIDATE = "VALIDATE"
    OPTIMIZE = "OPTIMIZE"

class AssetClassType(str, Enum):
    PROP = "PROP"
    CHARACTER = "CHARACTER"
    VEHICLE = "VEHICLE"
    BUILDING = "BUILDING"
    ENVIRONMENT = "ENVIRONMENT"
    WEAPON = "WEAPON"
    TOOL = "TOOL"
    FURNITURE = "FURNITURE"
    VFX = "VFX"
    ARCHITECTURAL = "ARCHITECTURAL"
    OTHER = "OTHER"

class ProvenanceType(str, Enum):
    USER_EXPLICIT = "USER_EXPLICIT"
    AI_INFERRED = "AI_INFERRED"
    PROJECT_RULE = "PROJECT_RULE"
    DEFAULT = "DEFAULT"
    DERIVED = "DERIVED"
    IMPORTED = "IMPORTED"

class RequirementHardness(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"
    PREFERENCE = "PREFERENCE"

class ConflictSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CompilationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    CONFLICT = "CONFLICT"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    INVALID_INTENT = "INVALID_INTENT"
