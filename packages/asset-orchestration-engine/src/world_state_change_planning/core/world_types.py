from enum import Enum

class WorldAssetStatus(str, Enum):
    REQUESTED = "REQUESTED"
    PLANNED = "PLANNED"
    BUILDING = "BUILDING"
    VALIDATING = "VALIDATING"
    VALID = "VALID"
    INVALID = "INVALID"
    DIRTY = "DIRTY"
    OUTDATED = "OUTDATED"
    FAILED = "FAILED"
    DELETED = "DELETED"

class WorldChangeType(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    MOVE = "MOVE"
    DUPLICATE = "DUPLICATE"
    REPLACE = "REPLACE"
    REGENERATE = "REGENERATE"
    RENAME = "RENAME"
    RECONFIGURE = "RECONFIGURE"

class WorldChangeScope(str, Enum):
    PROPERTY = "PROPERTY"
    COMPONENT = "COMPONENT"
    ASSET = "ASSET"
    LEVEL = "LEVEL"
    PROJECT = "PROJECT"

class WorldConstraintType(str, Enum):
    LOCK = "LOCK"
    LIMIT = "LIMIT"
    REQUIRE = "REQUIRE"
    FORBID = "FORBID"
    PREFER = "PREFER"
    DEPENDENCY = "DEPENDENCY"

class ReconciliationState(str, Enum):
    SYSTEM_NEWER = "SYSTEM_NEWER"
    BLENDER_NEWER = "BLENDER_NEWER"
    IDENTICAL = "IDENTICAL"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"

class ContextLevel(str, Enum):
    MINIMAL = "MINIMAL"
    STANDARD = "STANDARD"
    DETAILED = "DETAILED"
    DEBUG = "DEBUG"

class TransactionStatus(str, Enum):
    BEGIN = "BEGIN"
    PLAN = "PLAN"
    VALIDATE = "VALIDATE"
    EXECUTING = "EXECUTING"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"
