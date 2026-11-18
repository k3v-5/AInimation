from enum import Enum

class OperationState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    COMPENSATED = "COMPENSATED"

class TransactionState(str, Enum):
    BEGIN = "BEGIN"
    VALIDATING = "VALIDATING"
    GENERATING = "GENERATING"
    VALIDATING_RESULT = "VALIDATING_RESULT"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"

class MeshTopologyType(str, Enum):
    TRIANGLE_MESH = "TRIANGLE_MESH"
    QUAD_MESH = "QUAD_MESH"
    HYBRID_MESH = "HYBRID_MESH"
    CURVE = "CURVE"
    POINT_CLOUD = "POINT_CLOUD"

class ExportRole(str, Enum):
    RENDER_MESH = "RENDER_MESH"
    COLLISION_MESH = "COLLISION_MESH"
    LOD_MESH = "LOD_MESH"
    HELPER = "HELPER"
    DEBUG = "DEBUG"

class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class GenerationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    SUCCESS_WITH_WARNINGS = "SUCCESS_WITH_WARNINGS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    PARTIAL = "PARTIAL"
