from enum import Enum

class ActionType(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    MOVE = "MOVE"
    ROTATE = "ROTATE"
    SCALE = "SCALE"
    STYLE = "STYLE"
    REBUILD = "REBUILD"
    VALIDATE = "VALIDATE"

class RequirementPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    OPTIONAL = "OPTIONAL"

class RequirementStatus(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED = "RESOLVED"
    CONFLICTING = "CONFLICTING"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID = "INVALID"
    OVERRIDDEN = "OVERRIDDEN"

class AmbiguitySeverity(str, Enum):
    BLOCKING = "BLOCKING"
    WARNING = "WARNING"
    INFO = "INFO"

class SpecStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"
